from django.views.generic import ListView, TemplateView
from product.models import  Product, Checkout, Cart, Confirmation, CartItem
from vendor.views import VendorProductListView


#Categories class
class  CategoryListView(ListView):
    model = Product
    template_name = 'product/category.html'

    def get_queryset(self):
        return Product.objects.all().prefetch_related('category')

#Products class
class ProductListView(ListView):
    model = Product
    template_name = 'index.html'

    def get_queryset(self):
        return Product.objects.all().prefetch_related('images')
        # return Product.objects.filter(user__admin=self.request.user).prefetch_related('images')


class  CheckoutListView(ListView):
    model = Checkout
    template_name = 'product/checkout.html'


class ConfirmationListView(ListView):
    model = Confirmation
    template_name = 'product/confirmation.html'


class CartListView(ListView):
    model = Cart
    template_name = 'product/cart.html'

    def get_context_data(self, **kwargs):
        context = super(CartListView, self).get_context_data(**kwargs)
        user_cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart_items'] = CartItem.objects.filter(cart=user_cart)
        context['cart_subtotal'] = sum(item.price * item.quantity for item in context['cart_items'])
        return context

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

class CartItemListView(ListView):
                model = CartItem
                template_name = 'product/cart_items.html'

                def get_context_data(self, **kwargs):
                    context = super(CartItemListView, self).get_context_data(**kwargs)
                    user_cart, created = Cart.objects.get_or_create(user=self.request.user)
                    context['cart_items'] = CartItem.objects.filter(cart=user_cart)
                    context['cart_subtotal'] = sum(item.cart.product.price * item.quantity for item in context['cart_items'])
                    return context
                
                