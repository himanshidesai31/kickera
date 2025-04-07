from django.db import models
from orders.models import Order


class Payment(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, null=True)
    amount = models.FloatField(null=True)
    status = models.CharField(max_length=100, null=True)
    currency = models.CharField(max_length=3, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer_details = models.JSONField(null=True)

    def __str__(self):
        return f"{self.payment_id}'s Order"