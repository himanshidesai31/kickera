from http.client import responses

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from core.models import  Banner, Deal, Brand
from product.models import Product
from django.views.generic import TemplateView, UpdateView, DetailView
from django.contrib.auth.views import PasswordChangeView
from allauth.account.views import ReauthenticateView
from orders.models import Order

class HomePageView(TemplateView):
    template_name = 'index.html'
    #this is  use for showing the all product's  when the vendor has been added in to the there product list
    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        banners = Banner.objects.all().order_by('sort_order')
        context['banners'] = banners
        context['products_latest'] = Product.objects.filter(product_type='latest')
        context['products_coming'] = Product.objects.filter(product_type='coming')
        context['deals'] = Deal.objects.all()
        context['brands'] = Brand.objects.all()
        return context

class ConfirmationPageView(LoginRequiredMixin, TemplateView):
    template_name = 'product/confirmation.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('test') == 'true':
            from product.models import Product
            try:
                product = Product.objects.first()
                if product:
                    from orders.models import Order
                    order = Order.objects.create(
                        user=request.user,
                        product=product,
                        amount=product.price,
                        is_paid=True,
                        razorpay_order_id='test_order_id',
                        razorpay_payment_id='test_payment_id',
                        razorpay_signature='test_signature'
                    )
                    print(f"Created test order: {order.id}")
                    from django.shortcuts import redirect
                    return redirect(f'/product/confirmation/?order_id={order.id}')
            except Exception as e:
                print(f"Error creating test order: {e}")

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order_id = self.request.GET.get('order_id') or self.request.POST.get('order_id')
        print(f"ConfirmationPageView: order_id from request: {order_id}")
        print(f"ConfirmationPageView: user: {self.request.user}")

        if order_id:
            # Try to get the specific order
            try:
                order = Order.objects.get(
                    id=order_id,
                    user=self.request.user,
                    is_paid=True
                )
                print(f"ConfirmationPageView: Found order: {order.id}, is_paid: {order.is_paid}")
            except Order.DoesNotExist:
                print(f"ConfirmationPageView: Order not found with id {order_id}")
                order = None
        else:
            # Fallback to latest paid order if no order_id provided
            order = Order.objects.filter(
                user=self.request.user,
                is_paid=True
            ).order_by('-id').first()
            print(f"ConfirmationPageView: Latest paid order: {order.id if order else None}")

        context['order'] = order
        return context


class AboutPageView(LoginRequiredMixin, TemplateView):
    template_name = 'about.html'

class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'account/password_change.html'
    success_url = reverse_lazy('account_reauthenticate')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been updated!')
        return super(PasswordChangeView, self).form_valid(form)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Please correct the error below.')
        return response

class ReauthenticateView(LoginRequiredMixin, ReauthenticateView):
    template_name = 'account/reauthenticate.html'
    success_url = reverse_lazy('account_change_password_done')

    def form_valid(self, form):
        responses = super().form_valid(form)
        messages.success(self.request, 'Your password has been updated!')
        return responses

    def form_invalid(self, form):
        responses = super().form_invalid(form)
        messages.error(self.request, 'Please correct the error below.')
        return responses