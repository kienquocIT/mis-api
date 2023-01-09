from django.urls import path
from .views import TenantInformation

urlpatterns = [
    path('userlist', TenantInformation.as_view(), name='TenantInformation'),
]
