from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.accounting.accountingsettings.data_list import DOCUMENT_TYPE_LIST, ALLOWED_AMOUNT_SOURCES_MAP
from apps.accounting.accountingsettings.models.account_determination import (
    JEDocumentType, JEPostingRule, JEPostingGroup, JEGroupAssignment, JEGLAccountMapping, AMOUNT_SOURCE_CHOICES,
    GROUP_TYPE_CHOICES, JEPostingGroupRoleKey, JE_DOCUMENT_TYPE_APP
)
from apps.accounting.accountingsettings.serializers import JEGLAccountMappingCreateSerializer, \
    JEGLAccountMappingDetailSerializer
from apps.accounting.accountingsettings.serializers.account_determination import (
    JEDocumentTypeListSerializer, JEDocumentTypeUpdateSerializer,
    JEPostingRuleListSerializer, JEPostingGroupListSerializer, JEGroupAssignmentListSerializer,
    JEGLAccountMappingListSerializer, JEPostingGroupCreateSerializer, JEPostingGroupDetailSerializer,
    JEPostingGroupUpdateSerializer, JEPostingGroupRoleKeyListSerializer, JEGLAccountMappingUpdateSerializer,
    JEPostingRuleCreateSerializer, JEPostingRuleDetailSerializer, JEPostingRuleUpdateSerializer
)
from apps.shared import BaseListMixin, BaseUpdateMixin, BaseCreateMixin, BaseDestroyMixin, mask_view


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
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='view',
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
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

# Posting group
class JEPostingGroupList(BaseListMixin, BaseCreateMixin):
    queryset = JEPostingGroup.objects
    search_fields = ['title', 'code', 'posting_group_type']
    filterset_fields = {
        "is_active": ["exact"],
        "posting_group_type": ["exact"],
    }
    serializer_list = JEPostingGroupListSerializer
    serializer_create = JEPostingGroupCreateSerializer
    serializer_detail = JEPostingGroupDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="JE Posting Group List",
        operation_description="JE Posting Group List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create JE Posting Group",
        operation_description="Create new JE Posting Group",
        request_body=JEPostingGroupCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class JEPostingGroupDetail(BaseUpdateMixin, BaseDestroyMixin):
    queryset = JEPostingGroup.objects
    serializer_update = JEPostingGroupUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update JE Posting Group",
        request_body=JEPostingGroupUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete JE Posting Group",
        operation_description="Delete JE Posting Group by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='delete',
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class JEGroupAssignmentList(BaseListMixin):
    queryset = JEGroupAssignment.objects
    search_fields = ['posting_group__code']
    serializer_list = JEGroupAssignmentListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="JE Group Assignment List",
        operation_description="JE Group Assignment List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

# Posting Group - Role Key
class JEPostingGroupRoleKeyList(BaseListMixin):
    queryset = JEPostingGroupRoleKey.objects
    search_fields = ['posting_group__code', 'role_key']
    filterset_fields = {
        "posting_group_id": ["exact"]
    }
    serializer_list = JEPostingGroupRoleKeyListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="JE Posting Group Role key List",
        operation_description="JE Posting Group Role key List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

# GL account mapping
class JEGLAccountMappingList(BaseListMixin, BaseCreateMixin):
    queryset = JEGLAccountMapping.objects
    search_fields = ['posting_group__code', 'role_key']
    serializer_list = JEGLAccountMappingListSerializer
    serializer_create = JEGLAccountMappingCreateSerializer
    serializer_detail = JEGLAccountMappingDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="JE GL Account Mapping List",
        operation_description="JE GL Account Mapping List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create JE GL Account Mapping",
        operation_description="Create new JE GL Account Mapping",
        request_body=JEGLAccountMappingCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class JEGLAccountMappingDetail(BaseUpdateMixin, BaseDestroyMixin):
    queryset = JEGLAccountMapping.objects
    serializer_update = JEGLAccountMappingUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update GL Account Mapping",
        request_body=JEGLAccountMappingUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete GL Account Mapping",
        operation_description="Delete GL Account Mapping by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='delete',
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Posting rule
class JEPostingRuleList(BaseListMixin, BaseCreateMixin):
    queryset = JEPostingRule.objects
    search_fields = ['title', 'code']
    serializer_list = JEPostingRuleListSerializer
    serializer_create = JEPostingRuleCreateSerializer
    serializer_detail = JEPostingRuleDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="JE Posting Rule List",
        operation_description="JE Posting Rule List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create JE Posting Rule",
        operation_description="Create new JE Posting Rule",
        request_body=JEPostingRuleCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class JEPostingRuleDetail(BaseUpdateMixin, BaseDestroyMixin):
    queryset = JEPostingRule.objects
    serializer_update = JEPostingRuleUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update JE Posting Rule",
        request_body=JEPostingRuleUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete JE Posting Rule",
        operation_description="Delete JE Posting Rule by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='postingengine', model_code='postingengine', perm_code='delete',
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@swagger_auto_schema(
    method='get',
    operation_summary="Document type choices",
    operation_description="Document type choices",
)
@api_view(['GET'])
def get_je_document_type(request, *args, **kwargs):
    je_document_type = []
    app_title_map = dict(JE_DOCUMENT_TYPE_APP)
    for _, code, app_code, _ in DOCUMENT_TYPE_LIST:
        title = app_title_map.get(app_code, '')
        je_document_type.append((app_code, code, title))
    return Response({
        'result': {
            'je_document_type': je_document_type,
        }
    })


@swagger_auto_schema(
    method='get',
    operation_summary="Group type choices",
    operation_description="Group type choices",
)
@api_view(['GET'])
def get_je_group_type(request, *args, **kwargs):
    return Response({
        'result': {
            'je_group_type': GROUP_TYPE_CHOICES,
        }
    })


@swagger_auto_schema(
    method='get',
    operation_summary="Amount source choices",
    operation_description="Amount source choices",
)
@api_view(['GET'])
def get_je_amount_source(request, *args, **kwargs):
    document_type_app_code = request.query_params.get('document_type_app_code')
    je_amount_source = []
    if document_type_app_code:
        allowed_keys = ALLOWED_AMOUNT_SOURCES_MAP.get(document_type_app_code)
        if allowed_keys:
            je_amount_source = [
                {
                    'code': code,
                    'description': f"{code} - {description}",
                }
                for code, description in AMOUNT_SOURCE_CHOICES
                if code in allowed_keys
            ]
    return Response({
        'result': je_amount_source
    })
