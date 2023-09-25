from drf_yasg.utils import swagger_auto_schema

from apps.sales.opportunity.models import Opportunity, OpportunitySaleTeamMember
from apps.sales.opportunity.serializers import OpportunityListSerializer, OpportunityUpdateSerializer, \
    OpportunityCreateSerializer, OpportunityDetailSerializer, OpportunityForSaleListSerializer, \
    OpportunityMemberDetailSerializer, OpportunityAddMemberSerializer, OpportunityMemberDeleteSerializer, \
    OpportunityMemberPermissionUpdateSerializer, OpportunityMemberListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class OpportunityList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = Opportunity.objects
    filterset_fields = {
        'employee_inherit': ['exact'],
        'quotation': ['exact', 'isnull'],
        'sale_order': ['exact', 'isnull'],
        'is_close_lost': ['exact'],
        'is_deal_close': ['exact'],
        'id': ['in'],
    }
    serializer_list = OpportunityListSerializer
    serializer_create = OpportunityCreateSerializer
    serializer_detail = OpportunityListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "sale_person",
        ).prefetch_related(
            "opportunity_stage_opportunity__stage",
        )

    @swagger_auto_schema(
        operation_summary="Opportunity List",
        operation_description="Get Opportunity List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='opportunity', model_code='opportunity', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity",
        operation_description="Create new Opportunity",
        request_body=OpportunityCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='opportunity', model_code='opportunity', perm_code="create",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OpportunityDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = Opportunity.objects
    serializer_detail = OpportunityDetailSerializer
    serializer_update = OpportunityUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "decision_maker",
            "end_customer",
            "employee_inherit",
            "sale_order__delivery_of_sale_order",
            "quotation",
        ).prefetch_related(
            "stage",
        )

    @swagger_auto_schema(
        operation_summary="Opportunity detail",
        operation_description="Get Opportunity detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='opportunity', model_code='opportunity', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Opportunity",
        operation_description="Update Opportunity by ID",
        request_body=OpportunityUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='opportunity', model_code='opportunity', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# Opportunity List use for Sale Apps
class OpportunityForSaleList(BaseListMixin):
    queryset = Opportunity.objects
    search_fields = ['title']
    filterset_fields = {
        'employee_inherit': ['exact'],
        'quotation': ['exact', 'isnull'],
        'sale_order': ['exact', 'isnull'],
        'is_close_lost': ['exact'],
        'is_deal_close': ['exact'],
        'id': ['in'],
    }
    serializer_list = OpportunityForSaleListSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "sale_person",
            'customer__industry',
            'customer__owner',
            'customer__payment_term_customer_mapped',
            'customer__price_list_mapped'
        ).prefetch_related(
            "opportunity_stage_opportunity__stage",
            "customer__account_mapped_shipping_address",
            "customer__account_mapped_billing_address",
        )

    @swagger_auto_schema(
        operation_summary="Opportunity List For Sales",
        operation_description="Get Opportunity List For Sales",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OpportunityMemberDetail(BaseRetrieveMixin):
    queryset = OpportunitySaleTeamMember.objects
    serializer_detail = OpportunityMemberDetailSerializer

    @swagger_auto_schema(
        operation_summary="Opportunity member detail",
        operation_description="Get detail member in Opportunity by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OpportunityAddMember(BaseUpdateMixin):
    queryset = Opportunity.objects
    serializer_update = OpportunityAddMemberSerializer

    @swagger_auto_schema(
        operation_summary="Add member for Opportunity",
        operation_description="Add member for Opportunity",
        request_body=OpportunityAddMemberSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OpportunityDeleteMember(BaseUpdateMixin):
    queryset = OpportunitySaleTeamMember.objects
    serializer_update = OpportunityMemberDeleteSerializer

    @swagger_auto_schema(
        operation_summary="Add member for Opportunity",
        operation_description="Add member for Opportunity",
        request_body=OpportunityMemberDeleteSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class MemberPermissionUpdateSerializer(BaseUpdateMixin):
    queryset = OpportunitySaleTeamMember.objects
    serializer_update = OpportunityMemberPermissionUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Update permit for member in Opportunity",
        operation_description="Update permit for member in Opportunity",
        request_body=OpportunityMemberPermissionUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OpportunityMemberList(BaseRetrieveMixin):
    queryset = Opportunity.objects
    serializer_detail = OpportunityMemberListSerializer

    @swagger_auto_schema(
        operation_summary="Opportunity Member List",
        operation_description="Get Opportunity Member List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
