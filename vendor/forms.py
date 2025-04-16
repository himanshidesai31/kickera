from django import forms
from vendor.models import VendorProfile
from product.models import Product, Brand, Category, SubCategory
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


class SellerRegisterForm(forms.Form):
    business_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=15)
    email = forms.EmailField()
    business_registration_number = forms.CharField(max_length=50, required=False)
    tax_id = forms.CharField(max_length=50, required=False)
    gst_no = forms.CharField(max_length=15, required=False)
    logo = forms.ImageField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data


class VendorLoginForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(VendorLoginForm, self).__init__(request=request, *args, **kwargs)
        self.fields.pop('username')  # Remove the username field
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            # Set the username to email for authentication
            self.cleaned_data['username'] = email
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
            elif not self.user_cache.is_vendor:
                raise forms.ValidationError("This account is not registered as a vendor.")
        
        return self.cleaned_data


class VendorAddProductForm(forms.ModelForm):
    images = forms.FileField()

    class Meta:
        model = Product
        fields = ['product_type', 'name', 'price', 'discount', 'original_price', 'stock', 'category', 'subcategory', 'brand', 'images']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subcategory'].queryset = SubCategory.objects.none()
        
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = self.instance.category.subcategories.all()


class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'phone_number', 'email', 'business_registration_number', 'tax_id', 'logo', 'gst_no']


class VendorAddBrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name']


class VendorAddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']


class VendorAddSubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'sub_category_name']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].label = "Main Category"
        self.fields['sub_category_name'].label = "Sub Category Name"
