from django.db import models
from users.models import User

class VendorProfile(models.Model):
    admin = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name="vendorprofile")
    business_name = models.CharField(max_length=100, default="KickEra")
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    business_registration_number = models.CharField(max_length=50, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    gst_no = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.business_name} ({self.admin.username if self.admin else 'No Admin'})"
