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