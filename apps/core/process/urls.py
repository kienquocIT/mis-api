from django.urls import path

from apps.core.process.views import (
    ProcessConfigList, ProcessConfigDetail, ProcessConfigReadyList,
    ProcessRuntimeOfMeList, ProcessRuntimeList, ProcessRuntimeDetail, ProcessRuntimeStagesAppControl,
    ProcessStagesAppsOfMeList, ProcessRuntimeDataMatch, ProcessRuntimeMembers, ProcessRuntimeMemberDetail,
)

urlpatterns = [
    path('config/list', ProcessConfigList.as_view(), name='ProcessConfigList'),
    path('config/list/ready', ProcessConfigReadyList.as_view(), name='ProcessConfigReadyList'),
    path('config/detail/<str:pk>', ProcessConfigDetail.as_view(), name='ProcessConfigDetail'),

    path('runtime/list/me', ProcessRuntimeOfMeList.as_view(), name='ProcessRuntimeOfMeList'),
    path('runtime/data-match', ProcessRuntimeDataMatch.as_view(), name='ProcessRuntimeDataMatch'),
    path('runtime/stages-apps/me', ProcessStagesAppsOfMeList.as_view(), name='ProcessStagesAppsOfMeList'),
    path('runtime/list', ProcessRuntimeList.as_view(), name='ProcessRuntimeList'),
    path('runtime/detail/<str:pk>', ProcessRuntimeDetail.as_view(), name='ProcessRuntimeDetail'),
    path('runtime/detail/<str:process_id>/members', ProcessRuntimeMembers.as_view(), name='ProcessRuntimeMembers'),
    path(
        'runtime/app/<str:pk>',
        ProcessRuntimeStagesAppControl.as_view(),
        name='ProcessRuntimeStagesAppComplete'
    ),
    path('runtime/member/<str:pk>', ProcessRuntimeMemberDetail.as_view(), name='ProcessRuntimeMemberDetail'),
]
