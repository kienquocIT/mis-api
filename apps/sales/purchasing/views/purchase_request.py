from drf_yasg.utils import swagger_auto_schema

from apps.sales.distributionplan.models import DistributionPlan
from apps.sales.purchasing.models import PurchaseRequest, PurchaseRequestProduct
from apps.sales.purchasing.serializers import (
    PurchaseRequestListSerializer, PurchaseRequestCreateSerializer, PurchaseRequestDetailSerializer,
    PurchaseRequestProductListSerializer, PurchaseRequestUpdateSerializer,
    PurchaseRequestSaleListSerializer, SaleOrderListForPRSerializer, SaleOrderProductListForPRSerializer,
    DistributionPlanProductListForPRSerializer, DistributionPlanListForPRSerializer, ServiceOrderListForPRSerializer,
    ServiceOrderProductListForPRSerializer
)
from apps.sales.saleorder.models import SaleOrder
from apps.sales.serviceorder.models import ServiceOrder
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# main
class PurchaseRequestList(BaseListMixin, BaseCreateMixin):
    queryset = PurchaseRequest.objects
    filterset_fields = {
        'is_all_ordered': ['exact'],
        'system_status': ['exact'],
    }
    search_fields = [
        'title',
        'sale_order__title',
        'supplier__name',
    ]
    serializer_list = PurchaseRequestListSerializer
    serializer_detail = PurchaseRequestDetailSerializer
    serializer_create = PurchaseRequestCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        main_query = super().get_queryset().select_related(
            'supplier',
            'sale_order',
            'distribution_plan',
        )
        return self.get_queryset_custom_direct_page(main_query)

    @swagger_auto_schema(
        operation_summary="Purchase Request List",
        operation_description="Get Purchase Request List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaserequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Purchase Request",
        operation_description="Create new Purchase Request",
        request_body=PurchaseRequestCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaserequest', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class PurchaseRequestDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = PurchaseRequest.objects
    serializer_detail = PurchaseRequestDetailSerializer
    serializer_update = PurchaseRequestUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'supplier',
            'sale_order',
            'contact',
            'employee_inherit',
        )

    @swagger_auto_schema(
        operation_summary="Purchase Request detail",
        operation_description="Get Purchase Request detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaserequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Purchase Request update",
        operation_description="Update Purchase Request by ID",
        request_body=PurchaseRequestUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaserequest', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)


# related
class SaleOrderListForPR(BaseListMixin):
    queryset = SaleOrder.objects
    search_fields = [
        'title', 'code',
    ]
    filterset_fields = {
        'employee_inherit_id': ['exact', 'in'],
        'customer_id': ['exact'],
    }
    serializer_list = SaleOrderListForPRSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().filter(
            delivery_status__in=[0, 1, 2], system_status=3,
            is_done_purchase_request=False
        ).select_related(
            'employee_inherit',
            'employee_inherit__group'
        ).prefetch_related('sale_order_product_sale_order')

    @swagger_auto_schema(
        operation_summary="Sale Order List  For PR",
        operation_description="Get Sale Order List  For PR"
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class SaleOrderProductListForPR(BaseRetrieveMixin):
    queryset = SaleOrder.objects
    serializer_detail = SaleOrderProductListForPRSerializer

    @swagger_auto_schema(
        operation_summary="Sale Order Product List For PR",
        operation_description="SaleOrder Detail Product List For PR",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DistributionPlanListForPR(BaseListMixin):
    queryset = DistributionPlan.objects
    search_fields = [
        'title', 'code',
    ]
    filterset_fields = {}
    serializer_list = DistributionPlanListForPRSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().filter(system_status=3)

    @swagger_auto_schema(
        operation_summary="Distribution Plan list For PR",
        operation_description="Distribution Plan list For PR",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DistributionPlanProductListForPR(BaseRetrieveMixin):
    queryset = DistributionPlan.objects
    serializer_detail = DistributionPlanProductListForPRSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related(
            'product',
            'product__general_uom_group',
            'product__general_uom_group__uom_reference',
        )

    @swagger_auto_schema(operation_summary='Product List Distribution Plan')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ServiceOrderListForPR(BaseListMixin):
    queryset = ServiceOrder.objects
    search_fields = [
        'title', 'code',
    ]
    filterset_fields = {}
    serializer_list = ServiceOrderListForPRSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().filter(system_status=3, is_done_purchase_request=False)

    @swagger_auto_schema(
        operation_summary="Service Order list For PR",
        operation_description="Service Order list For PR",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ServiceOrderProductListForPR(BaseRetrieveMixin):
    queryset = ServiceOrder.objects
    serializer_detail = ServiceOrderProductListForPRSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related('service_details')

    @swagger_auto_schema(
        operation_summary="Service Order Product list For PR",
        operation_description="Service Order Product list For PR",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class PurchaseRequestProductList(BaseListMixin):
    queryset = PurchaseRequestProduct.objects
    filterset_fields = {
        'purchase_request_id': ['in', 'exact'],
    }
    serializer_list = PurchaseRequestProductListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super().get_queryset().filter(remain_for_purchase_order__gt=0).select_related(
            'purchase_request',
            'product',
            'product__general_product_category',
            'product__general_uom_group',
            'product__sale_default_uom',
            'product__sale_tax',
            'product__sale_currency_using',
            'product__purchase_default_uom',
            'product__purchase_tax',
            'uom',
            'uom__group',
            'uom__group__uom_reference',
            'tax',
        ).prefetch_related(
            'product__general_product_types_mapped'
        ).order_by('-purchase_request__date_created')

    @swagger_auto_schema(
        operation_summary="Purchase Request Product List",
        operation_description="Get Purchase Request Product List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# PR list use for other apps
class PurchaseRequestSaleList(BaseListMixin, BaseCreateMixin):
    queryset = PurchaseRequest.objects
    filterset_fields = {
        'is_all_ordered': ['exact'],
        'system_status': ['exact'],
        'sale_order__opportunity__is_deal_close': ['exact'],
        'request_for': ['exact', 'in'],
    }
    search_fields = [
        'title',
        'sale_order__title',
        'supplier__name',
    ]
    serializer_list = PurchaseRequestSaleListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'sale_order',
            'sale_order__opportunity',
        )

    @swagger_auto_schema(
        operation_summary="Purchase Request For Sale List",
        operation_description="Get Purchase Request For Sale List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
