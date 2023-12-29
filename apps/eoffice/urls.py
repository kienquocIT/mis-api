from django.urls import path, include

urlpatterns = [
    path('leave/', include('apps.eoffice.leave.urls')),
    path('business-trip/', include('apps.eoffice.businesstrip.urls')),
    path('asset-tools/', include('apps.eoffice.assettools.urls')),
    path('meeting-schedule/', include('apps.eoffice.meeting.urls')),
]
