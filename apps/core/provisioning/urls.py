from django.urls import path
from .views import NewTenant

urlpatterns = [
    path('new-tenant', NewTenant.as_view(), name='NewTenant'),
]
