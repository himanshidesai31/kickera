import json
import razorpay
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from kickera import settings
from orders.models import Order
from product.models import Product, Cart, WishList

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@method_decorator(csrf_exempt, name='dispatch')
class CreatePaymentView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        try:
            # Get request body data
            body_data = json.loads(request.body) if request.body else {}
            
            # Get the product
            product = get_object_or_404(Product, pk=product_id)

            # Calculate payment amount
            if 'cart_total' in body_data and body_data['cart_total']:
                payment_amount = int(float(body_data['cart_total']) * 100)
            else:
                payment_amount = int(product.price * 100)  # Razorpay expects amount in paise
            
            # Validate payment amount
            if payment_amount <= 0:
                return JsonResponse({'error': 'Invalid payment amount'}, status=400)

            # Create Razorpay order
            order_data = {
                'amount': payment_amount,
                'currency': "INR",
                'receipt': f"order_{product_id}_{request.user.id}"
            }
            
            razorpay_order = client.order.create(order_data)
            
            # Get address from request
            address_id = body_data.get('address_id') or request.GET.get('address_id')
            if not address_id:
                return JsonResponse({'error': 'Delivery address is required'}, status=400)

            try:
                from users.models import Address
                address = Address.objects.get(id=address_id, user=request.user)
            except Address.DoesNotExist:
                return JsonResponse({'error': 'Invalid delivery address'}, status=400)

            # Create order in database
            order = Order.objects.create(
                user=request.user,
                product=product,
                amount=payment_amount / 100,  # Store in rupees
                razorpay_order_id=razorpay_order['id'],
                address=address,
            )

            # Store wishlist items in session if present
            wishlist_item_ids = request.GET.getlist('wishlist_item_id')
            if wishlist_item_ids:
                request.session['wishlist_item_ids'] = wishlist_item_ids
            
            return JsonResponse({
                'order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'product_name': product.name,
                'amount': payment_amount,
                'razorpay_callback_url': settings.RAZORPAY_CALLBACK_URL,
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CreateCallbackView(View):
    def get(self, request):
        # Handle GET request from Razorpay (as seen in your URL)
        order_id = request.GET.get('razorpay_order_id')
        payment_id = request.GET.get('razorpay_payment_id')
        signature = request.GET.get('razorpay_signature')
        
        print(f"Payment callback GET: order_id={order_id}, payment_id={payment_id}")
        return self._process_payment(request, order_id, payment_id, signature)
    
    def post(self, request):
        # Handle POST request (original method)
        order_id = request.POST.get('razorpay_order_id')
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')
        
        print(f"Payment callback POST: order_id={order_id}, payment_id={payment_id}")
        return self._process_payment(request, order_id, payment_id, signature)
    
    def _process_payment(self, request, order_id, payment_id, signature):
        if order_id and payment_id and signature:
            try:
                # Get the order
                order = Order.objects.get(razorpay_order_id=order_id)
                print(f"Processing payment for order: {order.id}, current is_paid: {order.is_paid}")
                
                # Verify signature
                params_dict = {
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                }
                
                try:
                    # Verify the payment signature
                    client.utility.verify_payment_signature(params_dict)
                    print(f"Payment signature verified for order: {order.id}")
                    
                    # Mark order as paid
                    order.razorpay_payment_id = payment_id
                    order.razorpay_signature = signature
                    order.is_paid = 'Completed'  # Make sure this is a string value
                    order.save()
                    print(f"Order {order.id} saved as paid (Completed)")
                    
                    # Clear cart items if user is authenticated
                    if request.user.is_authenticated:
                        Cart.objects.filter(user=request.user).delete()
                        print(f"Cart items deleted for user: {request.user.id}")
                    
                    # Clear wishlist items if present
                    wishlist_item_ids = request.session.get('wishlist_item_ids', [])
                    if wishlist_item_ids and request.user.is_authenticated:
                        WishList.objects.filter(id__in=wishlist_item_ids, user=request.user).delete()
                        if 'wishlist_item_ids' in request.session:
                            del request.session['wishlist_item_ids']
                        print(f"Wishlist items deleted: {wishlist_item_ids}")
                    
                except Exception as e:
                    # Log the exception
                    print(f"Payment verification failed: {str(e)}")
                
                # Redirect to confirmation page
                redirect_url = f'/product/confirmation/?order_id={order.id}'
                print(f"Redirecting to: {redirect_url}")
                return redirect(redirect_url)
                
            except Order.DoesNotExist:
                print(f"Order not found with razorpay_order_id: {order_id}")
                return redirect('/product/confirmation/')
            except Exception as e:
                # Log the exception
                print(f"Payment callback error: {str(e)}")
                return redirect('/product/confirmation/')
        else:
            print("Missing required payment parameters")
            return redirect('/product/confirmation/')