# vendor/views.py
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, TemplateView, UpdateView, DetailView
from product.models import Product, Image, Category, Brand
from vendor.models import VendorProfile
from vendor.forms import SellerLoginForm, SellerRegisterForm, VendorAddProductForm, VendorAddBrandForm, VendorAddCategoryForm


class SellerHomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'seller/seller.html'


class SellerRegisterView(CreateView):  # LoginRequiredMixin हटाया
    template_name = 'seller/seller_register.html'
    form_class = SellerRegisterForm
    success_url = reverse_lazy('vendor_dashboard')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_vendor = True
        user.save()
        return super().form_valid(form)


class VendorProfileView(LoginRequiredMixin, DetailView):
    model = VendorProfile
    template_name = 'seller/vendor_profile.html'
    context_object_name = 'vendor'

    def get_object(self, queryset=None):
        return get_object_or_404(VendorProfile, admin=self.request.user)


class VendorProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = VendorProfile
    form_class = SellerRegisterForm
    template_name = 'seller/vendor_profile_edit.html'
    success_url = reverse_lazy('vendor_profile')

    def get_object(self, queryset=None):
        return get_object_or_404(VendorProfile, admin=self.request.user)


class SellerLoginView(LoginView):
    template_name = 'seller/seller_login.html'
    form_class = SellerLoginForm
    success_url = reverse_lazy('vendor_dashboard')


class VendorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'seller/vendor_dashboard.html'


class VendorProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'seller/vendor_product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(vendor__admin=self.request.user).select_related('vendor').prefetch_related('images')


class VendorAddProductView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'seller/vendor_add_products.html'
    form_class = VendorAddProductForm
    success_url = reverse_lazy('vendor_product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context

    def form_valid(self, form):
        product = form.save(commit=False)
        product.vendor = self.request.user.vendorprofile
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
        return context

    def form_valid(self, form):
        product = form.save(commit=False)
        product.vendor = self.request.user.vendorprofile
        product.save()

        images = self.request.FILES.getlist('images')
        if images:
            product.images.all().delete()  # ⚠ इमेज डिलीट करने से पहले वेरिफाई करें!
            for img in images:
                Image.objects.create(product=product, image=img)

        return super().form_valid(form)


class VendorDeleteProductView(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('vendor_product_list')

    def get_queryset(self):
        return Product.objects.filter(vendor__admin=self.request.user)


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
