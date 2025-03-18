from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView, FormView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin 
from .forms import UserUpdateForm, AddressForm
from .models import User, Address
from django.shortcuts import redirect

#profile view class
class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
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
        messages.error(self.request, 'Something went wrong , Invalid Form Submission')
        return super(ProfileView, self).form_invalid(form)

    def get_object(self, queryset=None):
        return self.request.user


#address list class view
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

#add address class view
class Add_AddressListView(LoginRequiredMixin, FormView):
    template_name = 'user/address_add.html'
    form_class = AddressForm
    success_url = reverse_lazy('address_list_view')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form Submission, Please fill the form correctly')
        print("-----------Form Invalid")  # Debugging message
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return redirect(self.success_url)
        print("-----------Form Valid")
        return super().form_valid(form)

    
    
#update address class view
class UpdateAddressView(LoginRequiredMixin, UpdateView):
    model = Address
    template_name = 'user/edit_address.html'
    form_class = AddressForm
    success_url = reverse_lazy('address_list_view')
    

#detete address class view
class DeleteAddressView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'user/delete_address.html'
    from_class = AddressForm
    success_url = reverse_lazy('address_list_view')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete(self, request, *args, **kwargs)
        messages.success(self.request, 'Address deleted successfully!')
        return redirect('address_list_view')   