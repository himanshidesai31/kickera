from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View, UpdateView
from core.models import Deal
from product.models import Product, Cart, Confirmation, WishList
from users.forms import AddressForm
from users.models import Address


#Categories class
class  CategoryListView(ListView):
    model = Product
    template_name = 'product/category.html'

    def get_queryset(self):
        return Product.objects.all().prefetch_related('category')

#Products class
class ProductListView(ListView):
    model = Product
    template_name = 'product/single_product.html'

    def get_queryset(self):
        return Product.objects.all().prefetch_related('images')



class CheckoutListView(ListView):
    model = Cart
    template_name = 'product/checkout.html'


class ConfirmationListView(ListView):
    model = Confirmation
    template_name = 'product/confirmation.html'


class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'product/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_total'] = sum(item.total_price for item in self.get_queryset())
        return context


class CartItemAddView(View):
    def post(self, request, pk):
        try:
            product = get_object_or_404(Product, pk=pk)
            cart_item, created = Cart.objects.get_or_create(product=product, user=request.user)

            if not created:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, "Your product quantity has been updated in the cart.")
            else:
                messages.success(request, "Product added to cart successfully.")

        except Exception as e:
            messages.error(request, f"An error occurred while adding the product to the cart: {str(e)}")

        return redirect('cart_list')


class CartRemoveView(View):
    def get(self, request, pk):
        try:
            cart_item = get_object_or_404(Cart, pk=pk, user=request.user)
            cart_item.delete()
            messages.success(request, "Product removed from cart successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while removing the product from the cart: {str(e)}")

        return redirect('cart_list')


class CartUpdateView(View):
    def post(self, request, pk):
        try:
            cart_item = get_object_or_404(Cart, pk=pk, user=request.user)
            new_quantity = int(request.POST.get('quantity', 1))
            
            if new_quantity <= 0:
                cart_item.delete()
                messages.success(request, "Product removed from cart successfully.")
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, "Cart quantity updated successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while updating the cart: {str(e)}")
        
        return redirect('cart_list')


class WishListView(LoginRequiredMixin, ListView):
    model = WishList
    template_name = 'product/wishlist.html'

    def get_queryset(self):
        return WishList.objects.all().prefetch_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wish_list'] = WishList.objects.all()
        return context

class AddWishListView(View):
    def post(self, request, pk):
        try:
            product = get_object_or_404(Product, pk=pk)
            wish_list,created = WishList.objects.get_or_create(product=product, user=request.user)

            if not created:
                wish_list.quantity += 1
                wish_list.save()
                messages.success(request, "Product Quantity added to wish list successfully.")
            else:
                messages.success(request, "Product added to wishlist successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while adding the product to the wishlist: {str(e)}")

        return redirect('wishlist')


class RemoveWishListView(View):
    def get(self, request, pk):
        try:
            wish_list = get_object_or_404(WishList, pk=pk , user=request.user)
            wish_list.delete()
            messages.success(request, "Product  removed from wish-list successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while removing the product: {str(e)}")

        return redirect('wishlist')

class CheckoutPageView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = 'cart_items'
    template_name = 'product/checkout.html'
    success_url = reverse_lazy('checkout')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get items from cart
        cart_items = self.get_queryset()
        cart_total = sum(item.product.price * item.quantity for item in cart_items)
        
        # Check if there are wishlist items in request
        wishlist_item_ids = self.request.GET.getlist('wishlist_item_id')
        wishlist_items = []
        wishlist_total = 0
        
        if wishlist_item_ids:
            # Get wishlist items
            wishlist_items = WishList.objects.filter(
                id__in=wishlist_item_ids,
                user=self.request.user
            )
            wishlist_total = sum(item.product.price for item in wishlist_items)
            
        # Get selected address
        address_id = self.request.GET.get('address_id')
        selected_address = None
        if address_id:
            try:
                selected_address = Address.objects.get(id=address_id, user=self.request.user)
            except Address.DoesNotExist:
                pass
                
        # Calculate total price (cart + wishlist)
        total_price = cart_total + wishlist_total
        
        # Update context with all information
        context.update({
            'cart_items': cart_items,
            'wishlist_items': wishlist_items,
            'total_price': total_price,
            'selected_address': selected_address,
        })
        
        return context

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class SelectUserAddressView(ListView):
    model = Address
    form_class = AddressForm
    template_name = 'product/user_checkout_address.html'
    context_object_name = 'address'
    success_url = reverse_lazy('checkout')

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        return get_object_or_404(Address, user=self.request.user)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        if user_id:
            # Get the wishlist items for the user
            wishlist_items = WishList.objects.filter(user_id=user_id)
            context['wishlist_items'] = wishlist_items
            
            # Calculate total price
            total_price = sum(item.product.price for item in wishlist_items)
            context['total_price'] = total_price
        return context


class DealListView(ListView):
    model = Deal
    template_name = 'index.html'
    context_object_name = 'deals'

    def get_queryset(self):
        return Deal.objects.all()
