from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.quotation.models import Quotation, QuotationExpense, QuotationAppConfig, QuotationIndicatorConfig, \
    QuotationProduct, QuotationCost
from apps.sales.quotation.serializers.quotation_config import QuotationConfigDetailSerializer, \
    QuotationConfigUpdateSerializer
from apps.sales.quotation.serializers.quotation_indicator import IndicatorListSerializer, IndicatorCreateSerializer, \
    IndicatorUpdateSerializer, IndicatorCompanyRestoreSerializer
from apps.sales.quotation.serializers.quotation_serializers import QuotationListSerializer, QuotationCreateSerializer, \
    QuotationDetailSerializer, QuotationUpdateSerializer, QuotationExpenseListSerializer,\
    QuotationListSerializerForCashOutFlow
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class QuotationList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = Quotation.objects
    filterset_fields = {
        'opportunity': ['exact', 'isnull'],
        'employee_inherit': ['exact'],
        'opportunity__sale_order': ['exact', 'isnull'],
        'opportunity__is_close_lost': ['exact'],
        'opportunity__is_deal_close': ['exact'],
        'system_status': ['in'],
    }
    serializer_list = QuotationListSerializer
    serializer_create = QuotationCreateSerializer
    serializer_detail = QuotationListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    # create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "opportunity",
            "employee_inherit",
        )

    @swagger_auto_schema(
        operation_summary="Quotation List",
        operation_description="Get Quotation List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='quotation', model_code='quotation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Quotation",
        operation_description="Create new Quotation",
        request_body=QuotationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        label_code='quotation', model_code='quotation', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class QuotationDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = Quotation.objects
    serializer_detail = QuotationDetailSerializer
    serializer_update = QuotationUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "opportunity__customer",
            "customer",
            "contact",
            "payment_term",
            "customer__payment_term_customer_mapped",
            "employee_inherit",
        ).prefetch_related(
            Prefetch(
                "quotation_product_quotation",
                queryset=QuotationProduct.objects.select_related(
                    "product",
                    'product__general_product_category',
                    'product__general_uom_group',
                    "product__sale_default_uom",
                    "product__sale_tax",
                    "product__sale_currency_using",
                    "unit_of_measure",
                    "tax",
                    "promotion",
                    "shipping",
                ),
            ),
            Prefetch(
                "quotation_cost_quotation",
                queryset=QuotationCost.objects.select_related(
                    "product",
                    'product__general_product_category',
                    'product__general_uom_group',
                    "product__sale_default_uom",
                    "product__sale_tax",
                    "product__sale_currency_using",
                    "unit_of_measure",
                    "tax",
                    "shipping",
                ),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Quotation detail",
        operation_description="Get Quotation detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='quotation', model_code='quotation', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Quotation",
        operation_description="Update Quotation by ID",
        request_body=QuotationUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='quotation', model_code='quotation', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class QuotationExpenseList(BaseListMixin):
    queryset = QuotationExpense.objects
    serializer_list = QuotationExpenseListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("tax").filter(
            quotation_id=self.request.query_params['filter_quotation']
        )

    @swagger_auto_schema(
        operation_summary="QuotationExpense List",
        operation_description="Get QuotationExpense List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# Config
class QuotationConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = QuotationAppConfig.objects
    serializer_detail = QuotationConfigDetailSerializer
    serializer_update = QuotationConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Quotation Config Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Quotation Config Update",
        request_body=QuotationConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


# Indicator
class QuotationIndicatorList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = QuotationIndicatorConfig.objects
    filterset_fields = ['application_code']
    serializer_list = IndicatorListSerializer
    serializer_create = IndicatorCreateSerializer
    serializer_detail = IndicatorListSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

    @swagger_auto_schema(
        operation_summary="Quotation Indicator List",
        operation_description="Get Quotation Indicator List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Quotation Indicator",
        operation_description="Create new Quotation Indicator",
        request_body=IndicatorCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class QuotationIndicatorDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = QuotationIndicatorConfig.objects
    serializer_detail = IndicatorListSerializer
    serializer_update = IndicatorUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Quotation Indicator detail",
        operation_description="Get Quotation Indicator detail by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Quotation Indicator",
        operation_description="Update Quotation Indicator by ID",
        request_body=IndicatorUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class QuotationIndicatorCompanyRestore(
    BaseUpdateMixin,
):
    queryset = QuotationIndicatorConfig.objects
    serializer_detail = IndicatorListSerializer
    serializer_update = IndicatorCompanyRestoreSerializer

    @swagger_auto_schema(
        operation_summary="Restore Quotation Indicator Of Company",
        operation_description="Restore Quotation Indicator Of Company",
        request_body=IndicatorCompanyRestoreSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class QuotationListForCashOutFlow(BaseListMixin):
    queryset = Quotation.objects
    filterset_fields = ['opportunity', 'sale_person']
    serializer_list = QuotationListSerializerForCashOutFlow
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related("customer", "sale_person", "opportunity")

    @swagger_auto_schema(
        operation_summary="Quotation List For Cash OutFlow",
        operation_description="Get Quotation List For Cash OutFlow",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.paginator.page_size = -1
        return self.list(request, *args, **kwargs)
