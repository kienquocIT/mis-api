from django.urls import path

from apps.core.web_builder.views import PageBuilderList, PageBuilderDetail, PageBuilderViewPathSub

urlpatterns = [
    path('page-list', PageBuilderList.as_view(), name='PageBuilderList'),
    path('page/<str:pk>', PageBuilderDetail.as_view(), name='PageBuilderDetail'),
    path(
        'page/<str:pk_tenant>/<str:pk_company>/<str:path_sub>/viewer',
        view=PageBuilderViewPathSub.as_view(), name='PageBuilderViewPathSub'
    ),
]
