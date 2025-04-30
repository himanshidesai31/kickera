from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView, FormView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AddressForm, UserUpdateForm
from .models import Address, User
from datetime import date
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


# profile view class
class ProfileView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'user/profile.html'
    # context_object_name = 'user'

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id) #use for filter multiple user ,for use case  in high level complex logic
        # return User.objects.get(pk=self.request.user.id) #get the current user

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user/profile_update.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        try:
            # Handle profile picture
            if 'picture' in self.request.FILES:
                form.instance.picture = self.request.FILES['picture']

            response = super().form_valid(form)
            messages.success(self.request, 'Profile updated successfully!')
            return response
        except Exception as e:
            messages.error(self.request, f'Error updating profile: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Profile'
        context['today'] = date.today()
        return context


# this is only list of address of the user right
class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    context_object_name = 'addresses'
    template_name = 'user/address_list.html'
    success_url = reverse_lazy('address-list')

    # used for filter user address
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        return self.request.user


# this is view only user can add new adders right
class Add_AddressListView(LoginRequiredMixin, FormView):
    template_name = 'user/address_add.html'
    form_class = AddressForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        messages.success(self.request, 'Address added successfully!')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        # Check if we have a product_id in the request for redirecting back to shipping address
        product_id = self.request.POST.get('product_id')
        next_url = self.request.POST.get('next')
        next_url2 = self.request.POST.get('next1')
        go_to_checkout = self.request.POST.get('go_to_checkout')

        if product_id and go_to_checkout:
            return reverse_lazy('checkout')
        elif product_id:
            return reverse_lazy('check_user_address', kwargs={'pk': product_id})
        elif next_url:
            return reverse_lazy('address_list_view')
        elif next_url2:
            return reverse_lazy('check_user_address', kwargs={'pk': 2})  # Default to product ID 2 if not specified
        else:
            return reverse_lazy('address_list_view') #redirect  after adding the new address


# update address class view
class UpdateAddressView(LoginRequiredMixin, UpdateView):
    model = Address
    template_name = 'user/edit_address.html'
    form_class = AddressForm
    success_url = reverse_lazy('address_list_view')
    
    def get_object(self, queryset=None):
        # Get the address and verify it belongs to the current user
        address_id = self.kwargs.get('pk')
        return get_object_or_404(Address, id=address_id, user=self.request.user)
        
    def form_valid(self, form):
        messages.success(self.request, 'Address updated successfully!')
        return super().form_valid(form)


# Detele address class view for deleteing the  object
class DeleteAddressView(LoginRequiredMixin, DeleteView):
    model = Address
    from_class = AddressForm
    success_url = reverse_lazy('address_list_view')


# Custom login redirect view
def custom_login_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_vendor:
            return redirect('vendor_dashboard')
        else:
            return redirect('index')
    return redirect('account_login')

def test_email_settings(request):
    try:
        send_mail(
            'Test Email from KickEra',
            'This is a test email to verify email settings.',
            settings.EMAIL_HOST_USER,
            ['chaudharykamlesh185@gmail.com'],
            fail_silently=False,
        )
        return JsonResponse({'status': 'success', 'message': 'Test email sent successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
