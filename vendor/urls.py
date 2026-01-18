#vendor/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView
from vendor.views import (
    SellerRegisterView, VendorDashboardView, SellerLoginView,
    VendorProductListView, VendorAddProductView, VendorUpdateProductView,
    VendorDeleteProductView, VendorProfileView, VendorProfileUpdateView,
    VendorAddBrandView, VendorCategoryAddView, VendorSubCategoryAddView,
    load_subcategory, VendorOrderListView, VendorChangePasswordView,
    VendorChangePassworDoneView, VendorOrderReportView, VendorReportsView,
    VendorSalesReportView, VendorProductPerformanceReportView,
    VendorInventoryReportView, VendorPaymentReportView,
    VendorCommissionReportView, VendorRefundReportView
)

urlpatterns = [
    # Authentication URLs
    path('register/', SellerRegisterView.as_view(), name='seller_register'),
    path('login/', SellerLoginView.as_view(), name='seller_login'),
    
    # Dashboard URLs
    path('dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('profile/', VendorProfileView.as_view(), name='vendor_profile'),
    path('profile/update/', VendorProfileUpdateView.as_view(), name='vendor_profile_update'),
    path('change-password/', VendorChangePasswordView.as_view(), name='vendor_change_password'),
    path('password-change-done/', VendorChangePassworDoneView.as_view(), name='vendor_change_password_done'),
    
    # Product Management URLs
    path('products/', VendorProductListView.as_view(), name='vendor_products'),
    path('products/add/', VendorAddProductView.as_view(), name='vendor_add_product'),
    path('products/update/<int:pk>/', VendorUpdateProductView.as_view(), name='vendor_update_product'),
    path('products/delete/<int:pk>/', VendorDeleteProductView.as_view(), name='vendor_delete_product'),
    path('add-brand/', VendorAddBrandView.as_view(), name='vendor_add_brand'),
    path('add-category/', VendorCategoryAddView.as_view(), name='vendor_add_category'),
    path('add-subcategory/', VendorSubCategoryAddView.as_view(), name='vendor_add_subcategory'),
    path('load-subcategories/', load_subcategory, name='load_subcategories'),
    
    # Order Management URLs
    path('orders/', VendorOrderListView.as_view(), name='vendor_orders'),
    
    # Report URLs
    path('reports/', VendorReportsView.as_view(), name='vendor_reports'),
    path('reports/sales/', VendorSalesReportView.as_view(), name='vendor_sales_report'),
    path('reports/products/', VendorProductPerformanceReportView.as_view(), name='vendor_product_report'),
    path('reports/inventory/', VendorInventoryReportView.as_view(), name='vendor_inventory_report'),
    path('reports/orders/', VendorOrderReportView.as_view(), name='vendor_order_report'),
    path('reports/payments/', VendorPaymentReportView.as_view(), name='vendor_payment_report'),
    path('reports/commission/', VendorCommissionReportView.as_view(), name='vendor_commission_report'),
    path('reports/refunds/', VendorRefundReportView.as_view(), name='vendor_refund_report'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
