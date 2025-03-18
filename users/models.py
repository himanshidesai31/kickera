from django.contrib.auth.models import AbstractUser
from django.db import models

#User model
class User(AbstractUser):
    mobile = models.CharField(max_length=15, unique=True, null=True)
    picture = models.ImageField(upload_to='profile_pics/', null=True)
    gender = models.CharField(max_length=50, null=True )
    birth_date = models.DateField(null=True)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100,blank=True)
    mobile = models.CharField(max_length=15)  # Removed `unique=True`
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default=HOME)
    city = models.CharField(max_length=100)
    Address = models.CharField(max_length=100 ,null=True)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100,null=True)
    pincode = models.CharField(max_length=10)  # Limited length for real pincodes

    def __str__(self):
        return f"{self.name} - {self.address_type} ({self.city})"
