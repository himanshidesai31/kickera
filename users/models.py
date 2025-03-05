from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    mobile = models.CharField(max_length=120, unique=True  ,null=True)
    address = models.ForeignKey('Address', null=True, blank=True, on_delete=models.CASCADE)
    picture = models.ImageField(null=True)
    gender = models.CharField(max_length=100, null=True)
    birth_date = models.DateField(null=True)


class Address(models.Model):
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    area = models.TextField(max_length=100)
    pincode = models.CharField(max_length=100)


class Profile(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField() #read only do not update this
    username = models.CharField(max_length=150) #read only do not update this
    dob = models.DateField()
    phone_number = models.CharField(max_length=150)

