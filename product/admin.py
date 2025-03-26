from django.contrib import admin
from product.models import  Checkout,Category ,Cart, Confirmation, Product, Image

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Checkout)
admin.site.register(Cart)
admin.site.register(Confirmation)
admin.site.register(Image)