from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, View, DetailView
from core.models import Deal
from product.models import Product, Cart, Confirmation, WishList, Category, Brand, SubCategory
from users.forms import AddressForm
from users.models import Address


#Categories class
class CategoryListView(ListView):
    model = Product
    template_name = 'product/category.html'
    context_object_name = 'products'
    paginate_by = 10  #showing the object in  the page you can use the paginate_by = number of page's

    def get_queryset(self):
        queryset = Product.objects.all().prefetch_related('images', 'category', 'brand','subcategory')
        # import pdb; pdb.set_trace()

        #Filter by subcategory
        sub_category_id = self.kwargs.get('sub_category_id')
        if sub_category_id:
            queryset = queryset.filter(subcategory_id=sub_category_id)


        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filter by brand
        brand_id = self.request.GET.get('brand')
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
            
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        #check product price ()
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Filter by product type
        product_type = self.request.GET.get('product_type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)
            
        # Sort results
        sort_by = self.request.GET.get('sort_by', 'name')
        sort_order = self.request.GET.get('sort_order', 'asc')
        
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = queryset.order_by(sort_by)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        
        # Add categories and brands for filter sidebar
        context['categories'] = Category.objects.all()
        context['sub_categories'] = SubCategory.objects.all()
        context['brands'] = Brand.objects.all()
        
        # Add current filter parameters for maintaining state
        context['current_filters'] = self.request.GET.copy()
        
        # Add price ranges
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        
        # Add sort parameters
        context['sort_by'] = self.request.GET.get('sort_by', 'name')
        context['sort_order'] = self.request.GET.get('sort_order', 'asc')
        
        return context


class CheckoutListView(LoginRequiredMixin,ListView):
    model = Cart
    template_name = 'product/checkout.html'


class ConfirmationListView(LoginRequiredMixin,ListView):
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


class CartItemAddView(LoginRequiredMixin,View):
    def post(self, request, pk):
        try:
            product = get_object_or_404(Product, pk=pk)
            cart_item, created = Cart.objects.get_or_create(product=product, user=request.user)

            if not created:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, f'"{product.name}" quantity updated to {cart_item.quantity} in your cart.')
            else:
                messages.success(request, f'"{product.name}" added to your cart successfully.')

        except Exception as e:
            messages.error(request, f"An error occurred while adding the product to the cart: {str(e)}")

        # Check if there's a next parameter in the form or A HTTP_REFERER for redirection
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
        if next_url and 'category' in next_url:
            return redirect(next_url)
        return redirect('cart_list')


class CartRemoveView(LoginRequiredMixin,View):
    def get(self, request, pk):
        try:
            cart_item = get_object_or_404(Cart, pk=pk, user=request.user)
            cart_item.delete()
            messages.success(request, "Product removed from cart successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while removing the product from the cart: {str(e)}")

        return redirect('cart_list')


class CartUpdateView(LoginRequiredMixin,View):
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
    context_object_name = 'wish_list'

    def get_queryset(self):
        return WishList.objects.filter(user=self.request.user).prefetch_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products_in_wishlist = Product.objects.filter(wishlist__user=self.request.user)
        context['products'] = products_in_wishlist
        return context


class AddWishListView(LoginRequiredMixin,View):
    def post(self, request, pk):
        try:
            product = get_object_or_404(Product, pk=pk)
            wish_list, created = WishList.objects.get_or_create(product=product, user=request.user)

            if not created:
                wish_list.quantity += 1
                wish_list.save()
                messages.success(request, f'"{product.name}" quantity updated in your wishlist.')
            else:
                messages.success(request, f'"{product.name}" added to your wishlist successfully.')
        except Exception as e:
            messages.error(request, f"An error occurred while adding the product to the wishlist: {str(e)}")

        # Check if there's a next parameter in the form or A HTTP_REFERER for redirection
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
        if next_url and 'category' in next_url:
            return redirect(next_url)
        return redirect('wishlist')


class RemoveWishListView(View,LoginRequiredMixin):
    def get(self, request, pk):
        try:
            wish_list = get_object_or_404(WishList, pk=pk , user=request.user)
            wish_list.delete()
            messages.success(request, "Product removed from wish-list successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while removing the product: {str(e)}")

        return redirect('wishlist')


class AddAllToCartView(LoginRequiredMixin, View):
    """Add all selected wishlist items to the cart"""
    
    def post(self, request):
        product_ids = request.POST.getlist('product_ids')
        next_url = request.POST.get('next') or reverse_lazy('cart_list')
        
        if not product_ids:
            messages.warning(request, "No products were selected to add to cart.")
            return redirect('wishlist')
        
        added_count = 0
        for product_id in product_ids:
            try:
                product = get_object_or_404(Product, pk=product_id)
                cart_item, created = Cart.objects.get_or_create(product=product, user=request.user)
                
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()
                added_count += 1
            except Exception as e:
                messages.error(request, f"Error adding product #{product_id} to cart: {str(e)}")
        
        if added_count > 0:
            messages.success(request, f"Added {added_count} product(s) to your cart successfully.")
        
        return redirect(next_url)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        if user_id:
            # Get the wishlist items for the use    r
            wishlist_items = WishList.objects.filter(user_id=user_id)
            cart_items = Cart.objects.filter(user_id=user_id)
            context['wishlist_items'] = wishlist_items
            context['cart_items'] = cart_items

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


# Context processor for cart and wishlist counts
def cart_wishlist_count(request):
    context = {
        'cart_count': 0,
        'wishlist_count': 0,
    }
    #It will only show the product number of the user who has added the product to their wish list or cart. also filter the user
    if request.user.is_authenticated:
        context['cart_count'] = Cart.objects.filter(user=request.user).count()
        context['wishlist_count'] = WishList.objects.filter(user=request.user).count()
    return context

# Product Detail View for use or check the product fully details
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.category:
            related_products = Product.objects.filter(category=self.object.category).exclude(id=self.object.id)
            context['related_products'] = related_products
        return context