from django.urls import path

from apps.core.mailer.views import (
    MailerFeatureList, MailerFeatureDetail, MailerSystemGetByCode, MailerSystemDetail,
    MailerServerConfigGet, MailerServerConfigDetail, MailServerTestConnectAPI, MailServerTestConnectDataAPI,
    MailerFeatureAppList, MailTemplateByApplication,
)

urlpatterns = [
    path('system/get/<str:system_code>', MailerSystemGetByCode.as_view(), name='MailerSystemGetByCode'),
    path('system/detail/<str:pk>', MailerSystemDetail.as_view(), name='MailerSystemDetail'),
    path('config/get', MailerServerConfigGet.as_view(), name='MailerServerConfigGet'),
    path('config/detail/<str:pk>', MailerServerConfigDetail.as_view(), name='MailerServerConfigDetail'),
    path('config/detail/<str:pk>/connection/test', MailServerTestConnectAPI.as_view(), name='MailServerTestConnectAPI'),
    path(
        'config/detail/<str:pk>/connection/test/data', MailServerTestConnectDataAPI.as_view(),
        name='MailServerTestConnectDataAPI'
    ),
    path('feature/list', MailerFeatureList.as_view(), name='MailerConfigList'),
    path('feature/list/<str:application_id>', MailTemplateByApplication.as_view(), name='MailTemplateByApplication'),
    path('feature/detail/<str:pk>', MailerFeatureDetail.as_view(), name='MailerConfigDetail'),
    path('feature/app/list', MailerFeatureAppList.as_view(), name='MailerFeatureAppList'),
]
