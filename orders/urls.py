from django.urls import path
from orders.views import OrderListView, UserOrderListView

urlpatterns = [
    path('vendor/order', OrderListView.as_view(), name='my_orders'),
    path('user/orders/', UserOrderListView.as_view(), name='user_orders'),
]


