from typing import Any

from django.db import models
from users.models import User
from vendor.models import VendorProfile

#product model
class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('latest', 'Latest'),
        ('coming', 'Coming'),
    ]

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='latest')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE ,null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.name


class Brand(models.Model):
    brand_name =models.CharField(max_length=255 ,null=True)

    def __str__(self):
        return self.brand_name


# Image Model
class Image(models.Model):
    image = models.ImageField(upload_to='product/images/', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')


#category model
class Category(models.Model):
    category_name = models.CharField(max_length=255,null=True)

    def __str__(self):
        return self.category_name


#checkout model

#conirmation model
class Confirmation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='confirmations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name if self.product else 'Unknown Product'

    class Meta:

        verbose_name_plural = "Confirmations"


#cart model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.user.username if self.user else 'Unknown User'}'s Cart"

    @property
    def total_price(self):
        return self.quantity * self.product.price


#wishlist
class WishList(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.product.name if self.product else 'Unknown Product'


    @property
    def total_price(self):
        return self.quantity * self.product.price
