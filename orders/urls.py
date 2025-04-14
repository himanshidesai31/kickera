from django.urls import path
from orders.views import OrderListView

urlpatterns = [
    path('my_orders/', OrderListView.as_view(), name='my_orders'),
]


