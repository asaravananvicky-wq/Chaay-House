from django.contrib.auth.models import User
from django.db import models


class CustomerProfile(models.Model):
    """Extra profile information for every registered customer.

    We keep Django's built-in User model for authentication (secure password
    hashing, login/logout, sessions) and attach shop-specific fields here.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    is_admin_staff = models.BooleanField(default=False, help_text="Shop staff who can access the admin dashboard")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s profile"
