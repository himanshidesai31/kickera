from django.contrib import admin
from product.models import Category,Checkout, Cart, Confirmation

admin.site.register(Category)
# admin.site.register(CartItem)
admin.site.register(Checkout)
admin.site.register(Cart)
admin.site.register(Confirmation)