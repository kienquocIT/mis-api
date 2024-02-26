from django.urls import path

from apps.core.printer.views import (
    PrintTemplateList, PrintTemplateDetail, PrintTemplateUsingDetail,
    PrintTemplateApplicationList,
)

urlpatterns = [
    path('apps', PrintTemplateApplicationList.as_view(), name='PrintTemplateApplicationList'),
    path('list', PrintTemplateList.as_view(), name='PrintTemplateList'),
    path('detail/<uuid:pk>', PrintTemplateDetail.as_view(), name='PrintTemplateDetail'),
    path('using/<uuid:application_id>', PrintTemplateUsingDetail.as_view(), name='PrintTemplateUsingDetail'),
]
