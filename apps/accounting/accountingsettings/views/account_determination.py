from drf_yasg.utils import swagger_auto_schema
from apps.accounting.accountingsettings.models.account_determination import (
    JEDocumentType, JEPostingRule, JEPostingGroup, JEGroupAssignment, JEGLAccountMapping
)
from apps.accounting.accountingsettings.serializers.account_determination import (
    JEDocumentTypeListSerializer, JEDocumentTypeUpdateSerializer,
    JEPostingRuleListSerializer, JEPostingGroupListSerializer, JEGroupAssignmentListSerializer,
    JEGLAccountMappingListSerializer
)
from apps.shared import BaseListMixin, BaseUpdateMixin, mask_view


class JEDocumentTypeList(BaseListMixin):
    queryset = JEDocumentType.objects
    search_fields = ['title', 'code']
    serializer_list = JEDocumentTypeListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="JE Document Type List",
        operation_description="JE Document Type List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class JEDocumentTypeDetail(BaseUpdateMixin):
    queryset = JEDocumentType.objects
    serializer_update = JEDocumentTypeUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update JE Document Type",
        request_body=JEDocumentTypeUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class JEPostingGroupList(BaseListMixin):
    queryset = JEPostingGroup.objects
    search_fields = ['title', 'code', 'posting_group_type']
    serializer_list = JEPostingGroupListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="JE Posting Group List",
        operation_description="JE Posting Group List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class JEGroupAssignmentList(BaseListMixin):
    queryset = JEGroupAssignment.objects
    search_fields = ['posting_group__code']
    serializer_list = JEGroupAssignmentListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="JE Group Assignment List",
        operation_description="JE Group Assignment List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class JEGLAccountMappingList(BaseListMixin):
    queryset = JEGLAccountMapping.objects
    search_fields = ['posting_group__code', 'role_key']
    serializer_list = JEGLAccountMappingListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="JE GL Account Mapping List",
        operation_description="JE GL Account Mapping List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class JEPostingRuleList(BaseListMixin):
    queryset = JEPostingRule.objects
    search_fields = ['title', 'code']
    serializer_list = JEPostingRuleListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="JE Posting Rule List",
        operation_description="JE Posting Rule List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
