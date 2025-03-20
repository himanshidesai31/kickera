from django.views.generic import ListView
from product.models import Category, Product, Checkout, Cart, Confirmation

#Categories class
class  CategoryListView(ListView):
    model = Category
    template_name = 'products/category.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['categories'] = Product.objects.all()
        # context['products_coming'] = Product.objects.all().order_by('?')

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


class  CartListView(ListView):
    model = Cart
    template_name = 'products/cart.html'

    def get_context_data(self, **kwargs):
        context = super(CartListView, self).get_context_data(**kwargs)
        context['cart_items'] = context['object_list']
        return context



class ConfirmationListView(ListView):
    model = Confirmation
    template_name = 'products/confirmation.html'