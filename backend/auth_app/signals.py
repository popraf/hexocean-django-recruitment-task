from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from auth_app.models import ThumbnailHeight
from imgs_app.tasks import heights_update_task

User = get_user_model()

@receiver(post_save, sender=ThumbnailHeight)
def trigger_thumb_height(sender, instance, created, **kwargs):
    """
    As soon as ThumbnailHeight object is saved by Django ORM,
    all images are placed in que (tasks.py) for async height processing.
    """
    if created:
        heights_update_task.delay(instance.id)
