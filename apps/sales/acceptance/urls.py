from django.urls import path

from .views import (FinalAcceptanceList)

urlpatterns = [
    path('final-acceptance/list', FinalAcceptanceList.as_view(), name='FinalAcceptanceList'),
]
