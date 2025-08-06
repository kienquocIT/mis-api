from django.urls import path

from apps.hrm.absenceexplanation.views import AbsenceExplanationList

urlpatterns = [
    path('absenceexplanation/list', AbsenceExplanationList.as_view(), name='AbsenceExplanationList'),
]
