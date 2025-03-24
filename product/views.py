from django.views.generic import ListView
from product.models import Category, Product, Checkout, Cart, Confirmation, CartItem


#Categories class
class  CategoryListView(ListView):
    model = Category
    template_name = 'products/category.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['categories'] = Product.objects.all()
        return context



class  ProductListView(ListView):
    model = Product
    template_name = 'index.html'

    def get_context_data(self,  **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['all_products'] = context['object_list']
        return context
                    
    
class  CheckoutListView(ListView):
    model = Checkout
    template_name = 'products/checkout.html'


class ConfirmationListView(ListView):
    model = Confirmation
    template_name = 'products/confirmation.html'



class CartListView(ListView):
    model = Cart
    template_name = 'products/cart.html'

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
                template_name = 'products/cart_items.html'

                def get_context_data(self, **kwargs):
                    context = super(CartItemListView, self).get_context_data(**kwargs)
                    user_cart, created = Cart.objects.get_or_create(user=self.request.user)
                    context['cart_items'] = CartItem.objects.filter(cart=user_cart)
                    context['cart_subtotal'] = sum(item.cart.product.price * item.quantity for item in context['cart_items'])
                    return context