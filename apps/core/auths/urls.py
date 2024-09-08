from django.urls import path

from .views import (
    AuthLogin, AuthRefreshLogin, MyProfile, AliveCheckView, SwitchCompanyView,
    MyLanguageView, ChangePasswordView, ForgotPasswordView, ForgotPasswordDetailView, AuthLogout, AuthLogsView,
    AuthLogReport,
)
from .views_2fa import TwoFAIntegrate, TwoFAIntegrateDetail, TwoFA

urlpatterns = [
    path('sign-in', AuthLogin.as_view(), name='AuthLogin'),
    path('sign-out', AuthLogout.as_view(), name='AuthLogout'),
    path('token-refresh', AuthRefreshLogin.as_view(), name='AuthRefreshLogin'),
    path('forgot-password', ForgotPasswordView.as_view(), name='ForgotPasswordView'),
    path('forgot-password/<str:pk>', ForgotPasswordDetailView.as_view(), name='ForgotPasswordDetailView'),

    path('profile', MyProfile.as_view(), name='MyProfile'),
    path('alive-check', AliveCheckView.as_view(), name='AliveCheck'),
    path('language', MyLanguageView.as_view(), name='MyLanguageView'),
    path('change-password', ChangePasswordView.as_view(), name='ChangePasswordView'),
    path('switch-company', SwitchCompanyView.as_view(), name='SwitchCompanyView'),
    path('logs', AuthLogsView.as_view(), name='AuthLogsView'),
    path('logs/report', AuthLogReport.as_view(), name='AuthLogReport'),

    path('2fa', TwoFA.as_view(), name='TwoFA'),
    path('2fa/integrate', TwoFAIntegrate.as_view(), name='TwoFAIntegrate'),
    path('2fa/integrate/<str:pk>', TwoFAIntegrateDetail.as_view(), name='TwoFAIntegrateDetail'),
]
