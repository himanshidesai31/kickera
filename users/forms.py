#this is forms.py
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Address,User


#userUpdateForm
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User

        # fields = ['first_name','last_name','email','username','birth_date','mobile'  ,'picture','gender','address']
        fields = ['first_name','last_name','email','username','birth_date','mobile','picture','gender']
        widgets = {
            "email": forms.EmailInput(attrs={"readonly": "readonly"}),  # Readonly email
            "username": forms.TextInput(attrs={"readonly": "readonly"}),  # Readonly username
        }

    #first_name validation
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise ValidationError("Please enter a first name.")
        return first_name

    #last_name validation
    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise ValidationError("Please enter a last name.")
        return last_name

    #birth_date validation
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        if birth_date:
            if birth_date > date.today():
                raise ValidationError("The birth date cannot be in the future.")
        return birth_date

    #mobile validation
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile:
            raise ValidationError("The mobile field cannot be empty.")

        if not mobile.isdigit():
            raise ValidationError("Enter a valid mobile number (digits only).")

        if len(mobile) < 10 or len(mobile) > 12:
            raise ValidationError("Mobile number should be between 10 and 12 digits.")
        return mobile



#address form
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'mobile', 'address_type', 'city', 'state', 'pincode', 'Address', 'country']  # Fixed 'address'

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("The name field cannot be empty.")
        return name

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile:
            raise ValidationError("The mobile field cannot be empty.")
        if not mobile.isdigit():
            raise ValidationError("Enter a valid mobile number (digits only).")
        if len(mobile) != 10:  # Fixed logic for 10-digit number
            raise ValidationError("Mobile number should be exactly 10 digits.")
        return mobile

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode:
            raise ValidationError("The pincode field cannot be empty.")
        if not pincode.isdigit():
            raise ValidationError("Pincode should only contain digits.")
        if len(pincode) < 6 or len(pincode) > 8:
            raise ValidationError("Pincode should be between 6 and 8 digits.")
        return pincode
