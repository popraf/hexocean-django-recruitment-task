from rest_framework.permissions import BasePermission

class NewExpiringLinksCreatePermission(BasePermission):
    def has_permission(self, request, view):
        return (request.user.userTier.accessGenerateExpiringLinks or request.user.is_staff)