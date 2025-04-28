import csv
import io
from datetime import datetime
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncYear
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from orders import models


def get_vendor_orders(vendor, report_type):
    """Get orders for vendor's products with specified report type"""
    from .models import Order
    
    # Base queryset for vendor's products
    base_query = Order.objects.filter(product__vendor=vendor)
    
    if report_type == 'yearly':
        return base_query.annotate(
            period=TruncYear('created_at')
        ).values(
            'period',
            'product__name'
        ).annotate(
            total_orders=Count('id'),
            total_amount=Sum('amount'),
            completed=Count('id', filter=models.Q(is_paid='Completed')),
            pending=Count('id', filter=models.Q(is_paid='Pending'))
        ).order_by('-period', 'product__name')
    else:  # monthly
        return base_query.annotate(
            period=TruncMonth('created_at')
        ).values(
            'period',
            'product__name'
        ).annotate(
            total_orders=Count('id'),
            total_amount=Sum('amount'),
            completed=Count('id', filter=models.Q(is_paid='Completed')),
            pending=Count('id', filter=models.Q(is_paid='Pending'))
        ).order_by('-period', 'product__name')

def generate_csv_report(orders, report_type):
    """Generate CSV report for vendor orders"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    headers = ['Period', 'Product', 'Total Orders', 'Completed', 'Pending', 'Total Amount']
    writer.writerow(headers)
    
    # Write data
    for order in orders:
        period_format = '%Y' if report_type == 'yearly' else '%Y-%m'
        writer.writerow([
            order['period'].strftime(period_format),
            order['product__name'],
            order['total_orders'],
            order['completed'],
            order['pending'],
            f"₹{float(order['total_amount'] or 0):.2f}"
        ])
    
    return output.getvalue()

def generate_pdf_report(orders, report_type):
    """Generate PDF report for vendor orders"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    
    # Prepare data
    data = [['Period', 'Product', 'Total Orders', 'Completed', 'Pending', 'Total Amount']]
    
    for order in orders:
        period_format = '%Y' if report_type == 'yearly' else '%Y-%m'
        data.append([
            order['period'].strftime(period_format),
            order['product__name'],
            str(order['total_orders']),
            str(order['completed']),
            str(order['pending']),
            f"₹{float(order['total_amount'] or 0):.2f}"
        ])
    
    # Create table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        # Header style
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        # Data style
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Alternate row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(table)
    doc.build(elements)
    return buffer.getvalue() 