#vendor/urls.py
from django.urls import path
from vendor.views import SellerHomePageView, SellerRegisterView, VendorDashboardView, SellerLoginView

urlpatterns = [
    path('seller/', SellerHomePageView.as_view(), name='seller'),
    path('seller/register/', SellerRegisterView.as_view(), name='seller-register'),
    path('seller/login/', SellerLoginView.as_view(), name='seller-login'),
    path('seller/dashboard/', VendorDashboardView.as_view(), name='vendor-dashboard'),
]
