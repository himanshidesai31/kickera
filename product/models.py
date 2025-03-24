from django.db import models
from core.models import Product
from users.models import User

#category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    id = models.AutoField(primary_key=True)
    # Removed price field as it is not relevant to categories
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


#conirmation model
class Confirmation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='confirmations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name if self.product else 'Unknown Product'

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
        return f"{self.user.username if self.user else 'Unknown User'}'s Order"


#cart model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)

    # def __str__(self):
    #     return f"{self.quantity} x {self.product.name} in {self.user.username if self.user else 'Unknown User'}'s Cart"

    def total_price(self):
        return self.quantity * self.product.price


#cartItem model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE , related_name='cart_items' ,null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.cart.product.name} in {self.cart.user.username if self.cart.user else 'Unknown User'}'s Cart"
