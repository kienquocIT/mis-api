from django.urls import path
from .views import NewTenant, TenantNewAdmin, TenantUpdateAdmin

urlpatterns = [
    path('tenants', NewTenant.as_view(), name='NewTenant'),
    path('tenant/new-admin/<str:pk>', TenantNewAdmin.as_view(), name='TenantNewAdmin'),
    path('tenant/update-admin/<str:code>', TenantUpdateAdmin.as_view(), name='TenantUpdateAdmin'),
]
