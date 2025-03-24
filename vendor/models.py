from django.db import models
from users.models import User


class VendorProfile(models.Model):
    admin = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    business_name = models.CharField(max_length=100, default="kickera")
    phone_number = models.CharField(max_length=15 ,null=True)
    email = models.EmailField(unique=True , null=True)
    business_registration_number = models.CharField(max_length=50, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    gst_no = models.CharField(max_length=15, blank=True, null=True)