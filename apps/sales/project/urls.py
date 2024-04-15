from django.urls import path

from .views import ProjectList, ProjectDetail, ProjectUpdate, ProjectMemberAdd, ProjectMemberDetail, ProjectGroupList, \
    ProjectGroupDetail, ProjectWorkList

urlpatterns = [
    path('list', ProjectList.as_view(), name='ProjectList'),
    path('detail/<str:pk>', ProjectDetail.as_view(), name='ProjectDetail'),
    path('edit/<str:pk>', ProjectUpdate.as_view(), name='ProjectUpdate'),
    path('<str:pk_pj>/member/add', ProjectMemberAdd.as_view(), name='ProjectMemberAdd'),
    path('<str:pk_pj>/member/detail/<str:pk_member>', ProjectMemberDetail.as_view(), name='ProjectMemberDetail'),
    path('group/list', ProjectGroupList.as_view(), name='ProjectGroupList'),
    path('<str:pk_pj>/group/detail/<str:pk_member>', ProjectGroupDetail.as_view(), name='ProjectGroupDetail'),
    path('work/list', ProjectWorkList.as_view(), name='ProjectWorkList'),
    path('<str:pk_pj>/work/detail/<str:pk_member>', ProjectGroupDetail.as_view(), name='ProjectGroupDetail'),

]
