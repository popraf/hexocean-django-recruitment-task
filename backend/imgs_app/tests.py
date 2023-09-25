from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import UploadedImage, Thumbnail, ExpiringLink
from auth_app.models import ThumbnailHeight, UserTier
from .validators import validate_img_extension, validate_img_size
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from imgs_app.models import UploadedImage, Thumbnail, ExpiringLink
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class ModelTestCase(TestCase):
    def setUp(self):
        # Create a test ThumbnailHeight
        self.thumbnail_height = ThumbnailHeight.objects.create(
            available_height=200
        )

        # Create a test UserTier and set the many-to-many relationship
        self.user_tier = UserTier.objects.create(
            name="Test Tier",
            accessOriginalFile=True,
            accessGenerateExpiringLinks=True
        )
        self.user_tier.thumbnailHeight.set([self.thumbnail_height])

        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            userTier = self.user_tier,
        )

        # Create a test UploadedImage
        self.uploaded_image = UploadedImage.objects.create(
            uploadedImage="path/to/image.jpg",
            user=self.user
        )

        # Create a test Thumbnail
        self.thumbnail = Thumbnail.objects.create(
            parentImage=self.uploaded_image,
            thumbnail="path/to/thumbnail.jpg",
            height=self.thumbnail_height,
            user=self.user
        )

    def test_uploaded_image_str(self):
        # Test the __str__ method of UploadedImage model
        uploaded_image = UploadedImage.objects.create(
            uploadedImage="path/to/image.jpg",
            user=self.user
        )
        self.assertEqual(
            str(uploaded_image),
            f"Image {uploaded_image.pk} - User {self.user.username}"
        )

    def test_thumbnail_str(self):
        # Test the __str__ method of Thumbnail model
        uploaded_image = UploadedImage.objects.create(
            uploadedImage="path/to/image.jpg",
            user=self.user
        )
        thumbnail = Thumbnail.objects.create(
            parentImage=uploaded_image,
            thumbnail="path/to/thumbnail.jpg",
            height=self.thumbnail_height,
            user=self.user
        )
        self.assertEqual(
            str(thumbnail),
            f"Thumbnail object ({thumbnail.pk})"
        )

    def test_expiring_link_str(self):
        # Test the __str__ method of ExpiringLink model
        expiring_link = ExpiringLink.objects.create(
            user=self.user,
            expiryTime=600,
            linkUUID="test_uuid"
        )
                
        self.assertEqual(
            str(expiring_link),
            f"ExpiringLink object ({expiring_link.pk})"
        )

    def test_expiring_link_validators(self):
        # Test the validators for expiryTime field in ExpiringLink model
        # Test a valid value (600)
        expiring_link = ExpiringLink(
            user=self.user,
            expiryTime=600,
            linkUUID="test_uuid"
        )
        expiring_link.full_clean()  # Should not raise ValidationError

        # Test a value below the minimum (299)
        invalid_expiring_link = ExpiringLink(
            user=self.user,
            expiryTime=299,
            linkUUID="test_uuid"
        )
        with self.assertRaises(ValidationError):
            invalid_expiring_link.full_clean()

        # Test a value above the maximum (30001)
        invalid_expiring_link = ExpiringLink(
            user=self.user,
            expiryTime=30001,
            linkUUID="test_uuid"
        )
        with self.assertRaises(ValidationError):
            invalid_expiring_link.full_clean()


class ViewsTestCase(TestCase):
    def setUp(self):
        # Create a test ThumbnailHeight
        self.thumbnail_height = ThumbnailHeight.objects.create(
            available_height=200
        )

        # Create a test UserTier and set the many-to-many relationship
        self.user_tier = UserTier.objects.create(
            name="Test Tier",
            accessOriginalFile=True,
            accessGenerateExpiringLinks=True
        )
        self.user_tier.thumbnailHeight.set([self.thumbnail_height])

        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            userTier = self.user_tier,
        )

        # Create a test UploadedImage
        self.uploaded_image = UploadedImage.objects.create(
            uploadedImage='./imgs_app/example_imgs/su1_1024x1024.jpg',
            user=self.user
        )

        # Create a test Thumbnail
        self.thumbnail = Thumbnail.objects.create(
            parentImage=self.uploaded_image,
            thumbnail='./imgs_app/example_imgs/su1_1024x1024.jpg',
            height=self.thumbnail_height,
            user=self.user
        )

        # Create a test ExpiringLink
        self.expiring_link = ExpiringLink.objects.create(
            user=self.user,
            expiryTime=600,
            linkUUID="test_uuid"
        )

        # Create an API client
        self.client = APIClient()
    
    def test_upload_image_view(self):
        url = reverse('images_upload')
        image_path = './imgs_app/example_imgs/su1_1024x1024.jpg'
        image_file = open(image_path, 'rb')  # Open the file in binary mode
        data = {
            'user': self.user.username,
            'uploadedImage': SimpleUploadedFile("image.jpg", image_file.read())
            }
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_images_list_api_view(self):
        url = reverse('images_view')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add assertions for the response data as needed

    def test_thumbnails_list_api_view(self):
        url = reverse('thumbnails_view', kwargs={'height': self.thumbnail_height.available_height})
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add assertions for the response data as needed

    def test_expiring_link_create_api_view_no_selections(self):
        url = reverse('expiring_link_create')
        data = {
            'expiryTime': 600,
        }
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expiring_link_retrieve_view(self):
        url = reverse('expiring_link_view', kwargs={'linkUUID': self.expiring_link.linkUUID})
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
