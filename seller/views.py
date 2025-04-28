from django.views.generic import View
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render
from django.contrib import messages
import datetime

# ... existing code ...

@method_decorator(staff_member_required, name='dispatch')
class GenerateReportView(View):
    def get(self, request, *args, **kwargs):
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

class VendorReportView(LoginRequiredMixin, View):
    template_name = 'seller/vendor_order_report.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.vendor = request.user.vendor
        except AttributeError:
            messages.error(request, "Access denied. Only vendors can access reports.")
            return HttpResponseForbidden("Only vendors can access this page")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        try:
            report_type = request.POST.get('report_type')
            format_type = request.POST.get('format')

            if report_type not in ['monthly', 'yearly']:
                messages.error(request, "Invalid report type selected")
                return HttpResponseBadRequest("Invalid report type")

            if format_type not in ['pdf', 'csv']:
                messages.error(request, "Invalid format type selected")
                return HttpResponseBadRequest("Invalid format type")

            # Get orders data
            orders = get_vendor_orders(self.vendor, report_type)
            
            if not orders.exists():
                messages.warning(request, f"No orders found for {report_type} report")
                return render(request, self.template_name)

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
            return render(request, self.template_name) 