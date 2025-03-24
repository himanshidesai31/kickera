#this  is urls.py
from django.urls import path
from users.views import ProfileView, AddressListView, Add_AddressListView, UpdateAddressView, DeleteAddressView

urlpatterns = [
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('list-address', AddressListView.as_view(), name='address_list_view'),
    path('add-address',Add_AddressListView.as_view(), name='add_address_view'),
    path('update-address/<int:pk>/',UpdateAddressView.as_view(), name='update_address_view'),
    path('delete-address/<int:pk>/',DeleteAddressView.as_view(),  name='delete_address_view'),

]