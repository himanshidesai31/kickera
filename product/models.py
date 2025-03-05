from django.db import models
from core.models import  Product
from users.models import User


#category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    id = models.AutoField(primary_key=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Set default value here
    image = models.ImageField(null=False, default='categories/default_image.jpg')
    description = models.TextField(blank=True, null=True)


#checkout model
class Checkout(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Checkouts"

#cart model
class Cart(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product)

    def __str__(self):
        return self.user.username + "'s Cart"

#conirmation model
class Confirmation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name

    class Meta:

        verbose_name_plural = "Confirmations"


class Order(models.Model):
    status = (
        ('Shipped', 'Shipped'),
        ('In Delivery', 'In Delivery'),
    )

    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product)

    name = models.CharField(max_length=500, null=True)
    email = models.EmailField(max_length=500, null=True)
    address = models.CharField(max_length=1000, null=True)
    card_number = models.CharField(max_length=16, null=True)
    cvv = models.CharField(max_length=3, null=True)

    shipped = models.CharField(max_length=50, null=True, choices=status)

    def __str__(self):
        return self.user.username + "'s Order"
