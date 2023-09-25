from rest_framework.serializers import ModelSerializer, ValidationError
from imgs_app.models import UploadedImage, Thumbnail, ExpiringLink

class ThumbnailSerializer(ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ['thumbnail']


class ImageSerializer(ModelSerializer):

    class Meta:
        model = UploadedImage
        fields = ['uploadedImage']

    def create(self, validated_data):
        img = UploadedImage(
            uploadedImage = validated_data['uploadedImage'],
            user = validated_data['user']
        )
        img.save()
        return img


class ExpiringLinkSerializer(ModelSerializer):

    class Meta:
        model = ExpiringLink
        fields = ['id', 'image', 'thumbnail', 'expiryTime']

    def __init__(self, *args, **kwargs):
        request = kwargs['context'].get('request')
        super().__init__(*args, **kwargs)

        # Filter the queryset for the 'user' field to show only the request user
        if request and request.user.is_authenticated:
            # And check if user can view original images
            if request.user.userTier.accessOriginalFile:
                self.fields['image'].queryset = UploadedImage.objects.filter(user=request.user) 
            else:
                self.fields['image'].queryset = None
            # Filter thumbnails by defined heights available for account tier
            account_heights = request.user.userTier.thumbnailHeight.values_list('available_height',flat=True)
            self.fields['thumbnail'].queryset = Thumbnail.objects.filter(user=request.user, height__available_height__in=account_heights)

    def validate(self, data):
        """We already check if user is authenticated in view,
        however we make double check. Moreover this function
        checks if img and thumbnail is null, and checks thumbnail height.
        Here's also additional check if the user associated with the
        image is requesting user, and if creation of expiration link
        for 'original' img is possible based on account tier.
        """
        request = self.context.get('request')
        selected_image = data.get('image')
        selected_thumbnail = data.get('thumbnail')

        if request and not request.user.is_authenticated:
            raise ValidationError("Please login.")

        if selected_image is None and selected_thumbnail is None:
            raise ValidationError("Please make selections.")
        
        if selected_thumbnail and selected_thumbnail.user != request.user:
            raise ValidationError("Please select your thumbnail.")

        if selected_image and selected_image.user != request.user:
            raise ValidationError("Please select your images.")

        if not selected_thumbnail.height.available_height in request.user.userTier.thumbnailHeight.values_list('available_height',flat=True):
            raise ValidationError("Incorrect image.")
            
        if selected_image and not request.user.userTier.accessOriginalFile:
            raise ValidationError("Account tier does not include this feature.")

        return data

    def create(self):
        return ExpiringLink(**self.validated_data)