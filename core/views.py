from django.contrib import messages 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from core.models import Product, Banner, Deal, Brand
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordChangeView

class HomePageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        banners = Banner.objects.all().order_by('sort_order')
        print(banners)  # Debugging statement
        context['banners'] = banners
        # context['categories'] = Category.objects.all()
        context['products_latest'] = Product.objects.filter(product_type='latest')
        context['products_coming'] = Product.objects.filter(product_type='coming')
        context['deals'] = Deal.objects.all()
        context['brands'] = Brand.objects.all()
        return context


class BlogPageView(LoginRequiredMixin, TemplateView):
    template_name = 'products/blog.html'


class SingleBlogPageView(LoginRequiredMixin, TemplateView):
    template_name = 'products/single_blog.html'


class SingleProductPageView(LoginRequiredMixin, TemplateView):
    template_name = 'products/single_product.html'


class CheckoutPageView(LoginRequiredMixin, TemplateView):
    template_name = 'products/checkout.html'



class ConfirmationPageView(LoginRequiredMixin, TemplateView):
    template_name = 'products/confirmation.html'


class TrackingPageView(LoginRequiredMixin, TemplateView):
    template_name = 'products/tracking.html'


class ElementPageView(LoginRequiredMixin, TemplateView):
    template_name = 'products/elements.html'


class AboutPageView(LoginRequiredMixin, TemplateView):
    template_name = 'about.html'


class WishlistPageView(LoginRequiredMixin, TemplateView):
    template_name = 'products/wishlist.html'
    
    
class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('account_change_password_done')
    template_name = 'account/password_change.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Something went wrong, Invalid Form Submission, Please fill the form correctly')
        return response