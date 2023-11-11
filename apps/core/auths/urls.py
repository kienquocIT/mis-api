from django.urls import path

from .views import (
    AuthLogin, AuthRefreshLogin, MyProfile, AliveCheckView, SwitchCompanyView, AuthValidAccessCode,
    MyLanguageView,
)

urlpatterns = [
    path('sign-in', AuthLogin.as_view(), name='AuthLogin'),
    path('media/sign-in-valid', AuthValidAccessCode.as_view(), name='AuthValidAccessCode'),
    path('switch-company', SwitchCompanyView.as_view(), name='SwitchCompanyView'),
    path('token-refresh', AuthRefreshLogin.as_view(), name='AuthRefreshLogin'),
    path('profile', MyProfile.as_view(), name='MyProfile'),
    path('alive-check', AliveCheckView.as_view(), name='AliveCheck'),
    path('language', MyLanguageView.as_view(), name='MyLanguageView'),
]
