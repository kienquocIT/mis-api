from django.urls import path, include

urlpatterns = [
    path('kms/', include('apps.kms.document_approval.urls')),
]
