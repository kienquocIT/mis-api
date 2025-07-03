from django.urls import path

from apps.hrm.attandance.views import ShiftMasterDataList

urlpatterns = [
    path('shift/list', ShiftMasterDataList.as_view(), name='ShiftMasterDataList'),
]
