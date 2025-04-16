from django.contrib import admin
from product.models import Cart, Confirmation, Product, Image, Category, Brand, WishList, SubCategory

admin.site.register(Product)
# admin.site.register(Checkout)
admin.site.register(Cart)
admin.site.register(WishList)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Confirmation)
admin.site.register(Image)
admin.site.register(Brand)