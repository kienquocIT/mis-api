from django.urls import path

from apps.core.mailer.views import (
    MailerConfigList, MailerConfigDetail, MailerSystemGetByCode, MailerSystemDetail,
    MailerServerConfigGet, MailerServerConfigDetail, MailServerTestConnectAPI, MailServerTestConnectDataAPI,
)

urlpatterns = [
    path('list', MailerConfigList.as_view(), name='MailerConfigList'),
    path('detail/<str:pk>', MailerConfigDetail.as_view(), name='MailerConfigDetail'),
    path('system/get/<str:system_code>', MailerSystemGetByCode.as_view(), name='MailerSystemGetByCode'),
    path('system/detail/<str:pk>', MailerSystemDetail.as_view(), name='MailerSystemDetail'),
    path('config/get', MailerServerConfigGet.as_view(), name='MailerServerConfigGet'),
    path('config/detail/<str:pk>', MailerServerConfigDetail.as_view(), name='MailerServerConfigDetail'),
    path('config/detail/<str:pk>/connection/test', MailServerTestConnectAPI.as_view(), name='MailServerTestConnectAPI'),
    path(
        'config/detail/<str:pk>/connection/test/data', MailServerTestConnectDataAPI.as_view(),
        name='MailServerTestConnectDataAPI'
    ),
]
