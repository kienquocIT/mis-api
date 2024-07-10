from django.urls import path

from .views import ProjectList, ProjectDetail, ProjectUpdate, ProjectMemberAdd, ProjectMemberDetail, ProjectGroupList, \
    ProjectGroupDetail, ProjectWorkList, ProjectWorkDetail, ProjectUpdateOrder, ProjectTaskList, ProjectGroupListDD, \
    ProjectTaskDetail, ProjectWorkExpenseList, ProjectCreateBaseline, ProjectBaselineDetail

urlpatterns = [
    path('list', ProjectList.as_view(), name='ProjectList'),
    path('detail/<str:pk>', ProjectDetail.as_view(), name='ProjectDetail'),
    path('edit/<str:pk>', ProjectUpdate.as_view(), name='ProjectUpdate'),
    path('update-order/<str:pk>', ProjectUpdateOrder.as_view(), name='ProjectUpdateOrder'),
    # member
    path('<str:pk_pj>/member/add', ProjectMemberAdd.as_view(), name='ProjectMemberAdd'),
    path('<str:pk_pj>/member/detail/<str:pk_member>', ProjectMemberDetail.as_view(), name='ProjectMemberDetail'),
    # group
    path('group/list', ProjectGroupList.as_view(), name='ProjectGroupList'),
    path('group/list-dd', ProjectGroupListDD.as_view(), name='ProjectGroupListDD'),
    path('group/detail/<str:pk>', ProjectGroupDetail.as_view(), name='ProjectGroupDetail'),
    # work
    path('work/list', ProjectWorkList.as_view(), name='ProjectWorkList'),
    path('work/detail/<str:pk>', ProjectWorkDetail.as_view(), name='ProjectWorkDetail'),
    # list task map project
    path('assign-task-list', ProjectTaskList.as_view(), name='ProjectTaskList'),
    path('assign-task-link/<str:pk>', ProjectTaskDetail.as_view(), name='ProjectTaskDetail'),
    # work expense list
    path('work-expense-list', ProjectWorkExpenseList.as_view(), name='ProjectWorkExpenseList'),
    path('create-baseline/list', ProjectCreateBaseline.as_view(), name='ProjectCreateBaseline'),
    path('create-baseline/detail/<str:pk>', ProjectBaselineDetail.as_view(), name='ProjectBaselineDetail'),
]
