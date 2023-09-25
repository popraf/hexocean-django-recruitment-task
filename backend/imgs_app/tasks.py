import io
import logging
from celery import shared_task
from pathlib import Path
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from auth_app.models import ThumbnailHeight
from imgs_app.models import UploadedImage, Thumbnail
from imgs_app.img_processing import SimpleImageProcessing

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task
def process_uploaded_img_task(object_id):
    """Asynchronous task to create thumbnail objects of single uploaded image
    to all available defined heights.
    This task is fired once image is uploaded, therefore after user account tier
    update the thumbnail is already available.

    Args:
        object_id (int): The uploaded image pk.

    Returns:
        Returns True after task completion.
    """
    try:
        img_uploaded = UploadedImage.objects.get(pk=object_id)

        if not img_uploaded:
            raise Exception("The image to process does not exist.")

        owner = img_uploaded.user
        thumbnailHeights = ThumbnailHeight.objects.all()
        img_uploaded_path = img_uploaded.uploadedImage
        selected_img = SimpleImageProcessing(img_uploaded_path)

        if not len(thumbnailHeights)>0:
            raise Exception("Account tiers and its hieghts are defined incorrectly!")

        image_io = io.BytesIO()

        for thumbnailHeight in thumbnailHeights:
            new_height = thumbnailHeight.available_height

            if Thumbnail.objects.filter(parentImage = img_uploaded, height__available_height=new_height):
                # If object with certain height already exists, iterate to next height
                continue

            # Process image to desired height keeping image's aspect ratio
            output_img = selected_img.new_thumbnail_keep_aspect(new_height)
            output_img.save(image_io, format='JPEG')
            content_img = ContentFile(image_io.getvalue())
            thumb = Thumbnail(
                parentImage = img_uploaded,
                height = thumbnailHeight,
                user = owner
            )
            thumb.thumbnail.save(f'{Path(img_uploaded.uploadedImage.name).stem}_thumbnail_{str(new_height)}.jpg', content_img)
            thumb.save()
        return True

    except Exception as e:
        logger.exception(f"Exception occured during Celery task. Error: {str(e)}")


@shared_task
def heights_update_task(object_id):
    """Asynchronous task to create new height thumbnail objects of all uploaded images.
    This task is fired once ThumbnailHeight model is created.
    available_height of ThumbnailHeight is not editable (in admin panel, in db its still possible), 
    therefore there's no need to check for a field update.

    Args:
        object_id (int): The new height object pk.

    Returns:
        Returns True after task completion.
    """
    try:
        thumbnailHeight = ThumbnailHeight.objects.get(pk=object_id)
        all_uploaded_imgs = UploadedImage.objects.all()
        new_height = thumbnailHeight.available_height
        image_io = io.BytesIO()

        if not all_uploaded_imgs:
            raise Exception("No uploaded images found.")
        
        for uploaded_img in all_uploaded_imgs:
            owner = uploaded_img.user
            img_uploaded_path = uploaded_img.uploadedImage

            if not img_uploaded_path:
                # Double check
                raise Exception("The image to process does not exist.")

            if Thumbnail.objects.filter(parentImage = uploaded_img, height__available_height=new_height):
                # If object with certain height already exists, iterate to next height
                continue

            selected_img = SimpleImageProcessing(img_uploaded_path)

            # Process image to desired height keeping image's aspect ratio
            output_img = selected_img.new_thumbnail_keep_aspect(new_height)
            output_img.save(image_io, format='JPEG')
            content_img = ContentFile(image_io.getvalue())
            thumb = Thumbnail(
                parentImage = uploaded_img,
                height = thumbnailHeight,
                user = owner
            )
            thumb.thumbnail.save(f'{Path(uploaded_img.uploadedImage.name).stem}_thumbnail_{str(new_height)}.jpg', content_img)
            thumb.save()
        return True

    except Exception as e:
        logger.exception(f"Exception occured during Celery task. Error: {str(e)}")


@shared_task
def check_user_thumbs_task(object_id):
    try:
        user = User.objects.get(pk=object_id)
        user_uploaded_imgs = UploadedImage.objects.filter(user = user)
        thumbnailHeights = ThumbnailHeight.objects.all()

        if not user_uploaded_imgs:
            raise Exception("No uploaded images found.")

        if not len(thumbnailHeights)>0:
            raise Exception("Account tiers and its hieghts are defined incorrectly!")

        image_io = io.BytesIO()

        for uploaded_img in user_uploaded_imgs:
            img_uploaded_path = uploaded_img.uploadedImage

            if not img_uploaded_path:
                # Double check
                raise Exception("The image to process does not exist.")

            for thumbnailHeight in thumbnailHeights:
                new_height = thumbnailHeight.available_height

                if Thumbnail.objects.filter(parentImage = uploaded_img, height__available_height=new_height):
                    # If object with certain height already exists, iterate to next height
                    continue

                selected_img = SimpleImageProcessing(img_uploaded_path)

                # Process image to desired height keeping image's aspect ratio
                output_img = selected_img.new_thumbnail_keep_aspect(new_height)
                output_img.save(image_io, format='JPEG')
                content_img = ContentFile(image_io.getvalue())
                thumb = Thumbnail(
                    parentImage = uploaded_img,
                    height = thumbnailHeight,
                    user = user
                )
                thumb.thumbnail.save(f'{Path(uploaded_img.uploadedImage.name).stem}_thumbnail_{str(new_height)}.jpg', content_img)
                thumb.save()
        return True

    except Exception as e:
        logger.exception(f"Exception occured during Celery task. Error: {str(e)}")
