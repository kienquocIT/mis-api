from django.urls import path

from apps.core.process.views import FunctionProcessList, ProcessDetail, SkipProcessStep, SetCurrentProcessStep

urlpatterns = [
    path('', ProcessDetail.as_view(), name='ProcessDetail'),
    path('function/list', FunctionProcessList.as_view(), name='FunctionProcessList'),

    path('step/skip/<str:pk>', SkipProcessStep.as_view(), name='SkipProcessStep'),
    path('step/set-current/<str:pk>', SetCurrentProcessStep.as_view(), name='SetCurrentProcessStep'),
]
