from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime
from django.db.models import Sum, Count, Avg

from product.models import Cart, Confirmation, Product, Image, Category, Brand, WishList, SubCategory, Review
from orders.models import Order

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['user', 'rating', 'comment', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'stock', 'category', 'brand', 'vendor']
    list_filter = ['category', 'brand', 'vendor', 'product_type']
    search_fields = ['name', 'id', 'category__category_name', 'brand__brand_name']
    inlines = [ReviewInline]
    
    actions = [
        'export_product_performance_csv',
        'export_product_performance_pdf',
        'export_inventory_report_csv',
        'export_inventory_report_pdf',
        'export_category_sales_csv',
        'export_category_sales_pdf',
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
            for action_name in ['export_product_performance_csv', 'export_product_performance_pdf', 
                               'export_inventory_report_csv', 'export_inventory_report_pdf']:
                if action_name in actions:
                    vendor_actions[action_name] = actions[action_name]
            return vendor_actions
                   
        # Regular users don't get any product actions
        return {}
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Filter products based on user type
        if request.user.is_superuser:
            return qs
            
        if hasattr(request.user, 'vendor_profile'):
            # For vendors, only show their products
            return qs.filter(vendor=request.user.vendor_profile)
            
        # Regular users shouldn't access this admin, but if they do, show no products
        return qs.none()
    
    @admin.action(description='Export product performance to CSV')
    def export_product_performance_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=product-performance-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Product ID', 'Product Name', 'Category', 'Brand', 'Price', 
                         'Total Orders', 'Total Sales Amount', 'Average Rating'])
        
        # Process each product
        for product in queryset:
            # Skip this product if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if product.vendor != request.user.vendor_profile:
                    continue
                    
            # Get order data for this product
            orders = Order.objects.filter(product=product)
            total_orders = orders.count()
            total_sales = orders.filter(is_paid='Completed').aggregate(total=Sum('amount'))['total'] or 0
            
            # Get average rating
            reviews = Review.objects.filter(product=product)
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 'N/A'
            if avg_rating != 'N/A':
                avg_rating = f"{avg_rating:.1f}"
            
            writer.writerow([
                product.id,
                product.name,
                product.category.category_name if product.category else 'N/A',
                product.brand.brand_name if product.brand else 'N/A',
                f"₹{product.price}",
                total_orders,
                f"₹{total_sales}",
                avg_rating
            ])
        
        return response
    
    @admin.action(description='Export product performance to PDF')
    def export_product_performance_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Product Performance Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['Product ID', 'Name', 'Category', 'Total Orders', 'Total Sales', 'Stock', 'Avg Rating']]
        
        # Process each product
        for product in queryset:
            # Skip this product if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if product.vendor != request.user.vendor_profile:
                    continue
                    
            # Get order data for this product
            orders = Order.objects.filter(product=product)
            total_orders = orders.count()
            total_sales = orders.filter(is_paid='Completed').aggregate(total=Sum('amount'))['total'] or 0
            
            # Get average rating
            reviews = Review.objects.filter(product=product)
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 'N/A'
            if avg_rating != 'N/A':
                avg_rating = f"{avg_rating:.1f}"
            
            data.append([
                str(product.id),
                product.name,
                product.category.category_name if product.category else 'N/A',
                str(total_orders),
                f"₹{total_sales}",
                str(product.stock),
                str(avg_rating)
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
        response['Content-Disposition'] = f'attachment; filename=product-performance-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response
    
    @admin.action(description='Export inventory report to CSV')
    def export_inventory_report_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=inventory-report-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Product ID', 'Product Name', 'Category', 'Brand', 'Price', 
                         'Current Stock', 'Stock Status', 'Vendor'])
        
        # Process each product
        for product in queryset:
            # Skip this product if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if product.vendor != request.user.vendor_profile:
                    continue
            
            # Determine stock status
            if product.stock <= 0:
                stock_status = 'Out of Stock'
            elif product.stock < 5:
                stock_status = 'Low Stock'
            else:
                stock_status = 'In Stock'
                
            writer.writerow([
                product.id,
                product.name,
                product.category.category_name if product.category else 'N/A',
                product.brand.brand_name if product.brand else 'N/A',
                f"₹{product.price}",
                product.stock,
                stock_status,
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
        data = [['Product ID', 'Product Name', 'Category', 'Current Stock', 'Stock Status', 'Price']]
        
        # Process each product
        for product in queryset:
            # Skip this product if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if product.vendor != request.user.vendor_profile:
                    continue
            
            # Determine stock status
            if product.stock <= 0:
                stock_status = 'Out of Stock'
            elif product.stock < 5:
                stock_status = 'Low Stock'
            else:
                stock_status = 'In Stock'
                
            data.append([
                str(product.id),
                product.name,
                product.category.category_name if product.category else 'N/A',
                str(product.stock),
                stock_status,
                f"₹{product.price}"
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
    
    @admin.action(description='Export category-wise sales to CSV')
    def export_category_sales_csv(self, request, queryset):
        # This report is admin-only
        if not request.user.is_superuser:
            return HttpResponse("Permission denied", status=403)
            
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=category-sales-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Category', 'Number of Products', 'Total Orders', 'Total Sales Amount'])
        
        # Get all categories
        categories = Category.objects.all()
        
        for category in categories:
            # Get products in this category
            products = Product.objects.filter(category=category)
            product_count = products.count()
            
            # Get orders for these products
            product_ids = products.values_list('id', flat=True)
            orders = Order.objects.filter(product__in=product_ids, is_paid='Completed')
            
            total_orders = orders.count()
            total_sales = orders.aggregate(total=Sum('amount'))['total'] or 0
            
            writer.writerow([
                category.category_name,
                product_count,
                total_orders,
                f"₹{total_sales}"
            ])
        
        return response
    
    @admin.action(description='Export category-wise sales to PDF')
    def export_category_sales_pdf(self, request, queryset):
        # This report is admin-only
        if not request.user.is_superuser:
            return HttpResponse("Permission denied", status=403)
            
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Category-wise Sales Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['Category', 'Products Count', 'Total Orders', 'Total Sales']]
        
        # Get all categories
        categories = Category.objects.all()
        
        for category in categories:
            # Get products in this category
            products = Product.objects.filter(category=category)
            product_count = products.count()
            
            # Get orders for these products
            product_ids = products.values_list('id', flat=True)
            orders = Order.objects.filter(product__in=product_ids, is_paid='Completed')
            
            total_orders = orders.count()
            total_sales = orders.aggregate(total=Sum('amount'))['total'] or 0
            
            data.append([
                category.category_name,
                str(product_count),
                str(total_orders),
                f"₹{total_sales}"
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
        response['Content-Disposition'] = f'attachment; filename=category-sales-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating', 'created_at', 'is_verified']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['product', 'user', 'rating', 'comment', 'created_at']
    
    actions = ['export_reviews_csv', 'export_reviews_pdf', 'verify_reviews']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Filter reviews based on user type
        if request.user.is_superuser:
            return qs
            
        if hasattr(request.user, 'vendor_profile'):
            # For vendors, only show reviews for their products
            return qs.filter(product__vendor=request.user.vendor_profile)
            
        # Regular users shouldn't access this admin, but if they do, show no reviews
        return qs.none()
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        # Check if user is superuser (Admin)
        if request.user.is_superuser:
            return actions
            
        # For Vendor users
        if hasattr(request.user, 'vendor_profile'):
            vendor_actions = {}
            for action_name in ['export_reviews_csv', 'export_reviews_pdf', 'verify_reviews']:
                if action_name in actions:
                    vendor_actions[action_name] = actions[action_name]
            return vendor_actions
                   
        # Regular users don't get any actions
        return {}
    
    @admin.action(description="Mark selected reviews as verified")
    def verify_reviews(self, request, queryset):
        queryset.update(is_verified=True)
    
    @admin.action(description='Export customer reviews to CSV')
    def export_reviews_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=customer-reviews-{datetime.now().strftime("%Y-%m-%d")}.csv'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Review ID', 'Product', 'Customer', 'Rating', 'Comment', 'Date', 'Verified'])
        
        # Write data rows
        for review in queryset:
            # Skip this review if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if review.product.vendor != request.user.vendor_profile:
                    continue
                    
            writer.writerow([
                review.id,
                review.product.name,
                review.user.username if review.user else 'Anonymous',
                review.rating,
                review.comment or 'No comment',
                review.created_at.strftime("%Y-%m-%d"),
                'Yes' if review.is_verified else 'No'
            ])
        
        return response
    
    @admin.action(description='Export customer reviews to PDF')
    def export_reviews_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Customer Reviews Report", styles['Heading1'])
        elements.append(title)
        
        # Define table data with header row
        data = [['ID', 'Product', 'Customer', 'Rating', 'Date', 'Verified']]
        
        # Add data rows to table
        for review in queryset:
            # Skip this review if user is vendor and product doesn't belong to them
            if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                if review.product.vendor != request.user.vendor_profile:
                    continue
                    
            data.append([
                str(review.id),
                review.product.name,
                review.user.username if review.user else 'Anonymous',
                str(review.rating),
                review.created_at.strftime("%Y-%m-%d"),
                'Yes' if review.is_verified else 'No'
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
        
        # Add comments in a separate section
        if queryset.filter(comment__isnull=False).exclude(comment='').exists():
            elements.append(Paragraph("Review Comments", styles['Heading2']))
            for review in queryset:
                if review.comment:
                    # Skip this review if user is vendor and product doesn't belong to them
                    if hasattr(request.user, 'vendor_profile') and not request.user.is_superuser:
                        if review.product.vendor != request.user.vendor_profile:
                            continue
                    
                    elements.append(Paragraph(f"<b>Review #{review.id} - {review.product.name} - Rating: {review.rating}/5</b>", styles['Normal']))
                    elements.append(Paragraph(f"{review.comment}", styles['Normal']))
                    elements.append(Paragraph(" ", styles['Normal']))  # Empty space
        
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=customer-reviews-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        response.write(pdf)
        
        return response

# Register models with admin site
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Image)
admin.site.register(Brand)
admin.site.register(Cart)
admin.site.register(WishList)
admin.site.register(Review, ReviewAdmin)