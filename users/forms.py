from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import Address, User


# ------------------------------
# User Update Form
# ------------------------------
class UserUpdateForm(forms.ModelForm):
    picture = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        widget=forms.FileInput(attrs={
            'class': 'custom-file-input',
            'accept': 'image/jpeg,image/png'
        })
    )

    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': date.today().strftime('%Y-%m-%d'),
            'class': 'form-control'
        }),
        error_messages={
            'required': 'Date of birth is required. Please select a valid date.',
            'invalid': 'Please enter a valid date format.'
        }
    )

    mobile = forms.CharField(
        widget=forms.TextInput(attrs={
            'pattern': '[0-9]{10,12}',
            'title': 'Please enter a valid mobile number (10-12 digits)'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'birth_date', 'mobile', 'picture', 'gender']
        widgets = {
            "email": forms.EmailInput(attrs={"readonly": "readonly"}),
            "username": forms.TextInput(attrs={"readonly": "readonly"}),
            "gender": forms.RadioSelect(attrs={'class': 'custom-control-input'})
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if len(first_name) < 2 or not first_name.replace(" ", "").isalpha():
            raise ValidationError("First name must be at least 2 letters and contain only alphabets.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if len(last_name) < 2 or not last_name.replace(" ", "").isalpha():
            raise ValidationError("Last name must be at least 2 letters and contain only alphabets.")
        return last_name

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        if not birth_date:
            raise ValidationError("Date of birth is required.")

        age = (date.today() - birth_date).days // 365
        if birth_date > date.today():
            raise ValidationError("The birth date cannot be in the future.")
        if age < 13:
            raise ValidationError("You must be at least 13 years old to use this service.")
        if age > 120:
            raise ValidationError("Please enter a valid birth date.")
        return birth_date

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile or not mobile.isdigit() or not (10 <= len(mobile) <= 12):
            raise ValidationError("Enter a valid mobile number between 10 and 12 digits.")
        if User.objects.exclude(pk=self.instance.pk).filter(mobile=mobile).exists():
            raise ValidationError("This mobile number is already in use.")
        return mobile

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        if picture and picture.size > 2 * 1024 * 1024:  # 2MB
            raise ValidationError("Image file size must be less than 2MB.")
        return picture


# ------------------------------
# Address Form
# ------------------------------
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'mobile', 'address_type', 'city', 'state', 'pincode', 'address', 'country']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError("The name field cannot be empty.")
        return name

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            raise ValidationError("Mobile number should be exactly 10 digits.")
        return mobile

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode or not pincode.isdigit() or not (6 <= len(pincode) <= 8):
            raise ValidationError("Pincode should be between 6 and 8 digits.")
        return pincode
