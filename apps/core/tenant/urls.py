from django.urls import path
from .views import TenantDetail

urlpatterns = [
    path('', TenantDetail.as_view(), name='TenantDetail'),
]
