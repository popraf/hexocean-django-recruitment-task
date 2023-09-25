from django.contrib import admin
from .models import UploadedImage, Thumbnail, ExpiringLink


admin.site.register(UploadedImage)
admin.site.register(Thumbnail)
admin.site.register(ExpiringLink)