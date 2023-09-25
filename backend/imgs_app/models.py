from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from imgs_app.validators import validate_img_extension, validate_img_size
from auth_app.models import ThumbnailHeight

User = get_user_model()

class UploadedImage(models.Model):
    """Default image model uploaded by the user.
    The image is further processed to make thumbnails accordingly to the plan.
    """
    uploadedImage = models.ImageField(
        upload_to = 'uploaded_imgs/', 
        blank = False, 
        validators = [validate_img_extension, validate_img_size]
        )
    user = models.ForeignKey(User, blank = False, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return f"Image {str(self.pk)} - User {str(self.user.username)}"


class Thumbnail(models.Model):
    """Thumbnail after resize. The uploaded image is qued
    and processed asynchronously using celery/redis,
    followed by storing thumbnail object.
    """
    parentImage = models.ForeignKey(
        UploadedImage,
        on_delete = models.CASCADE,
        blank = False
    )
    thumbnail = models.ImageField(
        upload_to = 'thumbnails/',
        blank = False
    )
    height = models.ForeignKey(ThumbnailHeight, blank = False, on_delete = models.CASCADE) # Once height is removed, object is deleted - height's object not editable
    user = models.ForeignKey(User, blank = False, on_delete = models.CASCADE) # OK, this introduces redundancy, 
                                                                              # however reduces complexity of queries, therefore its justified


class ExpiringLink(models.Model):
    """Expiring link model. 
    Checking if link is valid occurs in view.
    """
    user = models.ForeignKey(User, blank = False, on_delete = models.CASCADE)
    expiryTime = models.PositiveIntegerField(validators=[MinValueValidator(300), MaxValueValidator(30000)], default = 300, blank = False)
    image = models.ForeignKey(UploadedImage, models.CASCADE, blank = True, null = True)
    thumbnail = models.ForeignKey(Thumbnail, models.CASCADE, blank = True, null = True)
    createdAt = models.DateTimeField(auto_now_add = True, editable = False)
    linkUUID = models.CharField(max_length = 100)
