from django.urls import path

from apps.core.mailer.views import (
    MailerConfigList, MailerConfigDetail, MailerSystemGetByCode, MailerSystemDetail,
)

urlpatterns = [
    path('list', MailerConfigList.as_view(), name='MailerConfigList'),
    path('detail/<str:pk>', MailerConfigDetail.as_view(), name='MailerConfigDetail'),
    path('system/get/<str:system_code>', MailerSystemGetByCode.as_view(), name='MailerSystemGetByCode'),
    path('system/detail/<str:pk>', MailerSystemDetail.as_view(), name='MailerSystemDetail'),
]
