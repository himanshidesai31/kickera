from allauth.account.views import LoginView, LogoutView
from django.urls import path, include
from django.views.generic import TemplateView
from core.views import (
    HomePageView,
    AboutPageView,
    PasswordChangeView,
    ReauthenticateView,
    ConfirmationPageView,
    ContactView,
    SuccessView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('about/', AboutPageView.as_view(), name='about'),
    # path('contect/', ContectPageView.as_view(), name='contact'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('success/', SuccessView.as_view(), name='success'),
    path('product/confirmation/', ConfirmationPageView.as_view(), name='confirmation'),
    #password change url
    path('accounts/password/change/', PasswordChangeView.as_view(), name='account_change_password'),
    path('accounts/login/', LoginView.as_view(), name='account_login'),
    path('accounts/logout/', LogoutView.as_view(), name='account_logout'),
    path('accounts/reauthenticate/', ReauthenticateView.as_view(), name='account_reauthenticate'),
    path('accounts/password/change/done/', TemplateView.as_view(template_name="account/password_change_done.html"),
         name='account_change_password_done'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
