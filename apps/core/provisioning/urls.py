from django.urls import path
from .views import NewTenant, TenantNewAdmin

urlpatterns = [
    path('tenant', NewTenant.as_view(), name='NewTenant'),
    path('tenant/new-admin/<str:pk>', TenantNewAdmin.as_view(), name='TenantNewAdmin'),
]
