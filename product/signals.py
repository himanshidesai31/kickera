from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib import messages
from .models import Cart

@receiver(post_save, sender=Cart)
def cart_item_added_or_updated(sender, instance, created, **kwargs):
    request = getattr(instance, '_request', None)
    if request:
        if created:
            messages.success(request, "Product added successfully. This is Example of Signal's file code Message ")
        else:
            messages.success(request, "Your product quantity has been updated in the cart. Please check your cart. also this is Signal's file code Message")

@receiver(post_delete, sender=Cart)
def cart_item_removed(sender, instance, **kwargs):
    request = getattr(instance, '_request', None)
    if request:
        messages.success(request, "Product removed from cart successfully. also this is Signal's file code Message")
