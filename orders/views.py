from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from orders.models import Order

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Return only the orders of the logged-in user
        return Order.objects.filter(user=self.request.user).prefetch_related('product', 'product__images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(user=self.request.user)
        return context

#user view for order list
class UserOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/user_order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Return orders with prefetched related data including user addresses
        return Order.objects.filter(user=self.request.user).select_related('address', 'user').prefetch_related(
            'product', 
            'product__images',
            'user__addresses'
        )
