from django.urls import path
from apps.accounting.accountingsettings.views.asset_category import AssetCategoryList, AssetCategoryDetail
from apps.accounting.accountingsettings.views import InitialBalanceList, InitialBalanceDetail
from apps.accounting.accountingsettings.views.chart_of_account import (
    ChartOfAccountsList, get_chart_of_accounts_summarize
)
from apps.accounting.accountingsettings.views.account_determination import (
    JEDocumentTypeList, JEDocumentTypeDetail, JEPostingRuleList, JEPostingGroupList, JEGroupAssignmentList,
    JEGLAccountMappingList, get_je_amount_source, get_je_group_type, JEPostingGroupDetail, JEPostingGroupRoleKeyList,
    JEGLAccountMappingDetail, get_je_document_type, JEPostingRuleDetail,
)
from apps.accounting.accountingsettings.views.dimension import (
    DimensionDefinitionList, DimensionDefinitionDetail,
    DimensionDefinitionWithValueList, DimensionValueList, DimensionValueDetail, DimensionSyncConfigApplicationList,
    DimensionSyncConfigList, DimensionSyncConfigDetail, DimensionListForAccountingAccount, DimensionAccountMapList,
    DimensionAccountMapDetail, DimensionSplitTemplateList, DimensionSplitTemplateDetail,
)


urlpatterns = [
    path('chart-of-accounts/list', ChartOfAccountsList.as_view(), name='ChartOfAccountsList'),
    path('get_chart_of_accounts_summarize', get_chart_of_accounts_summarize, name='get_chart_of_accounts_summarize'),
    path('je-document-type/list', JEDocumentTypeList.as_view(), name='JEDocumentTypeList'),
    path('je-document-type/detail/<str:pk>', JEDocumentTypeDetail.as_view(), name='JEDocumentTypeDetail'),
    path('je-posting-group/list', JEPostingGroupList.as_view(), name='JEPostingGroupList'),
    path('je-posting-group/detail/<str:pk>', JEPostingGroupDetail.as_view(), name='JEPostingGroupDetail'),
    path('je-posting-group-role-key/list', JEPostingGroupRoleKeyList.as_view(), name='JEPostingGroupRoleKeyList'),
    path('je-group-assignment/list', JEGroupAssignmentList.as_view(), name='JEGroupAssignmentList'),
    path('je-gl-account-mapping/list', JEGLAccountMappingList.as_view(), name='JEGLAccountMappingList'),
    path('je-gl-account-mapping/detail/<str:pk>', JEGLAccountMappingDetail.as_view(), name='JEGLAccountMappingDetail'),
    path('je-posting-rule/list', JEPostingRuleList.as_view(), name='JEPostingRuleList'),
    path('je-posting-rule/detail/<str:pk>', JEPostingRuleDetail.as_view(), name='JEPostingRuleDetail'),
    path('get-je-document-type', get_je_document_type, name='get_je_document_type'),
    path('get-je-group-type', get_je_group_type, name='get_je_group_type'),
    path('get-je-amount-source', get_je_amount_source, name='get_je_amount_source'),
    path('get-je-group-type', get_je_group_type, name='get_je_group_type'),
] + [
    # Dimension
    path('dimension-definition/list', DimensionDefinitionList.as_view(), name='DimensionDefinitionList'),
    path(
        'dimension-definition/detail/<str:pk>',
         DimensionDefinitionDetail.as_view(),
         name='DimensionDefinitionDetail'
    ),
    path(
        'dimension-definition-values/<str:pk>',
         DimensionDefinitionWithValueList.as_view(),
         name='DimensionDefinitionWithValueList'
    ),
    path('dimension-value/list', DimensionValueList.as_view(), name='DimensionValueList'),
    path('dimension-value/detail/<str:pk>', DimensionValueDetail.as_view(), name='DimensionValueDetail'),
    path('dimension-sync-config/application-list', DimensionSyncConfigApplicationList.as_view(),
         name='DimensionSyncConfigApplicationList'),
    path('dimension-sync-config/list', DimensionSyncConfigList.as_view(),
         name='DimensionSyncConfigList'),
    path('dimension-sync-config/detail/<str:pk>', DimensionSyncConfigDetail.as_view(),
         name='DimensionSyncConfigDetail'),
    path('dimension-for-account/detail/<str:pk>', DimensionListForAccountingAccount.as_view(),
         name='DimensionListForAccountingAccount'),
    path('dimension-account-map/list', DimensionAccountMapList.as_view(), name='DimensionAccountMapList'),
    path('dimension-account-map/detail/<str:pk>', DimensionAccountMapDetail.as_view(),
         name='DimensionAccountMapDetail'),
] + [
    path('asset-category/list', AssetCategoryList.as_view(), name='AssetCategoryList'),
    path('asset-category/detail/<str:pk>', AssetCategoryDetail.as_view(), name='AssetCategoryDetail'),
] + [
      # Dimension
      path('dimension-definition/list', DimensionDefinitionList.as_view(), name='DimensionDefinitionList'),
      path(
          'dimension-definition/detail/<str:pk>',
          DimensionDefinitionDetail.as_view(),
          name='DimensionDefinitionDetail'
      ),
      path(
          'dimension-definition-values/<str:pk>',
          DimensionDefinitionWithValueList.as_view(),
          name='DimensionDefinitionWithValueList'
      ),
      path('dimension-value/list', DimensionValueList.as_view(), name='DimensionValueList'),
      path('dimension-value/detail/<str:pk>', DimensionValueDetail.as_view(), name='DimensionValueDetail'),
      path(
          'dimension-sync-config/application-list', DimensionSyncConfigApplicationList.as_view(),
          name='DimensionSyncConfigApplicationList'
      ),
      path(
          'dimension-sync-config/list', DimensionSyncConfigList.as_view(),
          name='DimensionSyncConfigList'
      ),
      path(
          'dimension-sync-config/detail/<str:pk>', DimensionSyncConfigDetail.as_view(),
          name='DimensionSyncConfigDetail'
      ),
      path(
          'dimension-for-account/detail/<str:pk>', DimensionListForAccountingAccount.as_view(),
          name='DimensionListForAccountingAccount'
      ),
      path('dimension-account-map/list', DimensionAccountMapList.as_view(), name='DimensionAccountMapList'),
      path(
          'dimension-account-map/detail/<str:pk>', DimensionAccountMapDetail.as_view(),
          name='DimensionAccountMapDetail'
      ),
      path(
          'dimension-split-template/list', DimensionSplitTemplateList.as_view(),
          name='DimensionSplitTemplateList'
      ),
      path(
          'dimension-split-template/detail/<str:pk>', DimensionSplitTemplateDetail.as_view(),
          name='DimensionSplitTemplateDetail'
      ),
    ] + [
      # Initial balance
      path('initial-balance/list', InitialBalanceList.as_view(), name='InitialBalanceList'),
      path('initial-balance/detail/<str:pk>', InitialBalanceDetail.as_view(), name='InitialBalanceDetail')
]
