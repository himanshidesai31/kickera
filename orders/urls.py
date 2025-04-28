from django.urls import path
from orders.views import OrderListView, UserOrderListView, generate_report, vendor_report_view

urlpatterns = [
    path('vendor/orders/', OrderListView.as_view(), name='my_orders'),
    path('user/orders/', UserOrderListView.as_view(), name='user_orders'),
    path('reports/', generate_report, name='generate_report'),
    path('vendor/order-reports/', vendor_report_view, name='vendor_reports'),
]


