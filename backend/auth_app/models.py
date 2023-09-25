from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

class ThumbnailHeight(models.Model):
    """Thumbnail height model.
    available_height is not designed to be updated, therefore please do not
    update it in db, nor change the admin panel mixins.
    Currently, available_height is read only in admin panel page.

    available_height: a single height of thumbnail available in user account tier
    """
    available_height = models.PositiveIntegerField(
        validators=[MinValueValidator(25), MaxValueValidator(8640)], 
        blank = False,
        unique = True,
        default = 25,
        ) # Ive set minimal and default value to 25 and max to 8640 (16k image height)

    def __str__(self) -> str:
        return f"Defined thumbnail height PK {str(self.pk)} - {str(self.available_height)}px"


class UserTier(models.Model):
    """User tier model.

    name: Tier name
    thumbnailHeights: height of thumbnail displayed for user
    accessOriginalFile: if user can access originally uploaded image file
    accessGenerateExpiringLinks: if user can generate by himself expiring link to the image
    """
    name = models.CharField(max_length=128, blank=False, unique=True)
    thumbnailHeight = models.ManyToManyField(ThumbnailHeight)
    accessOriginalFile = models.BooleanField(default=False)
    accessGenerateExpiringLinks = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.name)


class CustomUser(AbstractUser):
    """Custom user model, where user is linked to certain tier.
    By default new account uses account tier with PK equal 1
    (set by initial fixtures as Basic).
    """
    userTier = models.ForeignKey(UserTier, on_delete=models.PROTECT, default=1, blank=False)

    def __str__(self) -> str:
        return str(self.username)

