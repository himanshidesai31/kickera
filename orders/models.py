from django.db import models
from product.models import Product
from users.models import User

# Create your models here.
class Order(models.Model):
    status = (
        ('Shipped', 'Shipped'),
        ('In Delivery', 'In Delivery'),
    )
    order_status = models.CharField(max_length=20, choices=status, default='Shipped')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=100, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    name = models.CharField(max_length=500, null=True)
    email = models.EmailField(max_length=500, null=True)
    address = models.CharField(max_length=1000, null=True)
    card_number = models.CharField(max_length=16, null=True)
    cvv = models.CharField(max_length=3, null=True)
    shipped = models.CharField(max_length=50, null=True, choices=status)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown User'}'s Order"
