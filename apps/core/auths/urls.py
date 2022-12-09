from django.urls import path

from .views import AuthLogin, AuthRefreshLogin, MyProfile

urlpatterns = [
    path('sign-in', AuthLogin.as_view(), name='AuthLogin'),
    path('token-refresh', AuthRefreshLogin.as_view(), name='AuthRefreshLogin'),
    path('profile', MyProfile.as_view(), name='MyProfile'),
]
