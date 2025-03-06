from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from core.models import Product, Banner, Deal, Brand

class HomePageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['banners'] = Banner.objects.all().order_by('sort_order')
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


class CartPageView(LoginRequiredMixin, TemplateView):
    template_name = 'products/cart.html'


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
