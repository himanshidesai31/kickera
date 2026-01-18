from django.contrib import admin, messages
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime
from django.db.models import Sum, Count, F

from users.models import User
from vendor.models import VendorProfile, VendorRequest
from orders.models import Order
from product.models import Product

class VendorRequestAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'email', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['business_name', 'email']
    actions = ['approve_vendors', 'reject_vendors']

    def approve_vendors(self, request, queryset):
        for vendor_req in queryset:
            if vendor_req.status != 'approved':
                vendor_req.status = 'approved'
                vendor_req.save()

                # Import pdb
                # pdb.set_trace()
                
                # Create or get user with vendor privileges
                defaults = {"is_vendor": True}
                
                # If vendor request has a saved password, use it for new user creation
                if vendor_req.password:
                    defaults["password"] = vendor_req.password
                
                user, created = User.objects.get_or_create(
                    email=vendor_req.email,
                    defaults=defaults
                )
                
                # Update is_vendor flag for existing users too
                if not created:
                    user.is_vendor = True
                    user.save()
                    
                VendorProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'business_name': vendor_req.business_name,
                        'phone_number': vendor_req.phone_number,
                        'email': vendor_req.email,
                        'business_registration_number': vendor_req.business_registration_number,
                        'tax_id': vendor_req.tax_id,
                        'logo': vendor_req.logo,
                        'gst_no': vendor_req.gst_no,
                    }
                )

                # Send email notification
                if vendor_req.email:
                    try:
                        send_mail(
                            subject='Your Vendor Application has been Approved!',
                            message=f"Hello  your vendor request for '{vendor_req.business_name}' has been approved. You can now log in and start selling!",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[vendor_req.email],
                        )
                    except Exception as e:
                        self.message_user(
                            request,
                            f"Error sending approval email to {vendor_req.email}: {str(e)}",
                            level=messages.ERROR
                        )

        self.message_user(request, "Selected vendor requests have been approved and processed.")

    approve_vendors.short_description = " Approve selected vendor requests"

    def reject_vendors(self, request, queryset):
        for vendor_req in queryset:
            if vendor_req.status != 'rejected':
                vendor_req.status = 'rejected'
                vendor_req.save()

                if vendor_req.email:
                    try:
                        send_mail(
                            subject='Your Vendor Application has been Rejected',
                            message=f"Hello {vendor_req.user.username if vendor_req.user else 'Seller'}, unfortunately your vendor request for '{vendor_req.business_name}' has been rejected.",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[vendor_req.email],
                        )
                    except Exception as e:
                        self.message_user(
                            request,
                            f"Error sending rejection email to {vendor_req.email}: {str(e)}",
                            level=messages.ERROR
                        )

        self.message_user(request, "Selected vendor requests have been rejected and notified.")

    reject_vendors.short_description = " Reject selected vendor requests"

