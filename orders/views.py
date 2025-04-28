from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render
from orders.models import Order
from .report_utils import get_vendor_orders, generate_csv_report, generate_pdf_report
from django.contrib import messages
import datetime
from django.contrib.auth.decorators import login_required

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('product', 'product__images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(user=self.request.user)
        return context

#user view for order list
class UserOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/user_order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('address', 'user').prefetch_related(
            'product', 
            'product__images',
            'user__addresses'
        )

@staff_member_required
def generate_report(request):
    report_type = request.GET.get('type')
    format_type = request.GET.get('format')

    if report_type not in ['monthly', 'yearly']:
        return HttpResponseBadRequest('Report type must be monthly or yearly')
    if format_type not in ['csv', 'pdf']:
        return HttpResponseBadRequest('Format must be csv or pdf')

    orders = get_aggregated_orders(report_type)

    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders_{report_type}.csv"'
        response.write(generate_csv_report(orders))
    else:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orders_{report_type}.pdf"'
        response.write(generate_pdf_report(orders))

    return response

@login_required
def vendor_report_view(request):
    # Check if user is a vendor
    try:
        vendor = request.user.vendor
    except AttributeError:
        messages.error(request, "Access denied. Only vendors can access reports.")
        return HttpResponseForbidden("Only vendors can access this page")

    if request.method == 'POST':
        try:
            report_type = request.POST.get('report_type')
            format_type = request.POST.get('format_type')

            if report_type not in ['monthly', 'yearly']:
                messages.error(request, "Invalid report type selected")
                return HttpResponseBadRequest("Invalid report type")

            if format_type not in ['pdf', 'csv']:
                messages.error(request, "Invalid format type selected")
                return HttpResponseBadRequest("Invalid format type")

            # Get orders data
            orders = get_vendor_orders(vendor, report_type)

            if not orders.exists():
                messages.warning(request, f"No orders found for {report_type} report")
                return render(request, 'order/vendor_report.html')

            # Generate filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"orders_{report_type}_{timestamp}"

            # Generate and return report
            if format_type == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
                response.write(generate_csv_report(orders, report_type))
            else:
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
                response.write(generate_pdf_report(orders, report_type))

            return response

        except Exception as e:
            messages.error(request, f"Error generating report: {str(e)}")
            return render(request, 'order/vendor_report.html')

    return render(request, 'order/vendor_report.html')
