from django.urls import path

from apps.core.account.views import UserList, UserDetail
import uuid

urlpatterns = [
    path('users', UserList.as_view(), name='UserList'),
    path('user/<str:pk>', UserDetail.as_view(), name='UserDetail'),
]
