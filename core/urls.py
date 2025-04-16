from allauth.account.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import TemplateView
from core.views import (
    HomePageView,
    AboutPageView,
    PasswordChangeView,
    ReauthenticateView,
    ConfirmationPageView,
)
urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('product/confirmation/', ConfirmationPageView.as_view(), name='confirmation'),
    #password change url
    path('accounts/password/change/', PasswordChangeView.as_view(), name='account_change_password'),
    path('accounts/login/', LoginView.as_view(), name='account_login'),
    path('accounts/logout/', LogoutView.as_view(), name='account_logout'),
    path('accounts/reauthenticate/', ReauthenticateView.as_view(), name='account_reauthenticate'),
    path('accounts/password/change/done/', TemplateView.as_view(template_name="account/password_change_done.html"),
         name='account_change_password_done'),
]
