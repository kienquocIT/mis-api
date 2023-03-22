from django.urls import path

from .views import AuthLogin, AuthRefreshLogin, MyProfile, AliveCheckView, SwitchCompanyView

urlpatterns = [
    path('sign-in', AuthLogin.as_view(), name='AuthLogin'),
    path('switch-company', SwitchCompanyView.as_view(), name='SwitchCompanyView'),
    path('token-refresh', AuthRefreshLogin.as_view(), name='AuthRefreshLogin'),
    path('profile', MyProfile.as_view(), name='MyProfile'),
    path('alive-check', AliveCheckView.as_view(), name='AliveCheck'),
]
