# vendor/views.py
from allauth.headless.account.views import ChangePasswordView
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, TemplateView, UpdateView, DetailView, FormView
from orders.models import Order
from product.models import Product, Image, Category, Brand, SubCategory
from vendor.models import VendorProfile, VendorRequest
from vendor.forms import  SellerRegisterForm, VendorAddProductForm, VendorAddBrandForm, VendorAddCategoryForm, VendorProfileForm, VendorLoginForm, VendorAddSubCategoryForm
from django.views.generic.edit import CreateView
from users.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.hashers import make_password


class SellerRegisterView(FormView):#without using the model form i can used the FormView for this is Inquery
    template_name = 'seller/seller_register.html'
    form_class = SellerRegisterForm
    success_url = reverse_lazy('vendor_register_success')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        
        # Check if a vendor request with this email already exists
        existing_request = VendorRequest.objects.filter(email=email).exists()
        if existing_request:
            messages.error(self.request, "A vendor request with this email already exists and is pending approval.")
            return self.form_invalid(form)
            
        # Check if user already exists - we'll still create a vendor request
        user_exists = User.objects.filter(email=email).exists()
        
        # Create VendorRequest with hashed password
        vendor_request = VendorRequest.objects.create(
            business_name=form.cleaned_data['business_name'],
            phone_number=form.cleaned_data['phone_number'],
            email=email,
            gst_no=form.cleaned_data.get('gst_no'),
            tax_id=form.cleaned_data.get('tax_id'),
            business_registration_number=form.cleaned_data.get('business_registration_number'),
            logo=form.cleaned_data.get('logo'),
            status="pending",
            password=make_password(form.cleaned_data['password'])  # Store hashed password
        )
        
        # If user is authenticated, link this vendor request to them
        if self.request.user.is_authenticated and self.request.user.email == email:
            vendor_request.user = self.request.user
            vendor_request.save()
        
        # Try to send emails to admin
        try:
            admin_emails = [admin.email for admin in User.objects.filter(is_superuser=True) if admin.email]
            if admin_emails:
                send_mail(
                    subject='New Vendor Registration Request',
                    message=f"A new vendor '{form.cleaned_data['business_name']}' has registered and is awaiting approval.",
                    from_email=email,
                    recipient_list=admin_emails,
                    fail_silently=True,
                )
        except Exception:
            print('Something went wrong sending email to admin')
            
        # Try to send confirmation email to user
        try:
            send_mail(
                subject='Vendor Registration Request Received',
                message=(
                    f"Thank you for applying to become a vendor at KickEra. "
                    f"Your application for '{form.cleaned_data['business_name']}' is under review. "
                    f"You will receive an email when your application is approved or rejected."
                ),
                from_email=None,  # Use DEFAULT_FROM_EMAIL
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            print('Error sending confirmation email')
            
        if user_exists:
            messages.success(self.request, "Your vendor application has been submitted successfully. Since you already have an account, we've linked this request to your account. You will be notified once it is reviewed.")
        else:
            messages.success(self.request, "Your vendor application has been submitted successfully. You will be notified once it is reviewed.")
            
        return super().form_valid(form)


class VendorProfileView(LoginRequiredMixin, DetailView):
    model = VendorProfile
    template_name = 'seller/vendor_profile.html'
    context_object_name = 'vendor'

    def get_object(self, queryset=None):
        return get_object_or_404(VendorProfile, user=self.request.user)


class VendorProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = VendorProfile
    form_class = VendorProfileForm
    template_name = 'seller/vendor_profile_edit.html'
    success_url = reverse_lazy('vendor_profile')

    def get_object(self, queryset=None):
        return get_object_or_404(VendorProfile, user=self.request.user)


class SellerLoginView(LoginView):
    template_name = 'seller/seller_login.html'
    form_class = VendorLoginForm
    success_url = reverse_lazy('vendor_dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Set the user as a vendor if they're not already
        user = self.request.user
        if not user.is_vendor:
            # Check if they have a vendor profile
            vendor_profile = VendorProfile.objects.filter(user=user).exists()
            if vendor_profile:
                user.is_vendor = True
                user.save()
                print(f'User {user.email} is now marked as a vendor')
            
        return response
        
    def form_invalid(self, form):
        print('------------form is invalid----------')
        return super().form_invalid(form)
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return self.success_url


class VendorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'seller/vendor_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add vendor status information
        user = self.request.user
        
        try:
            context['vendor_profile'] = VendorProfile.objects.get(user=user)
        except VendorProfile.DoesNotExist:
            context['vendor_profile'] = None
            
        try:
            context['vendor_request'] = VendorRequest.objects.get(user=user)
        except VendorRequest.DoesNotExist:
            context['vendor_request'] = None
            
        return context


class VendorProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'seller/vendor_product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(vendor__user=self.request.user).select_related('vendor').prefetch_related('images')



class VendorAddProductView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'seller/vendor_add_products.html'
    form_class = VendorAddProductForm
    success_url = reverse_lazy('vendor_product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Load categories and print debug info
        categories = Category.objects.all()
        print(f"Categories count: {categories.count()}")
        for cat in categories:
            print(f"- Category: {cat.category_name} (ID: {cat.id})")
        context['categories'] = categories

        # Load brands
        context['brands'] = Brand.objects.all()

        # Load all subcategories and print debug info
        subcategories = SubCategory.objects.all()

        # Group subcategories by category for easy filtering in template
        subcategories_by_category = {}
        for cat in categories:
            subcategories_by_category[cat.id] = SubCategory.objects.filter(category=cat)

        context['subcategories'] = subcategories
        context['subcategories_by_category'] = subcategories_by_category

        print(f"Subcategories count: {subcategories.count()}")
        for subcat in subcategories:
            cat_name = subcat.category.category_name
            cat_id = subcat.category.id
            print(f"- All the Subcategory: {subcat.sub_category_name} (ID: {subcat.id}) - Category: {cat_name} (ID: {cat_id})")

        return context


    def form_valid(self, form):
        product = form.save(commit=False)
        product.vendor = self.request.user.vendor_profile
        product.save()

        images = self.request.FILES.getlist('images')
        for img in images:
            Image.objects.create(product=product, image=img)

        return redirect(self.success_url)


class VendorUpdateProductView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'seller/vendor_edit_product.html'
    form_class = VendorAddProductForm
    success_url = reverse_lazy('vendor_product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['product_images'] = self.object.images.all()
        
        # Load all subcategories 
        subcategories = SubCategory.objects.all()
        context['subcategories'] = subcategories
        
        return context

    def form_valid(self, form):
        product = form.save(commit=False)
        product.vendor = self.request.user.vendor_profile
        product.save()

        images = self.request.FILES.getlist('images')
        if images:
            product.images.all().delete()
            for img in images:
                Image.objects.create(product=product, image=img)

        return super().form_valid(form)


class VendorDeleteProductView(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('vendor_product_list')

    def get_queryset(self):
        return Product.objects.filter(vendor__user=self.request.user)


class VendorAddBrandView(LoginRequiredMixin, CreateView):
    model = Brand
    template_name = 'seller/vendor_add_brand.html'
    form_class = VendorAddBrandForm
    success_url = reverse_lazy('vendor_add_brand')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        return context


class VendorCategoryAddView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'seller/vendor_add_category.html'
    form_class = VendorAddCategoryForm
    success_url = reverse_lazy('vendor_add_category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        print('-------form  valid-----')
        return super().form_valid(form)

    def form_invalid(self, form):
        print('-------form  invalid-----')
        return super().form_invalid(form)


class VendorSubCategoryAddView(LoginRequiredMixin, CreateView):
    model = SubCategory
    template_name = 'seller/vendor_add_subcategory.html'
    form_class = VendorAddSubCategoryForm
    success_url = reverse_lazy('vendor_add_subcategory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subcategories'] = SubCategory.objects.all().select_related('category')
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        print('-------form valid-----')
        # Get the category from form data
        subcategory = form.save(commit=False)
        
        # Double-check that category is set
        if not subcategory.category_id and form.cleaned_data.get('category'):
            subcategory.category = form.cleaned_data.get('category')
            
        # Save the subcategory
        subcategory.save()
        
        # Show confirmation message
        messages.success(self.request, f'Subcategory "{subcategory.sub_category_name}" added to category "{subcategory.category.category_name}"')
        
        return super().form_valid(form)

    def form_invalid(self, form):
        print('-------form invalid-----')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error in {field}: {error}")
        return super().form_invalid(form)


#use for loading the subcategory list related there categories name's
def load_subcategory(request):
    category_id = request.GET.get('category_id')
    sub_categories = SubCategory.objects.filter(category_id=category_id).order_by('sub_category_name')
    return render(request, 'product/subcategory_dropdown_list_options.html', {
        'sub_categories': sub_categories
    })


class VendorOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'seller/vendor_order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        try:
            vendor_profile = self.request.user.vendor_profile
            return Order.objects.filter(
                product__vendor=vendor_profile
            ).order_by('-created_at')
        except VendorProfile.DoesNotExist:
            return Order.objects.none()

class VendorChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'seller/vendor_change_password.html'
    success_url = reverse_lazy('vendor_change_password_done')

    def form_valid(self, form):
        print('-------form valid-----')
        return super().form_valid(form)

    def form_invalid(self, form):
        print('-------form invalid-----')
        return super().form_invalid(form)


class VendorChangePassworDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'seller/vendor_change_password_done.html'