from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.quotation.models import Quotation, QuotationExpense, QuotationAppConfig, QuotationIndicatorConfig
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
    permission_classes = [IsAuthenticated]
    queryset = Quotation.objects
    filterset_fields = {
        'opportunity': ['exact'],
        'sale_person': ['exact'],
        'opportunity__sale_order': ['exact', 'isnull'],
        'opportunity__is_close_lost': ['exact'],
        'opportunity__is_deal_close': ['exact'],
    }
    serializer_list = QuotationListSerializer
    serializer_create = QuotationCreateSerializer
    serializer_detail = QuotationListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', 'employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "sale_person",
            "opportunity"
        )

    @swagger_auto_schema(
        operation_summary="Quotation List",
        operation_description="Get Quotation List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Quotation",
        operation_description="Create new Quotation",
        request_body=QuotationCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class QuotationDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = Quotation.objects
    serializer_detail = QuotationDetailSerializer
    serializer_update = QuotationUpdateSerializer
    update_hidden_field = ['employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "opportunity__customer",
            "customer",
            "contact",
            "sale_person",
            "payment_term",
            "customer__payment_term_mapped",
        )

    @swagger_auto_schema(
        operation_summary="Quotation detail",
        operation_description="Get Quotation detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Quotation",
        operation_description="Update Quotation by ID",
        request_body=QuotationUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class QuotationExpenseList(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = QuotationExpense.objects
    serializer_list = QuotationExpenseListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            "tax"
        )

    @swagger_auto_schema(
        operation_summary="QuotationExpense List",
        operation_description="Get QuotationExpense List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        kwargs.update({'quotation_id': request.query_params['filter_quotation']})
        return self.list(request, *args, **kwargs)


# Config
class QuotationConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = QuotationAppConfig.objects
    serializer_detail = QuotationConfigDetailSerializer
    serializer_update = QuotationConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Quotation Config Detail",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Quotation Config Update",
        request_body=QuotationConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


# Indicator
class QuotationIndicatorList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
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
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Quotation Indicator",
        operation_description="Create new Quotation Indicator",
        request_body=IndicatorCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class QuotationIndicatorDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = QuotationIndicatorConfig.objects
    serializer_detail = IndicatorListSerializer
    serializer_update = IndicatorUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Quotation Indicator detail",
        operation_description="Get Quotation Indicator detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Quotation Indicator",
        operation_description="Update Quotation Indicator by ID",
        request_body=IndicatorUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class QuotationIndicatorCompanyRestore(
    BaseUpdateMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = QuotationIndicatorConfig.objects
    serializer_detail = IndicatorListSerializer
    serializer_update = IndicatorCompanyRestoreSerializer

    @swagger_auto_schema(
        operation_summary="Restore Quotation Indicator Of Company",
        operation_description="Restore Quotation Indicator Of Company",
        request_body=IndicatorCompanyRestoreSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class QuotationListForCashOutFlow(BaseListMixin):
    permission_classes = [IsAuthenticated]
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
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
