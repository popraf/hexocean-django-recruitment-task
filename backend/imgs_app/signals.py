from django.dispatch import receiver
from django.db.models.signals import post_save
from imgs_app.models import UploadedImage
from imgs_app.tasks import process_uploaded_img_task


@receiver(post_save, sender=UploadedImage)
def trigger_uploaded_img(sender, instance, created, **kwargs):
    """
    As soon as UploadedImage object is saved by Django ORM,
    the image is placed in que (tasks.py) for async height processing.
    """
    if created:
        process_uploaded_img_task.delay(instance.id)
