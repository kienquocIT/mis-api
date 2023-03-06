from django.urls import path

from apps.core.account.views import UserList, UserDetail, CompanyUserDetail

urlpatterns = [
    path('users', UserList.as_view(), name='UserList'),
    path('user/<str:pk>', UserDetail.as_view(), name='UserDetail'),

    # update company of user
    path('user-company/<str:pk>', CompanyUserDetail.as_view(), name='CompanyUserDetail'),
]
