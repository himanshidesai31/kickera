from django.contrib import admin, messages
from django.conf import settings
from django.core.mail import send_mail
from users.models import User
from vendor.models import VendorProfile, VendorRequest

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


admin.site.register(VendorRequest, VendorRequestAdmin)
admin.site.register(VendorProfile, VendorProfileAdmin)