class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['business_name', 'email']
    actions = ['export_commission_report_csv', 'export_commission_report_pdf', 'export_vendor_sales_report_csv', 'export_vendor_sales_report_pdf']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        # Check if user is superuser (Admin)
        if request.user.is_superuser:
            return actions
            
        # For Vendor users, allow only their own reports
        if hasattr(request.user, 'vendor_profile'):
            # Keep only vendor-appropriate export actions
            vendor_actions = {}
            if 'export_commission_report_csv' in actions:
                vendor_actions['export_commission_report_csv'] = actions['export_commission_report_csv']
            if 'export_commission_report_pdf' in actions:
                vendor_actions['export_commission_report_pdf'] = actions['export_commission_report_pdf']
            if 'export_vendor_sales_report_csv' in actions:
                vendor_actions['export_vendor_sales_report_csv'] = actions['export_vendor_sales_report_csv']
            if 'export_vendor_sales_report_pdf' in actions:
                vendor_actions['export_vendor_sales_report_pdf'] = actions['export_vendor_sales_report_pdf']
            return vendor_actions
                   
        # Regular users don't get any vendor actions
        return {}
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Filter vendors based on user type
        if request.user.is_superuser:
            return qs
            
        if hasattr(request.user, 'vendor_profile'):
            # Vendors can only see themselves
            return qs.filter(id=request.user.vendor_profile.id)
            
        # Regular users shouldn't access this admin, but if they do, show no vendors
        return qs.none()
    
    @admin.action(description='Export commission report to CSV')
    def export_commission_report_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=commission-report-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Vendor', 'Period', 'Total Orders', 'Total Sales', 'Commission Rate', 'Commission Amount'])
        
        # Set a default commission rate (this should be configurable in a real system)
        commission_rate = 0.10  # 10%
        
        for vendor in queryset:
            # Skip this vendor if user is vendor and not themselves
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if vendor.id != request.user.vendor_profile.id:
                    continue
            
            # Get completed orders for this vendor
            vendor_products = Product.objects.filter(vendor=vendor)
            orders = Order.objects.filter(product__in=vendor_products, is_paid='Completed')
            
            # Group by month for current year
            current_year = datetime.now().year
            for month in range(1, 13):
                month_orders = orders.filter(created_at__year=current_year, created_at__month=month)
                total_orders = month_orders.count()
                
                if total_orders > 0:
                    total_sales = month_orders.aggregate(total=Sum('amount'))['total'] or 0
                    commission_amount = total_sales * commission_rate
                    
                    writer.writerow([
                        vendor.business_name,
                        f"{current_year}-{month:02d}",
                        total_orders,
                        f"₹{total_sales}",
                        f"{commission_rate:.0%}",
                        f"₹{commission_amount}"
                    ])
        
        return response
    
    @admin.action(description='Export commission report to PDF')
    def export_commission_report_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Commission Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['Vendor', 'Period', 'Orders', 'Total Sales', 'Commission']]
        
        # Set a default commission rate (this should be configurable in a real system)
        commission_rate = 0.10  # 10%
        
        for vendor in queryset:
            # Skip this vendor if user is vendor and not themselves
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if vendor.id != request.user.vendor_profile.id:
                    continue
            
            # Get completed orders for this vendor
            vendor_products = Product.objects.filter(vendor=vendor)
            orders = Order.objects.filter(product__in=vendor_products, is_paid='Completed')
            
            # Group by month for current year
            current_year = datetime.now().year
            for month in range(1, 13):
                month_orders = orders.filter(created_at__year=current_year, created_at__month=month)
                total_orders = month_orders.count()
                
                if total_orders > 0:
                    total_sales = month_orders.aggregate(total=Sum('amount'))['total'] or 0
                    commission_amount = total_sales * commission_rate
                    
                    data.append([
                        vendor.business_name,
                        f"{current_year}-{month:02d}",
                        str(total_orders),
                        f"₹{total_sales}",
                        f"₹{commission_amount}"
                    ])
        
        # Create table and set style
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=commission-report-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response
    
    @admin.action(description='Export vendor sales report to CSV')
    def export_vendor_sales_report_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=vendor-sales-report-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Vendor', 'Total Products', 'Products Sold', 'Total Orders', 'Total Sales', 'Average Order Value'])
        
        for vendor in queryset:
            # Skip this vendor if user is vendor and not themselves
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if vendor.id != request.user.vendor_profile.id:
                    continue
            
            # Get vendor statistics
            vendor_products = Product.objects.filter(vendor=vendor)
            total_products = vendor_products.count()
            
            orders = Order.objects.filter(product__in=vendor_products, is_paid='Completed')
            total_orders = orders.count()
            total_sales = orders.aggregate(total=Sum('amount'))['total'] or 0
            avg_order_value = total_sales / total_orders if total_orders > 0 else 0
            
            # Get distinct products that have been sold
            products_sold = orders.values('product').distinct().count()
            
            writer.writerow([
                vendor.business_name,
                total_products,
                products_sold,
                total_orders,
                f"₹{total_sales}",
                f"₹{avg_order_value:.2f}"
            ])
        
        return response
    
    @admin.action(description='Export vendor sales report to PDF')
    def export_vendor_sales_report_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Vendor Sales Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['Vendor', 'Products', 'Orders', 'Total Sales', 'Avg. Order Value']]
        
        for vendor in queryset:
            # Skip this vendor if user is vendor and not themselves
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if vendor.id != request.user.vendor_profile.id:
                    continue
            
            # Get vendor statistics
            vendor_products = Product.objects.filter(vendor=vendor)
            total_products = vendor_products.count()
            
            orders = Order.objects.filter(product__in=vendor_products, is_paid='Completed')
            total_orders = orders.count()
            total_sales = orders.aggregate(total=Sum('amount'))['total'] or 0
            avg_order_value = total_sales / total_orders if total_orders > 0 else 0
            
            data.append([
                vendor.business_name,
                str(total_products),
                str(total_orders),
                f"₹{total_sales}",
                f"₹{avg_order_value:.2f}"
            ])
        
        # Create table and set style
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=vendor-sales-report-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response

admin.site.register(VendorRequest, VendorRequestAdmin)
admin.site.register(VendorProfile, VendorProfileAdmin)
