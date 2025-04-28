#vendor/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView
from vendor.views import SellerRegisterView, VendorDashboardView, SellerLoginView, \
    VendorProductListView, VendorAddProductView, VendorUpdateProductView, VendorDeleteProductView, VendorProfileView, \
    VendorProfileUpdateView, VendorAddBrandView, VendorCategoryAddView, VendorSubCategoryAddView, load_subcategory, \
    VendorOrderListView, VendorChangePasswordView, VendorChangePassworDoneView, VendorOrderReportView

urlpatterns = [
    path('register/', SellerRegisterView.as_view(), name='seller_register'),
    path('login/', SellerLoginView.as_view(), name='seller_login'),

    path('dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('profile/', VendorProfileView.as_view(), name='vendor_profile'),
    path('profile/edit/<int:pk>/', VendorProfileUpdateView.as_view(), name='vendor_profile_update'),
    path('register/success/', TemplateView.as_view(template_name='seller/vendor_register_success.html'), name='vendor_register_success'),

    path('changepassword/',VendorChangePasswordView.as_view(), name='vendor_change_password'),

    path('changepassword-done',VendorChangePassworDoneView.as_view(), name='vendor_change_password_done'),

    #vendor - product related urls
    path('product-list', VendorProductListView.as_view(), name='vendor_product_list'),
    path('add-product',VendorAddProductView.as_view(), name='vendor_add_product'),

    path('edit-product/<int:pk>/',VendorUpdateProductView.as_view(), name='vendor_edit_product'),
    path('delete-product/<int:pk>/',VendorDeleteProductView.as_view(), name='vendor_delete_product'),

    path('brand-add', VendorAddBrandView.as_view(), name='vendor_add_brand'),

    path('add-category', VendorCategoryAddView.as_view(), name='vendor_add_category'),
    path('add-subcategory/', VendorSubCategoryAddView.as_view(), name='vendor_add_subcategory'),

    path('ajax/load-subcategories/', load_subcategory, name='ajax-load-subcategories'),

    path('order-list',VendorOrderListView.as_view(), name='vendor_orders'),

    #vendor can generate the report for it
    path('order-reports',VendorOrderReportView.as_view(), name='vendor_order_report'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
