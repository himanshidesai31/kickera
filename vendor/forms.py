from django import forms
from vendor.models import VendorProfile
from product.models import Product, Brand


class SellerRegisterForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'phone_number', 'email', 'business_registration_number', 'tax_id', 'logo', 'gst_no']

    def save(self, commit=True):
        instance = super(SellerRegisterForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance


class SellerLoginForm(forms.Form):  # Ensure forms is defined
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class VendorAddProductForm(forms.ModelForm):
    images = forms.FileField()

    class Meta:
        model = Product
        fields = ['product_type', 'name', 'price', 'discount', 'original_price', 'stock', 'category', 'brand', 'images']


class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'phone_number', 'email', 'business_registration_number', 'tax_id', 'logo', 'gst_no']


class VendorAddBrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name']