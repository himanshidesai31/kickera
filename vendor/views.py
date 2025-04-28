# vendor/views.py
from allauth.headless.account.views import ChangePasswordView
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, TemplateView, UpdateView, DetailView, FormView
from orders.models import Order
from product.models import Product, Image, Category, Brand, SubCategory
from vendor.models import VendorProfile, VendorRequest
from vendor.forms import  SellerRegisterForm, VendorAddProductForm, VendorAddBrandForm, VendorAddCategoryForm, VendorProfileForm, VendorLoginForm, VendorAddSubCategoryForm
from django.views.generic.edit import CreateView
from users.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.hashers import make_password
# Import for report generation
from django.http import HttpResponse
import csv
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
import calendar
from io import BytesIO
from django.template.loader import get_template
from django.views import View
import json
from collections import Counter
from django.utils import timezone
# Make sure to install these packages:
# pip install xhtml2pdf reportlab

try:
    # For PDF generation
    from xhtml2pdf import pisa
except ImportError:
    pisa = None


class SellerRegisterView(FormView):#without using the model form i can used the FormView for this is Inquery
    template_name = 'seller/seller_register.html'
    form_class = SellerRegisterForm
    success_url = reverse_lazy('vendor_register_success')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        
        # Check if a vendor request with this email already exists
        existing_request = VendorRequest.objects.filter(email=email).exists()
        if existing_request:
            messages.error(self.request, "A vendor request with this email already exists and is pending approval.")
            return self.form_invalid(form)
            
        # Check if user already exists - we'll still create a vendor request
        user_exists = User.objects.filter(email=email).exists()
        
        # Create VendorRequest with hashed password
        vendor_request = VendorRequest.objects.create(
            business_name=form.cleaned_data['business_name'],
            phone_number=form.cleaned_data['phone_number'],
            email=email,
            gst_no=form.cleaned_data.get('gst_no'),
            tax_id=form.cleaned_data.get('tax_id'),
            business_registration_number=form.cleaned_data.get('business_registration_number'),
            logo=form.cleaned_data.get('logo'),
            status="pending",
            password=make_password(form.cleaned_data['password'])  # Store hashed password
        )
        
        # If user is authenticated, link this vendor request to them
        if self.request.user.is_authenticated and self.request.user.email == email:
            vendor_request.user = self.request.user
            vendor_request.save()
        
        # Try to send emails to admin
        try:
            admin_emails = [admin.email for admin in User.objects.filter(is_superuser=True) if admin.email]
            if admin_emails:
                send_mail(
                    subject='New Vendor Registration Request',
                    message=f"A new vendor '{form.cleaned_data['business_name']}' has registered and is awaiting approval.",
                    from_email=email,
                    recipient_list=admin_emails,
                    fail_silently=True,
                )
        except Exception:
            print('Something went wrong sending email to admin')
            
        # Try to send confirmation email to user
        try:
            send_mail(
                subject='Vendor Registration Request Received',
                message=(
                    f"Thank you for applying to become a vendor at KickEra. "
                    f"Your application for '{form.cleaned_data['business_name']}' is under review. "
                    f"You will receive an email when your application is approved or rejected."
                ),
                from_email=None,  # Use DEFAULT_FROM_EMAIL
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            print('Error sending confirmation email')
            
        if user_exists:
            messages.success(self.request, "Your vendor application has been submitted successfully. Since you already have an account, we've linked this request to your account. You will be notified once it is reviewed.")
        else:
            messages.success(self.request, "Your vendor application has been submitted successfully. You will be notified once it is reviewed.")
            
        return super().form_valid(form)


class VendorProfileView(LoginRequiredMixin, DetailView):
    model = VendorProfile
    template_name = 'seller/vendor_profile.html'
    context_object_name = 'vendor'

    def get_object(self, queryset=None):
        return get_object_or_404(VendorProfile, user=self.request.user)


class VendorProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = VendorProfile
    form_class = VendorProfileForm
    template_name = 'seller/vendor_profile_edit.html'
    success_url = reverse_lazy('vendor_profile')

    def get_object(self, queryset=None):
        return get_object_or_404(VendorProfile, user=self.request.user)


class SellerLoginView(LoginView):
    template_name = 'seller/seller_login.html'
    form_class = VendorLoginForm
    success_url = reverse_lazy('vendor_dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Set the user as a vendor if they're not already
        user = self.request.user
        if not user.is_vendor:
            # Check if they have a vendor profile
            vendor_profile = VendorProfile.objects.filter(user=user).exists()
            if vendor_profile:
                user.is_vendor = True
                user.save()
                print(f'User {user.email} is now marked as a vendor')
            
        return response
        
    def form_invalid(self, form):
        print('------------form is invalid----------')
        return super().form_invalid(form)
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return self.success_url


class VendorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'seller/vendor_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add vendor status information
        user = self.request.user
        
        try:
            vendor_profile = VendorProfile.objects.get(user=user)
            context['vendor_profile'] = vendor_profile
            
            # Get product statistics
            products_count = Product.objects.filter(vendor=vendor_profile).count()
            context['products_count'] = products_count
            
            # Get order statistics
            orders = Order.objects.filter(product__vendor=vendor_profile)
            context['orders_count'] = orders.count()
            
            # Calculate total sales
            total_sales = orders.filter(is_paid='Completed').aggregate(Sum('amount'))['amount__sum'] or 0
            context['total_sales'] = total_sales
            
            # Get pending orders
            pending_orders = orders.filter(is_paid='Pending').count()
            context['pending_orders'] = pending_orders
            
            # Get recent orders (last 5)
            recent_orders = orders.order_by('-created_at')[:5]
            context['recent_orders'] = recent_orders
            
            # Count orders by status
            orders_by_status = {}
            for status_choice in Order.payment_status:
                status = status_choice[0]
                count = orders.filter(is_paid=status).count()
                orders_by_status[status] = count
            context['orders_by_status'] = orders_by_status
            
            # Get monthly sales data for the current year
            current_year = datetime.now().year
            monthly_sales = []
            
            for month in range(1, 13):
                month_start = datetime(current_year, month, 1)
                if month == 12:
                    month_end = datetime(current_year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = datetime(current_year, month + 1, 1) - timedelta(days=1)
                
                month_sales = orders.filter(
                    created_at__gte=month_start,
                    created_at__lte=month_end,
                    is_paid='Completed'
                ).aggregate(Sum('amount'))['amount__sum'] or 0
                
                monthly_sales.append(month_sales)
            
            context['monthly_sales'] = monthly_sales
            
        except VendorProfile.DoesNotExist:
            context['vendor_profile'] = None
            
        try:
            context['vendor_request'] = VendorRequest.objects.get(user=user)
        except VendorRequest.DoesNotExist:
            context['vendor_request'] = None
            
        return context


class VendorProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'seller/vendor_product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(vendor__user=self.request.user).select_related('vendor').prefetch_related('images')



class VendorAddProductView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'seller/vendor_add_products.html'
    form_class = VendorAddProductForm
    success_url = reverse_lazy('vendor_product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Load categories and print debug info
        categories = Category.objects.all()
        print(f"Categories count: {categories.count()}")
        for cat in categories:
            print(f"- Category: {cat.category_name} (ID: {cat.id})")
        context['categories'] = categories

        # Load brands
        context['brands'] = Brand.objects.all()

        # Load all subcategories and print debug info
        subcategories = SubCategory.objects.all()

        # Group subcategories by category for easy filtering in template
        subcategories_by_category = {}
        for cat in categories:
            subcategories_by_category[cat.id] = SubCategory.objects.filter(category=cat)

        context['subcategories'] = subcategories
        context['subcategories_by_category'] = subcategories_by_category

        print(f"Subcategories count: {subcategories.count()}")
        for subcat in subcategories:
            cat_name = subcat.category.category_name
            cat_id = subcat.category.id
            print(f"- All the Subcategory: {subcat.sub_category_name} (ID: {subcat.id}) - Category: {cat_name} (ID: {cat_id})")

        return context


    def form_valid(self, form):
        product = form.save(commit=False)
        product.vendor = self.request.user.vendor_profile
        product.save()

        images = self.request.FILES.getlist('images')
        for img in images:
            Image.objects.create(product=product, image=img)

        return redirect(self.success_url)


class VendorUpdateProductView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'seller/vendor_edit_product.html'
    form_class = VendorAddProductForm
    success_url = reverse_lazy('vendor_product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['product_images'] = self.object.images.all()
        
        # Load all subcategories 
        subcategories = SubCategory.objects.all()
        context['subcategories'] = subcategories
        
        return context

    def form_valid(self, form):
        product = form.save(commit=False)
        product.vendor = self.request.user.vendor_profile
        product.save()

        images = self.request.FILES.getlist('images')
        if images:
            product.images.all().delete()
            for img in images:
                Image.objects.create(product=product, image=img)

        return super().form_valid(form)


class VendorDeleteProductView(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('vendor_product_list')

    def get_queryset(self):
        return Product.objects.filter(vendor__user=self.request.user)


class VendorAddBrandView(LoginRequiredMixin, CreateView):
    model = Brand
    template_name = 'seller/vendor_add_brand.html'
    form_class = VendorAddBrandForm
    success_url = reverse_lazy('vendor_add_brand')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        return context


class VendorCategoryAddView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'seller/vendor_add_category.html'
    form_class = VendorAddCategoryForm
    success_url = reverse_lazy('vendor_add_category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        print('-------form  valid-----')
        return super().form_valid(form)

    def form_invalid(self, form):
        print('-------form  invalid-----')
        return super().form_invalid(form)


class VendorSubCategoryAddView(LoginRequiredMixin, CreateView):
    model = SubCategory
    template_name = 'seller/vendor_add_subcategory.html'
    form_class = VendorAddSubCategoryForm
    success_url = reverse_lazy('vendor_add_subcategory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subcategories'] = SubCategory.objects.all().select_related('category')
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        print('-------form valid-----')
        # Get the category from form data
        subcategory = form.save(commit=False)
        
        # Double-check that category is set
        if not subcategory.category_id and form.cleaned_data.get('category'):
            subcategory.category = form.cleaned_data.get('category')
            
        # Save the subcategory
        subcategory.save()
        
        # Show confirmation message
        messages.success(self.request, f'Subcategory "{subcategory.sub_category_name}" added to category "{subcategory.category.category_name}"')
        
        return super().form_valid(form)

    def form_invalid(self, form):
        print('-------form invalid-----')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error in {field}: {error}")
        return super().form_invalid(form)


#use for loading the subcategory list related there categories name's
def load_subcategory(request):
    category_id = request.GET.get('category_id')
    sub_categories = SubCategory.objects.filter(category_id=category_id).order_by('sub_category_name')
    return render(request, 'product/subcategory_dropdown_list_options.html', {
        'sub_categories': sub_categories
    })


class VendorOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'seller/vendor_order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        try:
            vendor_profile = self.request.user.vendor_profile
            return Order.objects.filter(
                product__vendor=vendor_profile
            ).order_by('-created_at')
        except VendorProfile.DoesNotExist:
            return Order.objects.none()


class VendorOrderReportView(LoginRequiredMixin, View):
    template_name = 'seller/vendor_order_report.html'

    def get(self, request, *args, **kwargs):
        try:
            vendor_profile = request.user.vendor_profile
            # Get all orders for this vendor
            orders = Order.objects.filter(
                product__vendor=vendor_profile
            ).select_related('product', 'user').order_by('-created_at')

            # Calculate statistics
            total_amount = orders.aggregate(Sum('amount'))['amount__sum'] or 0
            total_orders = orders.count()
            
            # Get payment and delivery stats
            payment_stats = dict(Counter(order.is_paid for order in orders))
            delivery_stats = dict(Counter(order.order_status for order in orders))

            context = {
                'orders': orders,
                'total_amount': total_amount,
                'total_orders': total_orders,
                'payment_stats': payment_stats,
                'delivery_stats': delivery_stats,
                'current_year': timezone.now().year,
                'current_month': timezone.now().month,
            }
            return render(request, self.template_name, context)
            
        except VendorProfile.DoesNotExist:
            messages.error(request, "Vendor profile not found.")
            return redirect('vendor_dashboard')

    def post(self, request, *args, **kwargs):
        report_type = request.POST.get('report_type', 'all')
        report_format = request.POST.get('format', 'pdf')

        try:
            vendor_profile = request.user.vendor_profile
        except VendorProfile.DoesNotExist:
            messages.error(request, "Vendor profile not found.")
            return redirect('vendor_dashboard')

        # Base query
        orders = Order.objects.filter(product__vendor=vendor_profile)

        # Apply date filters and prepare context
        context = {
            'vendor': vendor_profile,
            'report_date': timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        if report_type == 'monthly':
            month = int(request.POST.get('month', timezone.now().month))
            year = int(request.POST.get('year_monthly', timezone.now().year))
            
            # Get month name
            month_name = calendar.month_name[month]
            
            # Calculate date range for the month
            last_day = calendar.monthrange(year, month)[1]
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, last_day) + timedelta(days=1)
            
            # Filter orders for the month
            orders = orders.filter(created_at__gte=start_date, created_at__lt=end_date)
            
            # Calculate statistics
            total_amount = orders.aggregate(Sum('amount'))['amount__sum'] or 0
            order_count = orders.count()
            average_order_value = round(total_amount / order_count, 2) if order_count > 0 else 0
            
            # Payment and delivery statistics
            payment_stats = dict(Counter(order.is_paid for order in orders))
            delivery_stats = dict(Counter(order.order_status for order in orders))
            
            # Daily order counts
            daily_orders = {}
            for day in range(1, last_day + 1):
                date = datetime(year, month, day)
                count = orders.filter(created_at__date=date).count()
                daily_orders[day] = count
            
            # Update context with monthly specific data
            context.update({
                'month_name': month_name,
                'year': year,
                'orders': orders,
                'total_amount': total_amount,
                'average_order_value': average_order_value,
                'payment_stats': payment_stats,
                'delivery_stats': delivery_stats,
                'daily_orders': daily_orders,
                'report_type': 'monthly'
            })
            
            # Use monthly specific template
            template_name = 'seller/vendor_order_report_monthly.html'

        elif report_type == 'date_range':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            if start_date and end_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                orders = orders.filter(created_at__gte=start_date, created_at__lt=end_date_obj)
            else:
                messages.warning(request, "Please select both start and end dates.")
            template_name = 'seller/vendor_order_report_pdf.html'

        elif report_type == 'yearly':
            year = int(request.POST.get('year', timezone.now().year))
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            orders = orders.filter(created_at__gte=start_date, created_at__lt=end_date)
            template_name = 'seller/vendor_order_report_pdf.html'

        else:
            template_name = 'seller/vendor_order_report_pdf.html'

        # Generate report based on format
        if report_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="vendor_order_report_{timezone.now().strftime("%Y%m%d")}.csv"'
            writer = csv.writer(response)
            
            # Headers
            writer.writerow([
                'Order ID', 'Date', 'Product', 'Customer', 
                'Payment Status', 'Order Status', 'Amount'
            ])

            # Data
            for order in orders:
                writer.writerow([
                    order.id,
                    order.created_at.strftime("%Y-%m-%d"),
                    order.product.name if order.product else '',
                    order.user.get_full_name() if order.user else 'Unknown',
                    order.is_paid,
                    order.order_status,
                    order.amount
                ])
            return response

        elif report_format == 'pdf' and pisa:
            try:
                # Add orders to context
                context.update({
                    'orders': orders,
                    'total_amount': orders.aggregate(Sum('amount'))['amount__sum'] or 0,
                })
                
                # Use the correct template for PDF generation
                template = get_template('seller/vendor_order_report_pdf.html')
                html = template.render(context)
                result = BytesIO()
                
                pdf = pisa.pisaDocument(
                    BytesIO(html.encode('UTF-8')),
                    result,
                    encoding='UTF-8'
                )

                if not pdf.err:
                    response = HttpResponse(result.getvalue(), content_type='application/pdf')
                    filename = f"vendor_order_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response
                else:
                    print("PDF Generation Errors:", pdf.err)
                    messages.error(request, f"Error generating PDF: {pdf.err}")
            except Exception as e:
                import traceback
                print("Exception during PDF generation:", str(e))
                print("Traceback:", traceback.format_exc())
                messages.error(request, f"Error generating PDF: {str(e)}")
            
            return redirect('vendor_dashboard')


class VendorChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'seller/vendor_change_password.html'
    success_url = reverse_lazy('vendor_change_password_done')

    def form_valid(self, form):
        print('-------form valid-----')
        return super().form_valid(form)

    def form_invalid(self, form):
        print('-------form invalid-----')
        return super().form_invalid(form)


class VendorChangePassworDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'seller/vendor_change_password_done.html'