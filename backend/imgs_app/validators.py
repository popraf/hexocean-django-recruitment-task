from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_img_extension(value):
    """
    Custom function to validate image file extension.
    """
    return FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])(
        value
    )

def validate_img_size(value):
    """
    Custom function to validate image file size.
    """
    max_size = 25 * 1024 * 1024 # 25MB

    if value.size > max_size:
        raise ValidationError("File size is above limits.")
