from django.test import TestCase
from django.core.exceptions import ValidationError  
from auth_app.models import ThumbnailHeight, UserTier, CustomUser

class ModelTestCase(TestCase):
    def setUp(self):
        # Create some test data for the models
        self.thumbnail_height = ThumbnailHeight.objects.create(available_height=200)
        self.user_tier = UserTier.objects.create(
            name="Basic Tier",
            accessOriginalFile=False,
            accessGenerateExpiringLinks=False,
        )
        self.custom_user = CustomUser.objects.create(
            username="testuser",
            userTier=self.user_tier,
        )

    def test_thumbnail_height_str(self):
        # Test the __str__ method of ThumbnailHeight model
        self.assertEqual(
            str(self.thumbnail_height),
            f"Defined thumbnail height PK {self.thumbnail_height.pk} - {self.thumbnail_height.available_height}px",
        )

    def test_user_tier_str(self):
        # Test the __str__ method of UserTier model
        self.assertEqual(str(self.user_tier), "Basic Tier")

    def test_custom_user_str(self):
        # Test the __str__ method of CustomUser model
        self.assertEqual(str(self.custom_user), "testuser")

    def test_custom_user_default_user_tier(self):
        # Test that a new CustomUser instance uses the default UserTier with PK 1
        new_user = CustomUser.objects.create(username="newuser")
        self.assertEqual(new_user.userTier.pk, 1)

    def test_thumbnail_height_validators(self):
        # Test the validators for available_height field
        # Test a valid value (200)
        valid_thumbnail_height = ThumbnailHeight(available_height=200)
        # valid_thumbnail_height.full_clean()  # Should raise ValidationError as height 200 is already in db
        with self.assertRaises(ValidationError) as context:
            valid_thumbnail_height.full_clean()

        # Test a value below the minimum (24)
        invalid_thumbnail_height = ThumbnailHeight(available_height=24)
        with self.assertRaises(ValidationError):
            invalid_thumbnail_height.full_clean()

        # Test a value above the maximum (8641)
        invalid_thumbnail_height = ThumbnailHeight(available_height=8641)
        with self.assertRaises(ValidationError):
            invalid_thumbnail_height.full_clean()

    def test_user_tier_thumbnail_height_relationship(self):
        # Test the relationship between UserTier and ThumbnailHeight
        self.user_tier.thumbnailHeight.add(self.thumbnail_height)
        self.assertIn(self.thumbnail_height, self.user_tier.thumbnailHeight.all())

    def test_custom_user_user_tier_relationship(self):
        # Test the relationship between CustomUser and UserTier
        self.assertEqual(self.custom_user.userTier, self.user_tier)

