from django.urls import path

from .views import ProjectList, ProjectDetail, ProjectUpdate, ProjectMemberAdd, ProjectMemberDetail, ProjectGroupList, \
    ProjectGroupDetail, ProjectWorkList, ProjectWorkDetail

urlpatterns = [
    path('list', ProjectList.as_view(), name='ProjectList'),
    path('detail/<str:pk>', ProjectDetail.as_view(), name='ProjectDetail'),
    path('edit/<str:pk>', ProjectUpdate.as_view(), name='ProjectUpdate'),
    # member
    path('<str:pk_pj>/member/add', ProjectMemberAdd.as_view(), name='ProjectMemberAdd'),
    path('<str:pk_pj>/member/detail/<str:pk_member>', ProjectMemberDetail.as_view(), name='ProjectMemberDetail'),
    # group
    path('group/list', ProjectGroupList.as_view(), name='ProjectGroupList'),
    path('group/detail/<str:pk>', ProjectGroupDetail.as_view(), name='ProjectGroupDetail'),
    # work
    path('work/list', ProjectWorkList.as_view(), name='ProjectWorkList'),
    path('work/detail/<str:pk>', ProjectWorkDetail.as_view(), name='ProjectWorkDetail'),

]
