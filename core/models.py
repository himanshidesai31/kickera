from django.db import models

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
    description = models.TextField(blank=True, null=True)
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

#Contact Model For Website FeedBack
class Contact(models.Model):
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    email = models.EmailField(max_length=100,null=True)
    message = models.TextField(max_length=400,null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"