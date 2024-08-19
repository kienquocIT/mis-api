from drf_yasg.utils import swagger_auto_schema

from apps.sales.contract.models import ContractApproval
from apps.sales.contract.serializers.contract import ContractListSerializer, ContractCreateSerializer, \
    ContractDetailSerializer, ContractUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class ContractList(BaseListMixin, BaseCreateMixin):
    queryset = ContractApproval.objects
    search_fields = ['title', 'code']
    filterset_fields = {}
    serializer_list = ContractListSerializer
    serializer_create = ContractCreateSerializer
    serializer_detail = ContractListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Contract List",
        operation_description="Get Contract List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='contract', model_code='contractapproval', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Contract",
        operation_description="Create New Contract",
        request_body=ContractCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        employee_require=True,
        label_code='contract', model_code='contractapproval', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class ContractDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ContractApproval.objects
    serializer_detail = ContractDetailSerializer
    serializer_update = ContractUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Contract detail",
        operation_description="Get Contract detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='contract', model_code='contractapproval', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Contract",
        operation_description="Update Contract by ID",
        request_body=ContractUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='contract', model_code='contractapproval', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, pk, **kwargs)
