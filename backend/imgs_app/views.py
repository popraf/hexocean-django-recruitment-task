import uuid
import datetime
import logging
from pathlib import Path
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from imgs_app.models import UploadedImage, Thumbnail, ExpiringLink
from imgs_app.serializers import ImageSerializer, ThumbnailSerializer, ExpiringLinkSerializer
from imgs_app.permissions import NewExpiringLinksCreatePermission
from imgs_app.tasks import check_user_thumbs_task

logger = logging.getLogger(__name__)

class UploadImageView(CreateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user = self.request.user)
            return Response(status = 201)
        return Response({"error": str(serializer.errors)}, status = 400)


class ImagesListApiView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ImageSerializer

    def get_queryset(self):
        user = self.request.user
        original_imgs = UploadedImage.objects.filter(user = user)
        return original_imgs

    @method_decorator(cache_page(60*10)) # cache for 10minutes
    @method_decorator(vary_on_headers("Authorization",)) # should take into account when building its cache key
    def list(self, request, *args, **kwargs):
        try:
            user = self.request.user
            userAccessOriginalFile = user.userTier.accessOriginalFile
            if userAccessOriginalFile:
                get_images = self.get_queryset()
                if get_images:
                    serializer_original_imgs = ImageSerializer(get_images, many = True)
                    return Response({'original_imgs': serializer_original_imgs.data}, status = 200)
                else:
                    return Response({"error": "Please upload image."}, status = 204)
            else:
                return Response({"error": "Current account plan does not include this feature."}, status = 403)

        except Exception as e:
            logger.exception(f"An error occurred in ImagesListApiView -> list. {str(e)}")
            return Response({'error': 'An error occurred'}, status=500)


class ThumbnailsListApiView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ThumbnailSerializer

    def get_queryset(self, heights: int):
        user = self.request.user
        original_imgs = UploadedImage.objects.filter(user = user)
        len_original_imgs = len(original_imgs)
        if heights and len_original_imgs>0:
            thumbnails = Thumbnail.objects.filter(user = user, height__available_height = heights)
            return {'thumbnails_arr': thumbnails, 'len_original_imgs': len_original_imgs}

    @method_decorator(cache_page(60*10)) # cache for 10minutes
    @method_decorator(vary_on_headers("Authorization",)) # should take into account when building its cache key
    def list(self, request, *args, **kwargs):
        try:
            user = self.request.user
            userTierHeights = user.userTier.thumbnailHeight.values_list('available_height',flat=True)
            height = self.kwargs["height"]

            if height is None:
                return Response({"error": "Please specify thumbnail size."}, status = 400)

            if len(userTierHeights) == 0:
                logger.exception("Account tiers and its hieghts are defined incorrectly!")
                return Response({"error": "Service temporarily unavailable."}, status = 405)

            if height in userTierHeights:
                get_images = self.get_queryset(height)
                if len(get_images['thumbnails_arr'])>0 and get_images['len_original_imgs']>0:
                    serializer_thumbnails = ThumbnailSerializer(get_images['thumbnails_arr'], many = True)
                    return Response({'thumbnails':serializer_thumbnails.data,}, status = 200)
                elif get_images['len_original_imgs'] == 0:
                    return Response({"error":"Please upload image in order to get thumbnail."}, status = 204)
                else:
                    # Check if user has thumbnails asynchronously just-in-case no objects got created (or removed)
                    check_user_thumbs_task.delay(user.pk)
                    return Response({"error": "Please try again in a moment. Temporarily unavailable."}, status = 405)
            else:
                return Response({"error": "Please query thumbnail height based on account tier."}, status = 403)

        except Exception as e:
            logger.exception(f"An error occurred in ThumbnailsListApiView -> list. {str(e)}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class ExpiringLinkCreateApiView(CreateAPIView):
    permission_classes = [IsAuthenticated, NewExpiringLinksCreatePermission]
    serializer_class = ExpiringLinkSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid():
            link = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response = {
                "link": request.build_absolute_uri(reverse('expiring_link_view', kwargs = {'linkUUID': str(link.linkUUID)})),
                "created_at": link.createdAt,
                "valid_for": f"{link.expiryTime} seconds",
            }
            return Response(response, status = 201, headers=headers)
        else:
            logger.exception("An error occurred in ExpiringLinkCreateApiView -> create.")
            return Response(str(serializer.errors), status = 400)

    def perform_create(self, serializer):
        link = serializer.create()
        link.user = self.request.user
        link.linkUUID = uuid.uuid4().hex
        link.save()
        return link


class ExpiringLinkRetrieveView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ExpiringLink.objects.all()
    serializer_class = ExpiringLinkSerializer
    lookup_field = 'linkUUID'

    def get(self, request, *args, **kwargs):
        instance = self.get_object()

        if (instance.createdAt + datetime.timedelta(seconds = instance.expiryTime)) <= timezone.now():
            instance.delete()
            return Response({"error": "Expiration link is not valid."}, status = 404)

        image_file = instance.image
        thumbnail_file = instance.thumbnail

        serializer_images = ImageSerializer(image_file, many=False)
        serializer_thumbnails = ThumbnailSerializer(thumbnail_file, many = False)

        return Response({
            "image": serializer_images.data,
            "thumbnail": serializer_thumbnails.data
        }, status = 200)

