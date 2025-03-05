from  django.urls import  path
from users.views import UserAddressView
urlpatterns = [
   path('', UserAddressView.as_view()),
]