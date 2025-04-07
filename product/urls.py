from  django.urls import  path
from product.views import CategoryListView, CheckoutListView, ConfirmationListView, ProductListView, \
    CartItemAddView, CartListView, CartRemoveView, CheckoutPageView, SelectUserAddressView, CartUpdateView

urlpatterns = [
    path('category/',CategoryListView.as_view(),name='category_list'),
    path('product/',ProductListView.as_view(),name='product_list'),
    path('confirmation/',ConfirmationListView.as_view(),name='confirmation-list'),

    path('cart/',CartListView.as_view(),name='cart_list'),
    path('add-cart/<int:pk>/', CartItemAddView.as_view(), name='cart_add'),
    path('remove-cart/<int:pk>/', CartRemoveView.as_view(), name='cart_remove'),
    path('update-cart/<int:pk>/', CartUpdateView.as_view(), name='cart_update'),
    path('checkout/', CheckoutPageView.as_view(), name='checkout'),

    path('shipinng-address/<int:pk>/', SelectUserAddressView.as_view(), name='check_user_address'),

]