from django.urls import path
from core.views import (
    HomePageView,
    BlogPageView,
    SingleBlogPageView,
    SingleProductPageView,
    CheckoutPageView,
    CartPageView,
    ConfirmationPageView,
    TrackingPageView,
    ElementPageView,
    AboutPageView,
    WishlistPageView,

)

urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('blog/', BlogPageView.as_view(), name='blog'),
    path('single-blog/', SingleBlogPageView.as_view(), name='single_blog'),
    path('product/', SingleProductPageView.as_view(), name='single_product'),
    path('checkout/', CheckoutPageView.as_view(), name='checkout'),
    path('cart/', CartPageView.as_view(), name='cart'),
    path('confirmation/', ConfirmationPageView.as_view(), name='confirmation'),
    path('tracking/', TrackingPageView.as_view(), name='tracking'),
    path('elements/', ElementPageView.as_view(), name='elements'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('wishlist/', WishlistPageView.as_view(), name='wishlist'),


]
