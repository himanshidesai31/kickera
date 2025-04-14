#vendor/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from vendor.views import SellerHomePageView, SellerRegisterView, VendorDashboardView, SellerLoginView, \
    VendorProductListView, VendorAddProductView, VendorUpdateProductView, VendorDeleteProductView, VendorProfileView, \
    VendorProfileUpdateView, VendorAddBrandView, VendorCategoryAddView
from django.views.generic import TemplateView

urlpatterns = [
    path('seller/', SellerHomePageView.as_view(), name='seller_register'),
    path('seller/register/', SellerRegisterView.as_view(), name='seller_register'),
    path('seller/login/', SellerLoginView.as_view(), name='seller_login'),
    path('seller/dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('seller/profile/', VendorProfileView.as_view(), name='vendor_profile'),
    path('seller/profile/edit/<int:pk>/', VendorProfileUpdateView.as_view(), name='vendor_profile_update'),
    path('seller/register/success/', TemplateView.as_view(template_name='seller/vendor_register_success.html'), name='vendor_register_success'),
    
    #vendor - product related urls
    path('product/product-list', VendorProductListView.as_view(), name='vendor_product_list'),
    path('product/add-product',VendorAddProductView.as_view(), name='vendor_add_product'),
    path('product/edit-product/<int:pk>/',VendorUpdateProductView.as_view(), name='vendor_edit_product'),
    path('product/delete-product/<int:pk>/',VendorDeleteProductView.as_view(), name='vendor_delete_product'),

    path('brand-add', VendorAddBrandView.as_view(), name='vendor_add_brand'),

    path('add-category', VendorCategoryAddView.as_view(), name='vendor_add_category'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
