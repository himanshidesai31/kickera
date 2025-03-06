#this is forms.py
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Address,User


#userUpdateForm
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "mobile", "picture", "gender", "birth_date"]
        widgets = {
            "email": forms.EmailInput(attrs={"readonly": "readonly"}),  # Readonly email
            "username": forms.TextInput(attrs={"readonly": "readonly"}),  # Readonly username
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise ValidationError("The birth date cannot be in the future.")
        return birth_date
    
    # def mobile_validation(self):
    #     mobile_number = self.cleaned_data.get('mobile')
    #     if mobile_number:


#address form
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'mobile', 'address_type', 'city', 'state', 'pincode']