from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.core.auths.urls')),
    path('account/', include('apps.core.account.urls')),
    path('provisioning/', include('apps.core.provisioning.urls')),
    path('hr/', include('apps.core.hr.urls')),
    path('tenant/', include('apps.core.tenant.urls')),
    path('company/', include('apps.core.company.urls')),
    path('base/', include('apps.core.base.urls')),
    path('workflow/', include('apps.core.workflow.urls')),
]
