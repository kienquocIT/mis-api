from django.urls import path

from apps.hrm.absenceexplanation.views import AbsenceExplanationList, AbsenceExplanationDetail

urlpatterns = [
    path('list', AbsenceExplanationList.as_view(), name='AbsenceExplanationList'),
    path('detail/<str:pk>', AbsenceExplanationDetail.as_view(), name='AbsenceExplanationDetail')
]
