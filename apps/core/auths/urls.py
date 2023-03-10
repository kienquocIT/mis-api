from django.urls import path

from .views import AuthLogin, AuthRefreshLogin, MyProfile, AliveCheckView

urlpatterns = [
    path('sign-in', AuthLogin.as_view(), name='AuthLogin'),
    path('token-refresh', AuthRefreshLogin.as_view(), name='AuthRefreshLogin'),
    path('profile', MyProfile.as_view(), name='MyProfile'),
    path('alive-check', AliveCheckView.as_view(), name='MyProfile'),
]
