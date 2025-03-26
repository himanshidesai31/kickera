# admin.py
from django.contrib import admin
from .models import Banner,  Deal, Brand

admin.site.register(Banner)
# admin.site.register(Product)
admin.site.register(Deal)
admin.site.register(Brand)
