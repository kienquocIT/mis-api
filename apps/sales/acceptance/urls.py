from django.urls import path

from .views import (FinalAcceptanceList, FinalAcceptanceDetail)

urlpatterns = [
    path('final-acceptance/list', FinalAcceptanceList.as_view(), name='FinalAcceptanceList'),
    path('final-acceptance/<str:pk>', FinalAcceptanceDetail.as_view(), name='FinalAcceptanceDetail'),
]
