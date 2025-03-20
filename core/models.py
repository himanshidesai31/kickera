from django.db import models

# Product model:
class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('latest', 'Latest'),
        ('coming', 'Coming'),
    ]
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='latest')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', blank=True, null=True)

    def __str__(self):
        return self.name


# Banner model:
class Banner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# Deal model:
class Deal(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='deals/')
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    deal_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title


# Brand model:
class Brand(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='brands/')

    def __str__(self):
        return self.name

# class PasswordChangeFormModel(models.Model):
#     old_password = models.CharField(max_length=255)
#     new_password = models.CharField(max_length=255)
#     confirm_password = models.CharField(max_length=255)

#     def __str__(self):
#         return self.old_password
        