from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime
from django.db.models import Sum, Count
from django.utils.html import strip_tags

from orders.models import Order
from product.models import Product

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'amount', 'is_paid', 'order_status', 'created_at']
    list_filter = ['is_paid', 'order_status', 'created_at']
    search_fields = ['id', 'user__username', 'user__email', 'product__name', 'razorpay_order_id']
    date_hierarchy = 'created_at'
    
    actions = [
        'export_sales_report_csv', 
        'export_sales_report_pdf', 
        'export_order_report_csv', 
        'export_order_report_pdf',
        'export_inventory_report_csv',
        'export_inventory_report_pdf',
        'export_payment_report_csv',
        'export_payment_report_pdf',
        'export_refund_report_csv',
        'export_refund_report_pdf'
    ]
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        # Check if user is superuser (Admin)
        if request.user.is_superuser:
            return actions
            
        # For Vendor users
        if hasattr(request.user, 'vendor_profile'):
            # Keep only vendor-appropriate export actions
            vendor_actions = {}
            for action_name in ['export_sales_report_csv', 'export_sales_report_pdf', 
                               'export_order_report_csv', 'export_order_report_pdf',
                               'export_inventory_report_csv', 'export_inventory_report_pdf',
                               'export_payment_report_csv', 'export_payment_report_pdf',
                               'export_refund_report_csv', 'export_refund_report_pdf']:
                if action_name in actions:
                    vendor_actions[action_name] = actions[action_name]
            return vendor_actions
                   
        # For regular users, only show order reports and refund reports
        user_actions = {}
        for action_name in ['export_order_report_csv', 'export_order_report_pdf', 
                           'export_refund_report_csv', 'export_refund_report_pdf']:
            if action_name in actions:
                user_actions[action_name] = actions[action_name]
        return user_actions
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Filter orders based on user type
        if request.user.is_superuser:
            return qs
            
        if hasattr(request.user, 'vendor_profile'):
            # For vendors, only show orders containing their products
            return qs.filter(product__vendor=request.user.vendor_profile)
            
        # For regular users, only show their own orders
        return qs.filter(user=request.user)
    
    @admin.action(description='Export sales report to CSV')
    def export_sales_report_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=sales-report-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Order ID', 'Customer', 'Email', 'Product', 
                         'Amount', 'Payment Status', 'Order Status', 'Date'])
        
        # Write data rows
        for order in queryset:
            # Skip this order if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if order.product.vendor != request.user.vendor_profile:
                    continue
                    
            writer.writerow([
                order.id,
                order.user.username if order.user else 'Guest',
                order.user.email if order.user else 'N/A',
                order.product.name if order.product else 'N/A',
                f"₹{order.amount}" if order.amount else 'N/A',
                order.is_paid,
                order.order_status,
                order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else 'N/A'
            ])
        
        return response
    
    @admin.action(description='Export sales report to PDF')
    def export_sales_report_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Sales Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['Order ID', 'Customer', 'Product', 'Amount', 'Status', 'Date']]
        
        # Add data rows to table
        for order in queryset:
            # Skip this order if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if order.product.vendor != request.user.vendor_profile:
                    continue
                    
            data.append([
                str(order.id),
                order.user.username if order.user else 'Guest',
                order.product.name if order.product else 'N/A',
                f"₹{order.amount}" if order.amount else 'N/A',
                order.is_paid,
                order.created_at.strftime("%Y-%m-%d") if order.created_at else 'N/A'
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
        response['Content-Disposition'] = f'attachment; filename=sales-report-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response
    
    @admin.action(description='Export order details to CSV')
    def export_order_report_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=order-report-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Order ID', 'Order Date', 'Customer', 'Shipping Address', 
                        'Product', 'Amount', 'Payment Status', 'Order Status'])
        
        # Write data rows
        for order in queryset:
            shipping_address = f"{order.address.address}, {order.address.city}, {order.address.state} - {order.address.pincode}" if order.address else "N/A"
            
            writer.writerow([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else 'N/A',
                order.user.username if order.user else 'Guest',
                shipping_address,
                order.product.name if order.product else 'N/A',
                f"₹{order.amount}" if order.amount else 'N/A',
                order.is_paid,
                order.order_status,
            ])
        
        return response
    
    @admin.action(description='Export order details to PDF')
    def export_order_report_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Order Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['Order ID', 'Customer', 'Order Date', 'Product', 'Amount', 'Status']]
        
        # Add data rows to table
        for order in queryset:
            data.append([
                str(order.id),
                order.user.username if order.user else 'Guest',
                order.created_at.strftime("%Y-%m-%d") if order.created_at else 'N/A',
                order.product.name if order.product else 'N/A',
                f"₹{order.amount}" if order.amount else 'N/A',
                order.order_status
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
        response['Content-Disposition'] = f'attachment; filename=order-report-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response
        
    @admin.action(description='Export inventory report to CSV')
    def export_inventory_report_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=inventory-report-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Product ID', 'Product Name', 'Category', 'Brand', 'Price', 'Stock', 'Vendor'])
        
        # Get unique products from orders
        products = set()
        for order in queryset:
            if order.product:
                products.add(order.product)
                
        # If no products found in orders, get all products
        if not products and (request.user.is_superuser or hasattr(request.user, 'vendor_profile')):
            if hasattr(request.user, 'vendor_profile'):
                products = Product.objects.filter(vendor=request.user.vendor_profile)
            else:
                products = Product.objects.all()
        
        # Write product data
        for product in products:
            writer.writerow([
                product.id,
                product.name,
                product.category.category_name if product.category else 'N/A',
                product.brand.brand_name if product.brand else 'N/A',
                f"₹{product.price}",
                product.stock,
                product.vendor.business_name if product.vendor else 'N/A'
            ])
            
        return response
    
    @admin.action(description='Export inventory report to PDF')
    def export_inventory_report_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Inventory Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['Product ID', 'Product Name', 'Category', 'Stock', 'Price', 'Vendor']]
        
        # Get unique products from orders
        products = set()
        for order in queryset:
            if order.product:
                products.add(order.product)
                
        # If no products found in orders, get all products
        if not products and (request.user.is_superuser or hasattr(request.user, 'vendor_profile')):
            if hasattr(request.user, 'vendor_profile'):
                products = Product.objects.filter(vendor=request.user.vendor_profile)
            else:
                products = Product.objects.all()
        
        # Add product data to table
        for product in products:
            data.append([
                str(product.id),
                product.name,
                product.category.category_name if product.category else 'N/A',
                str(product.stock),
                f"₹{product.price}",
                product.vendor.business_name if product.vendor else 'N/A'
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
        response['Content-Disposition'] = f'attachment; filename=inventory-report-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response
    
    @admin.action(description='Export payment report to CSV')
    def export_payment_report_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=payment-report-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Order ID', 'Payment Date', 'Customer', 'Amount', 
                         'Payment Status', 'Payment ID', 'Razorpay Order ID'])
        
        # Write data rows
        for order in queryset:
            # Skip this order if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if order.product.vendor != request.user.vendor_profile:
                    continue
                    
            writer.writerow([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else 'N/A',
                order.user.username if order.user else 'Guest',
                f"₹{order.amount}" if order.amount else 'N/A',
                order.is_paid,
                order.razorpay_payment_id or 'N/A',
                order.razorpay_order_id or 'N/A'
            ])
        
        return response
    
    @admin.action(description='Export payment report to PDF')
    def export_payment_report_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Payment Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['Order ID', 'Date', 'Customer', 'Amount', 'Status', 'Payment ID']]
        
        # Add data rows to table
        for order in queryset:
            # Skip this order if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if order.product.vendor != request.user.vendor_profile:
                    continue
                    
            data.append([
                str(order.id),
                order.created_at.strftime("%Y-%m-%d") if order.created_at else 'N/A',
                order.user.username if order.user else 'Guest',
                f"₹{order.amount}" if order.amount else 'N/A',
                order.is_paid,
                order.razorpay_payment_id or 'N/A'
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
        response['Content-Disposition'] = f'attachment; filename=payment-report-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response
    
    @admin.action(description='Export refund report to CSV')
    def export_refund_report_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=refund-report-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Order ID', 'Refund Date', 'Customer', 'Product', 
                         'Amount', 'Status', 'Reason'])
        
        # Filter only refunded/canceled orders
        refund_orders = queryset.filter(is_paid='Canceled')
        
        # Write data rows
        for order in refund_orders:
            writer.writerow([
                order.id,
                order.updated_at.strftime("%Y-%m-%d %H:%M") if order.updated_at else 'N/A',
                order.user.username if order.user else 'Guest',
                order.product.name if order.product else 'N/A',
                f"₹{order.amount}" if order.amount else 'N/A',
                'Refunded',
                'Order canceled' # Add reason field in your model if needed
            ])
        
        return response
    
    @admin.action(description='Export refund report to PDF')
    def export_refund_report_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Refund Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['Order ID', 'Date', 'Customer', 'Product', 'Amount', 'Status']]
        
        # Filter only refunded/canceled orders
        refund_orders = queryset.filter(is_paid='Canceled')
        
        # Add data rows to table
        for order in refund_orders:
            data.append([
                str(order.id),
                order.updated_at.strftime("%Y-%m-%d") if order.updated_at else 'N/A',
                order.user.username if order.user else 'Guest',
                order.product.name if order.product else 'N/A',
                f"₹{order.amount}" if order.amount else 'N/A',
                'Refunded'
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
        response['Content-Disposition'] = f'attachment; filename=refund-report-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response

# Register the Order model with the custom admin
admin.site.register(Order, OrderAdmin)