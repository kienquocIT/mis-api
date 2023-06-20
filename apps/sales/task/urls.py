from django.urls import path

from apps.sales.task.views.config import TaskConfigDetail

urlpatterns = [
    path('config', TaskConfigDetail.as_view(), name='TaskConfigDetail'),
]
