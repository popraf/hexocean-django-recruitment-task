from django.urls import path
from imgs_app.views import (
    UploadImageView, 
    ImagesListApiView, 
    ThumbnailsListApiView, 
    ExpiringLinkCreateApiView,
    ExpiringLinkRetrieveView
    )

urlpatterns = [
    path('images/upload/', UploadImageView.as_view(), name='images_upload'),
    path('images/view/', ImagesListApiView.as_view(), name='images_view'),
    path('thumbnails/view/<int:height>/', ThumbnailsListApiView.as_view(), name='thumbnails_view'),
    path('expiring_link/new/', ExpiringLinkCreateApiView.as_view(), name='expiring_link_create'),
    path('expiring_link/<str:linkUUID>/', ExpiringLinkRetrieveView.as_view(), name='expiring_link_view'),
]
