from django import forms
from core.models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'message']
        widgets = {'first_name': forms.TextInput(attrs={ 'class': 'form-control','placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Enter your email address'}),
            'message': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Enter your message here','rows': 5}),
        }
