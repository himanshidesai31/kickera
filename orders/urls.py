from django.urls import path
from orders.views import OrderListView

urlpatterns = [
    path('vendor/order', OrderListView.as_view(), name='my_orders'),
]


