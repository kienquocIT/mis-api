from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.quotation.models.quotation import Quotation
from apps.sales.quotation.serializers.quotation import QuotationListSerializer, QuotationCreateSerializer, \
    QuotationDetailSerializer, QuotationUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class QuotationList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = Quotation.objects.all()
    filterset_fields = []
    serializer_list = QuotationListSerializer
    serializer_create = QuotationCreateSerializer
    serializer_detail = QuotationListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    # def get_queryset(self):
    #     return super().get_queryset().select_related(
    #         "opportunity"
    #     )

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

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "customer",
            "contact",
            "sale_person"
        )

    @swagger_auto_schema(
        operation_summary="Quotation detail",
        operation_description="Get Quotation detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.serializer_class = QuotationDetailSerializer
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Quotation",
        operation_description="Update Quotation by ID",
        request_body=QuotationUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = QuotationUpdateSerializer
        return self.update(request, *args, **kwargs)

