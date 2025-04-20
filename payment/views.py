import json
import razorpay
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from kickera import settings
from orders.models import Order
from product.models import Product, Cart, WishList

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@method_decorator(csrf_exempt, name='dispatch')
class CreatePaymentView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        try:
            # Get request body data
            body_data = {}
            if request.body:
                body_data = json.loads(request.body)
            
            product = get_object_or_404(Product, pk=product_id)

            if 'cart_total' in body_data and body_data['cart_total']:
                payment_amount = int(float(body_data['cart_total']) * 100)
            else:
                payment_amount = int(product.price * 100)  # Razorpay expects amount in paise
            
            order_data = {
                'amount': payment_amount,
                'currency': "INR",
                'payment_capture': 1,
            }
            razorpay_order = client.order.create(order_data)

            # Get the address from request or use default
            address_id = request.POST.get('address_id')
            address = None
            if address_id:
                try:
                    from users.models import Address
                    address = Address.objects.get(id=address_id, user=request.user)
                except:
                    # If specified address doesn't exist, try to get default address
                    address = request.user.addresses.first()
            else:
                # Try to get default address
                address = request.user.addresses.first()

            order = Order.objects.create(
                user=request.user,
                product=product,
                amount=payment_amount / 100,  # Store in rupees
                razorpay_order_id=razorpay_order['id'],
                address=address,  # Set the address
            )

            wishlist_item_ids = request.GET.getlist('wishlist_item_id')
            if wishlist_item_ids:
                request.session['wishlist_item_ids'] = wishlist_item_ids
            
            return JsonResponse({
                'order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'product_name': product.name,
                'amount': order_data['amount'],
                'razorpay_callback_url': settings.RAZORPAY_CALLBACK_URL,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CreateCallbackView(LoginRequiredMixin, View):
    def post(self, request):
        order_id = request.POST.get('razorpay_order_id')
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')

        print(f"Callback received: order_id={order_id}, payment_id={payment_id}, signature={signature}")

        if order_id and payment_id and signature:
            try:
                order = Order.objects.get(razorpay_order_id=order_id)
                print(f"Found order: {order.id}, is_paid: {order.is_paid}")

                try:
                    client.utility.verify_payment_signature({
                        'razorpay_order_id': order_id,
                        'razorpay_payment_id': payment_id,
                        'razorpay_signature': signature
                    })
                    order.razorpay_payment_id = payment_id
                    order.razorpay_signature = signature
                    order.is_paid = True
                    order.save()
                    
                    print(f"Payment verified successfully. Order {order.id} marked as paid.")
                    
                    # Clear the user's cart after successful payment
                    Cart.objects.filter(user=request.user).delete()
                    
                    # Clear the user's wishlist items that were part of this order
                    wishlist_item_ids = request.session.get('wishlist_item_ids', [])
                    if wishlist_item_ids:
                        WishList.objects.filter(id__in=wishlist_item_ids, user=request.user).delete()
                        del request.session['wishlist_item_ids']
                    
                    # Redirect to confirmation page with order ID
                    return redirect(f'/product/confirmation/?order_id={order.id}')
                except razorpay.errors.SignatureVerificationError:
                    print(f"Payment signature verification failed for order {order.id}")
                    order.is_paid = False
                    order.save()
                    return redirect('/product/confirmation/')
            except Order.DoesNotExist:
                print(f"Order not found with razorpay_order_id: {order_id}")
                return redirect('/product/confirmation/')
        else:
            print("Missing payment parameters")
            return redirect('/product/confirmation/')