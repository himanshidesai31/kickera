from django.urls import path
from payment.views import CreatePaymentView, CreateCallbackView

urlpatterns = [
    path('create-payment/<int:product_id>/', CreatePaymentView.as_view(), name='payment'),
    path('callback/', CreateCallbackView.as_view(), name='payment_callback'),
]

