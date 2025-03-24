from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from vendor.forms import SellerLoginForm,SellerRegisterForm
from django.shortcuts import redirect

class SellerHomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'seller/seller.html'

class SellerRegisterView(LoginRequiredMixin,CreateView):
    template_name = 'seller/seller_register.html'
    form_class = SellerRegisterForm
    success_url = reverse_lazy('vendor-dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        print('-------form valid-------')
        # messages.success(self.request, 'Your vendor account has been created successfully.')
        return response

    def form_invalid(self, form):
        print('------form invalid--------')
        # messages.error(self.request, 'Something went wrong. Please correct the errors below.')
        return self.render_to_response(self.get_context_data(form=form))

class SellerLoginView(LoginView):
    form_class = SellerLoginForm
    template_name = 'seller/seller_login.html'

    def form_valid(self, form):
        user = authenticate(self.request, username=form.cleaned_data['email'], password=form.cleaned_data['password'])
        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Login successful.')
            return redirect('vendor-dashboard')  # Redirect instead of using success_url
        else:
            messages.error(self.request, 'Invalid login credentials.')
            return self.form_invalid(form)

class VendorDashboardView(TemplateView):
    template_name = 'seller/vendor_dashboard.html'
