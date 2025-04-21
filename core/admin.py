# admin.py
from django.contrib import admin
from .models import Banner, Deal, Brand, Contact

admin.site.register(Banner)
# admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Deal)
admin.site.register(Brand)
