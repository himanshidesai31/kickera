from django.urls import path
from .views import GenerateReportView, VendorReportView

urlpatterns = [
    path('reports/', GenerateReportView.as_view(), name='generate_report'),
    path('vendor/order-reports/', VendorReportView.as_view(), name='vendor_reports'),
] 