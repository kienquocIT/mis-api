from django.urls import path, include

urlpatterns = [
    path('kms/', include('apps.kms.documentapproval.urls')),
    path('kms/', include('apps.kms.incomingdocument.urls')),
]
