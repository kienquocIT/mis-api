from django.urls import path
from apps.core.company.views import (
    CompanyList,
    CompanyDetail, CompanyUploadLogo,
    CompanyListOverview,
    CompanyUserNotMapEmployeeList, CompanyOverviewDetail,
    CompanyConfigDetail, RestoreDefaultOpportunityConfigStage,
)


urlpatterns = [
    path('config', CompanyConfigDetail.as_view(), name='CompanyConfigDetail'),
    path('list', CompanyList.as_view(), name='CompanyList'),
    path('<str:pk>', CompanyDetail.as_view(), name='CompanyDetail'),
    path('<str:pk>/logo', CompanyUploadLogo.as_view(), name='CompanyUploadLogo'),

    # overview company page
    path('overview/list', CompanyListOverview.as_view(), name='CompanyListOverview'),
    path('overview/<str:pk>/<int:option>', CompanyOverviewDetail.as_view(), name='CompanyOverviewDetail'),
    path('user/available', CompanyUserNotMapEmployeeList.as_view(), name='CompanyUserNotMapEmployeeList'),
    path(
        'default-opportunity-stage/<str:pk>',
        RestoreDefaultOpportunityConfigStage.as_view(),
        name='RestoreDefaultOpportunityConfigStage'
    ),
]
