from django.views.generic import ListView
from orders.models import Order

class OrderListView(ListView):
    model = Order
    template_name = 'order/order_list.html'

    def get_queryset(self):
        return Order.objects.all().prefetch_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.all()
        return context