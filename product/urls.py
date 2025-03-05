from  django.urls import  path
from product.views import CategoryListView, CheckoutListView, CartListView, ConfirmationListView, ProductListView

urlpatterns = [
    path('category/',CategoryListView.as_view(),name='category-list'),
    path('product/',ProductListView.as_view(),name='product-list'),
    path('checkout/',CheckoutListView.as_view(),name='checkout-list'),
    path('cart/',CartListView.as_view(), name='cart-list'),
    path('confirmation/',ConfirmationListView.as_view(),name='confirmation-list'),
]