from django.contrib import messages
from django.contrib.messages import success
from django.http import request, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView, FormView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin 
from .forms import AddressForm
from .models import Address
from django.shortcuts import redirect

#profile view class
class ProfileView(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'user/profile.html'
    success_url = reverse_lazy('profile')

    def get_success_url(self):
        return reverse_lazy('profile',kwargs={'pk':self.request.user.id})

    def form_valid(self, form):
        response = super().form_valid(form)
        print('-------------------valid form-------------------')
        messages.success(self.request, 'Profile updated successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Something went wrong , Invalid Form Submission ,Please Try Again')
        return super(ProfileView, self).form_invalid(form)

    def get_object(self, queryset=None):
        return self.request.user


#this is only list of address of the user right
class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    context_object_name = 'addresses'
    template_name = 'user/address_list.html'
    success_url = reverse_lazy('address-list')

    #used for filter user address
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        return self.request.user



#this is view only user can add new adders right
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
            return reverse_lazy('index')

#update address class view
class UpdateAddressView(LoginRequiredMixin, UpdateView):
    model = Address
    template_name = 'user/edit_address.html'
    form_class = AddressForm
    success_url = reverse_lazy('address_list_view')
    

#detete address class view
class DeleteAddressView(LoginRequiredMixin, DeleteView):
    model = Address
    from_class = AddressForm
    success_url = reverse_lazy('address_list_view')
