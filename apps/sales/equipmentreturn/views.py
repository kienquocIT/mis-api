from drf_yasg.utils import swagger_auto_schema
from apps.sales.equipmentloan.models import EquipmentLoan
from apps.sales.equipmentreturn.models import EquipmentReturn
from apps.sales.equipmentreturn.serializers import (
    EquipmentReturnListSerializer, EquipmentReturnCreateSerializer,
    EquipmentReturnDetailSerializer, EquipmentReturnUpdateSerializer, EREquipmentLoanListByAccountSerializer
)
from apps.shared import BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, mask_view


__all__ = [
    'EquipmentReturnList',
    'EquipmentReturnDetail',
    'EREquipmentLoanListByAccount',
]

# main
class EquipmentReturnList(BaseListMixin, BaseCreateMixin):
    queryset = EquipmentReturn.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = EquipmentReturnListSerializer
    serializer_create = EquipmentReturnCreateSerializer
    serializer_detail = EquipmentReturnDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Equipment Return list",
        operation_description="Equipment Return list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='equipmentreturn', model_code='equipmentreturn', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Product Modification",
        operation_description="Create new Product Modification",
        request_body=EquipmentReturnCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='equipmentreturn', model_code='equipmentreturn', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class EquipmentReturnDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = EquipmentReturn.objects  # noqa
    serializer_detail = EquipmentReturnDetailSerializer
    serializer_update = EquipmentReturnUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(operation_summary='Detail Equipment Return')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='equipmentreturn', model_code='equipmentreturn', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Product Modification", request_body=EquipmentReturnUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='equipmentreturn', model_code='equipmentreturn', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)

# related
class EREquipmentLoanListByAccount(BaseListMixin):
    queryset = EquipmentLoan.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = EREquipmentLoanListByAccountSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        if 'account_mapped_id' in self.request.query_params:
            return super().get_queryset().filter(
                system_status=3,
                account_mapped_id=self.request.query_params.get('account_mapped_id')
            ).prefetch_related(
                'equipment_loan_items',
                'equipment_loan_items__equipment_loan_item_detail',
            )
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Equipment Loan List By Account",
        operation_description="Equipment Loan List By Account",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
