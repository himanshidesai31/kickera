from django.contrib.auth.models import AbstractUser
from django.db import models


class Address(models.Model):
    WORK = 'work'
    HOME = 'home'
    OTHER = 'other'

    ADDRESS_TYPES = [
        (WORK, 'Work'),
        (HOME, 'Home'),
        (OTHER, 'Other'),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)  # Removed `unique=True`
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default=WORK)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)  # Limited length for real pincodes

    def __str__(self):
        return f"{self.name} - {self.address_type} ({self.city})"

#User model
class User(AbstractUser):
    mobile = models.CharField(max_length=15, unique=True, null=True)
    address = models.ForeignKey(
        Address, null=True, on_delete=models.SET_NULL, related_name="users"
    )
    picture = models.ImageField(upload_to='profile_pics/', null=True)
    gender = models.CharField(max_length=50, null=True)
    birth_date = models.DateField(null=True)

    def __str__(self):
        return f"{self.username}:{self.email}"