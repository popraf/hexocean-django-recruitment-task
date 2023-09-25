from django.contrib import admin
from auth_app.models import UserTier, CustomUser, ThumbnailHeight


class ThumbnailHeightAdmin(admin.ModelAdmin):
    """
    ! DO NOT REMOVE `available_height` FROM readonly_fields !
    It prevents modifying from user panel defined height, however
    on db level it is still possible to modify it, so be cautious.
    This field is linked to thumbnails and user tiers - after update
    thumbnails are not processed, resulting in incorrect size return.
    """
    readonly_fields = ['available_height']  # ! DO NOT REMOVE `available_height` FROM readonly_fields !

    def has_add_permission(self, request):
        return True  # Allow adding new instances

    def has_change_permission(self, request, obj=None):
        return False  # Disallow changing existing instances

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deleting instances


admin.site.register(ThumbnailHeight, ThumbnailHeightAdmin)
admin.site.register(UserTier)
admin.site.register(CustomUser)