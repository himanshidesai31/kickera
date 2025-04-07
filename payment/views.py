from msilib.schema import ListView

from django.views.generic import TemplateView, DetailView
from payment.models import Payment


# Create your views here.
class PaymentView(TemplateView):
    model = Payment
    template_name = 'payment/payment.html'

    # def get_context_data(self, **kwargs):
    #     context = super(PaymentView, self).get_context_data(**kwargs)
    #     context['payment'] = self.get_object()
    #     return context
    #
    # def get_queryset(self):
    #     return Payment.objects.all()
