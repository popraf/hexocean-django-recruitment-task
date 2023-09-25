import logging
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

class SimpleImageProcessing:
    """Image processing class with two methods to resize upload image to thumbnail.

    Args:
        imgpath: UploadedImage.uploadedImage ImageField.
    """
    def __init__(self, imgpath):
        self.imgpath = imgpath
    
    def img_loader(self):
        try:
            _img = PILImage.open(self.imgpath)
            return _img.copy()

        except Exception as e:
            logger.exception(f"An error occurred while using img_loader. {str(e)}")

    def new_thumbnail_reduce_keep_aspect(self, new_width = 1024, new_height = 1024):
        """This method calculates an appropriate thumbnail size to 
        preserve the aspect of the image and does not enlarge the image.
        The resulting size is not bigger than the given args.
        Width and height is set to 1024px by default.

        Args:
            new_width (int): The requested width in pixels.
            new_height (int): The requested height in pixels.

        Returns:
            Returns resized image.
        """
        img = self.img_loader()

        try:
            img.thumbnail((new_width, new_height), resample=PILImage.Resampling.LANCZOS, reducing_gap=2.0)
            return img

        except Exception as e:
            logger.exception(f"An error occurred while using new_thumbnail_reduce_keep_aspect. {str(e)}")

    def new_thumbnail_resize(self, new_width, new_height):
        """Returns a resized copy of this image. The method enlarges
        or reduces image size to provided width and height.

        Args:
            new_width (int): The requested width in pixels.
            new_height (int): The requested height in pixels.

        Returns:
            Returns resized image.
        """
        img = self.img_loader()

        try:
            return img.resize((new_width, new_height), resample=PILImage.Resampling.LANCZOS, box=None, reducing_gap=None)

        except Exception as e:
            logger.exception(f"An error occurred while using new_thumbnail_resize. {str(e)}")

    def new_thumbnail_keep_aspect(self, new_height):
        """Returns an image enlarged or reduced to specified height,
        while maintaining the aspect ratio.

        Args:
            new_height (int): The requested height in pixels.

        Returns:
            Returns resized image.
        """
        img = self.img_loader()

        try:
            hpercent = (new_height/float(img.size[1]))
            new_width = int((float(img.size[0])*float(hpercent)))
            return img.resize((new_width, new_height), resample=PILImage.Resampling.LANCZOS, box=None, reducing_gap=None)

        except Exception as e:
            logger.exception(f"An error occurred while using new_thumbnail_keep_aspect. {str(e)}")

    # def new_thumbnail_crop(self, box):
    #     """Returns a rectangular region from image.
    #     The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.

    #     Args:
    #         box (tuple(int)): 4-tuple defining the left, upper, right, and lower pixel coordinate (e.g. `(20, 20, 100, 100)`).

    #     Returns:
    #         Returns resized image.
    #     """
    #     img = self.img_loader()

    #     try:
    #         img.crop(box)
    #         return img

    #     except Exception as e:
    #         print(f"Exception occured: {str(e)}")
