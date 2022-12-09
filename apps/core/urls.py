from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.core.auths.urls')),
    path('provisioning/', include('apps.core.provisioning.urls')),
]
