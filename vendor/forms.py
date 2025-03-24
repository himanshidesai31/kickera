from django import forms
from vendor.models import VendorProfile


class SellerRegisterForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'phone_number', 'email', 'business_registration_number', 'tax_id', 'logo', 'gst_no']

    def save(self, commit=True):
        instance = super(SellerRegisterForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance


class SellerLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)