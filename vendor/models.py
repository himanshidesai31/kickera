from django.db import models
from users.models import User

class VendorRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    business_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    business_registration_number = models.CharField(max_length=50, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    gst_no = models.CharField(max_length=15, blank=True, null=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    password = models.CharField(max_length=128, blank=True, null=True)  # To store the hashed password
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.business_name} {self.status} {self.email}'


class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_profile')
    business_name = models.CharField(max_length=100, default="KickEra")
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    business_registration_number = models.CharField(max_length=50, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    gst_no = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)


    def __str__(self):
        return f'{self.business_name} {self.email}'
