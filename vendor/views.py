#vendor/views.py
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from product.models import Product, Image, Category, Brand
from users.models import User
from vendor.forms import SellerLoginForm, SellerRegisterForm, VendorAddProductForm, VendorAddBrandForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, TemplateView, UpdateView, DetailView
from vendor.models import  VendorProfile


class SellerHomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'seller/seller.html'


class SellerRegisterView(LoginRequiredMixin,CreateView):
    template_name = 'seller/seller_register.html'
    form_class = SellerRegisterForm
    success_url = reverse_lazy('vendor_dashboard')

    def form_valid(self, form):
        form.instance.admin = self.request.user
        response = super().form_valid(form)

        # Save the VendorProfile first
        user = User.objects.get(id=self.request.user.id)
        user.is_vendor = True
        user.save()
        return response

    def form_invalid(self, form):
        print('------form invalid--------')
        return self.render_to_response(self.get_context_data(form=form))

#Vendor profile view showing the vendor user details
class VendorProfileView(DetailView):
    model = VendorProfile
    template_name = 'seller/vendor_profile.html'
    context_object_name = 'vendor'

    # def get_queryset(self):
    #     return VendorProfile.objects.filter(admin=self.request.user)  # QuerySet return kre che

    def get_object(self, queryset=None):
        return self.get_queryset().first() # first record return kre che

class VendorProfileUpdateView(UpdateView):
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


class VendorDashboardView(TemplateView):
    template_name = 'seller/vendor_dashboard.html'


#vendor product related view's
class VendorProductListView(LoginRequiredMixin,ListView):
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
        product = form.save(commit=False)  #
        product.vendor = self.request.user.vendorprofile
        product.save()  # Now save it

        #  image upload
        images = self.request.FILES.getlist('images')
        for img in images:
            Image.objects.create(product=product, image=img)

        return redirect(self.success_url)


class VendorUpdateProductView(LoginRequiredMixin, UpdateView):
    template_name = 'seller/vendor_edit_product.html'
    model = Product
    form_class = VendorAddProductForm
    success_url = reverse_lazy('vendor_product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()  # Pass all brands to the template

        if self.object.category:
            context['selected_category'] = self.object.category.id

        if self.object.brand:
            context['selected_brand'] = self.object.brand.id

        return context


    def form_valid(self, form):
        form.instance.vendor = VendorProfile.objects.filter(admin=self.request.user).first()
        category_name = self.request.POST.get('category')

        if category_name:
            try:
                category = Category.objects.get(id=category_name)
                form.instance.category = category
            except Category.DoesNotExist:
                form.add_error('category', 'Invalid category selected.')
                return self.form_invalid(form)

        self.object = form.save()

        images = self.request.FILES.getlist('images')
        if images:
            self.object.images.all().delete()
            for img in images:
                Image.objects.create(product=self.object, image=img)

        return super().form_valid(form)


    def form_invalid(self, form):
        print('------form invalid--------')
        return self.render_to_response(self.get_context_data(form=form))


class VendorDeleteProductView(LoginRequiredMixin,DeleteView):
    model = Product
    success_url = reverse_lazy('vendor_product_list')

    def get_queryset(self):
        return Product.objects.filter(vendor__admin=self.request.user)


class VendorAddBrandView(LoginRequiredMixin, CreateView):
    model = Brand
    template_name = 'seller/Vendor_add_brand.html'
    form_class = VendorAddBrandForm
    success_url = reverse_lazy('vendor_add_brand')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['brands'] = Brand.objects.all()
        return context

    def form_valid(self, form):
        print('------form valid--------')
        return super().form_valid(form)

    def form_invalid(self, form):
        print('------form invalid--------')
        return super().form_invalid(form)
