from django.views.generic import TemplateView
from users.models import Address


# Create your views here.
#login view
class UserAddressView(TemplateView):
    model = Address
    template_name = 'user/profile.html'
