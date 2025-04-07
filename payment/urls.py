from django.urls import path
from payment.views import PaymentView

urlpatterns = [
    path('product/payment',PaymentView.as_view(),name='payment'),

]