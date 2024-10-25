from django.urls import path

from .views import (
    ProjectList, ProjectDetail, ProjectUpdate, ProjectMemberAdd, ProjectMemberDetail, ProjectGroupList,
    ProjectGroupDetail, ProjectWorkList, ProjectWorkDetail, ProjectUpdateOrder, ProjectTaskList, ProjectGroupListDD,
    ProjectTaskDetail, ProjectWorkExpenseList, ProjectListBaseline, ProjectBaselineDetail, ProjectBaselineUpdate,
    ProjectConfigDetail, ProjectExpenseHomeList, ProjectNewsList, ProjectNewsCommentList, ProjectNewsCommentDetail,
    ProjectNewsCommentDetailFlows
)


urlpatterns = [
    path('config', ProjectConfigDetail.as_view(), name='ProjectConfigDetail'),
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
    path('project-expense-home-list', ProjectExpenseHomeList.as_view(), name='ProjectExpenseHomeList'),
    # baseline workflow
    path('baseline/list', ProjectListBaseline.as_view(), name='ProjectListBaseline'),
    path('baseline/detail/<str:pk>', ProjectBaselineDetail.as_view(), name='ProjectBaselineDetail'),
    path('baseline/edit/<str:pk>', ProjectBaselineUpdate.as_view(), name='ProjectBaselineUpdate'),

    # news
    path('news', ProjectNewsList.as_view(), name='ProjectNewsList'),
    path('news/comment/<str:pk>', ProjectNewsCommentDetail.as_view(), name='ProjectNewsCommentDetail'),
    path('news/comment/<str:pk>/flows', ProjectNewsCommentDetailFlows.as_view(), name='ProjectNewsCommentDetailFlows'),
    path('new/<str:news_id>/comments', ProjectNewsCommentList.as_view(), name='ProjectNewsCommentList'),
]
