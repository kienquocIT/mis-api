from django.urls import path

from apps.core.account.views import UserList

urlpatterns = [
    path('users', UserList.as_view(), name='UserList'),
]
