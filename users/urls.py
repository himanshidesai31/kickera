#this  is urls.py
from django.urls import path
from users.views import ProfileView, AddressListView, Add_AddressListView, UpdateAddressView, DeleteAddressView, \
    UpdateProfileView, custom_login_redirect

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile-update/<int:pk>/', UpdateProfileView.as_view(), name='update_profile'),
    path('list-address', AddressListView.as_view(), name='address_list_view'),
    path('add-address',Add_AddressListView.as_view(), name='add_address_view'),
    path('update-address/<int:pk>/',UpdateAddressView.as_view(), name='update_address_view'),
    path('delete-address/<int:pk>/',DeleteAddressView.as_view(),  name='delete_address_view'),
    path('login-redirect/', custom_login_redirect, name='custom_login_redirect'),
]