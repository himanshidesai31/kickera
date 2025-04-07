from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    mobile = models.CharField(max_length=15, unique=True, null=True)
    picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_vendor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username}:{self.email}"

class Address(models.Model):
    WORK = 'work'
    HOME = 'home'
    OTHER = 'other'

    ADDRESS_TYPES = [
        (WORK, 'Work'),
        (HOME, 'Home'),
        (OTHER, 'Other'),
    ]

    vendor = models.ForeignKey('vendor.VendorProfile', null=True, blank=True, on_delete=models.CASCADE, related_name='addresses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='addresses')
    name = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default=HOME)
    city = models.CharField(max_length=100)
    Address = models.CharField(max_length=255, null=True, blank=True)  # Fixed field name (lowercase "address")
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} - {self.address_type} ({self.city})"
