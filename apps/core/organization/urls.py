from django.urls import path

from apps.core.organization.views import GroupLevelList, GroupLevelDetail, GroupDetail, GroupList, RoleList, RoleDetail

urlpatterns = [
    path('levels', GroupLevelList.as_view(), name='GroupLevelList'),
    path("level/<str:pk>", GroupLevelDetail.as_view(), name="GroupLevelDetail"),
    path('groups', GroupList.as_view(), name='GroupList'),
    path("group/<str:pk>", GroupDetail.as_view(), name="GroupDetail"),

    path("roles", RoleList.as_view(), name="RoleList"),
    path("role/<str:pk>", RoleDetail.as_view(), name="RoleDetail"),
]
