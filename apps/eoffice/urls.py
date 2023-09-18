from django.urls import path, include

urlpatterns = [
    path('leave/', include('apps.eoffice.leave.urls')),
]
