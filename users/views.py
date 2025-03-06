from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserUpdateForm
from .models import User

class ProfileView(LoginRequiredMixin,UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user/profile.html'
    success_url = reverse_lazy('profile')  # Redirect after successful update

    def form_valid(self, form):
        reponse = super(ProfileView, self).form_valid(form)
        print('-------------------valide form')
        messages.success(self.request, 'Profile updated successfully')
        return reponse

    def form_invalid(self, form):
        print('--------------------invalide')
        messages.error(self.request, 'Something went wrong , Invalid Form Submission')
        return super(ProfileView,self).form_invalid(form)

    def get_object(self, queryset=None):
        """Return the currently logged-in user as the object to update"""
        return self.request.user

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data( **kwargs)
    #     context['user'] = self.request.user
    #     return context