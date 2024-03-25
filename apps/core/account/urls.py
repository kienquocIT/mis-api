from django.urls import path

from apps.core.account.views import (
    UserList, UserDetail, CompanyUserDetail, UserOfTenantList, UserDetailResetPassword,
    UserSendWelcome,
)

urlpatterns = [
    path('users', UserList.as_view(), name='UserList'),
    path('user/<str:pk>', UserDetail.as_view(), name='UserDetail'),
    path('user/<str:pk>/mail-welcome', UserSendWelcome.as_view(), name='UserSendWelcome'),
    path('user/<str:pk>/reset-password', UserDetailResetPassword.as_view(), name='UserDetailResetPassword'),

    # update company of user
    path('user-company/<str:pk>', CompanyUserDetail.as_view(), name='CompanyUserDetail'),
    path('user-tenant', UserOfTenantList.as_view(), name='UserOfTenantList'),
]
