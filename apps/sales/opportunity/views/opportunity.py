from drf_yasg.utils import swagger_auto_schema

from apps.sales.opportunity.models import Opportunity, OpportunitySaleTeamMember
from apps.sales.opportunity.serializers import (
    OpportunityListSerializer, OpportunityUpdateSerializer,
    OpportunityCreateSerializer, OpportunityDetailSerializer, OpportunityForSaleListSerializer,
    OpportunityMemberDetailSerializer, OpportunityAddMemberSerializer, OpportunityMemberDeleteSerializer,
    OpportunityMemberPermissionUpdateSerializer, OpportunityMemberListSerializer,
    OpportunityListSerializerForCashOutFlow
)
from apps.sales.opportunity.serializers.opp_members import (
    MemberOfOpportunityDetailSerializer,
    MemberOfOpportunityUpdateSerializer, MemberOfOpportunityAddSerializer,
)
from apps.shared import (
    BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, TypeCheck,
    ResponseController, BaseDestroyMixin,
)


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
    search_fields = ['title', 'code']
    serializer_list = OpportunityListSerializer
    serializer_create = OpportunityCreateSerializer
    serializer_detail = OpportunityListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "sale_person",
            # "employee_inherit",
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
            "members",
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


class MemberOfOpportunityDetailAdd(BaseCreateMixin):
    queryset = OpportunitySaleTeamMember
    serializer_create = MemberOfOpportunityAddSerializer

    def get_opp_member_of_current_user(self, opp_obj):
        return OpportunitySaleTeamMember.objects.filter_current(
            opportunity=opp_obj,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    @classmethod
    def get_opp_obj(cls, pk_idx):
        if TypeCheck.check_uuid(pk_idx):
            return Opportunity.objects.filter_current(pk=pk_idx, fill__tenant=True, fill__company=True).first()
        return None

    def check_permit_add_member_opp(self, opp_obj) -> bool:
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        if emp_id and str(opp_obj.employee_inherit_id) == str(emp_id):
            return True

        opp_member_current_user = self.get_opp_member_of_current_user(opp_obj=opp_obj)
        if opp_member_current_user:
            return opp_member_current_user.permit_add_member
        return False

    def create_hidden_field_manual_after(self):
        return {
            'tenant_id': self.cls_check.employee_attr.tenant_id,
            'company_id': self.cls_check.employee_attr.company_id,
            'opportunity_id': getattr(self, 'opportunity_id', None),
        }

    def get_serializer_detail_return(self, obj):
        return {'member': 'Successful'}

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, pk_opp, **kwargs):
        opp_obj = self.get_opp_obj(pk_opp)
        if opp_obj:
            if self.check_permit_add_member_opp(opp_obj=opp_obj):
                setattr(self, 'opportunity_id', opp_obj.id)
                return self.create(request, *args, pk_opp, **kwargs)
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()


class MemberOfOpportunityDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = OpportunitySaleTeamMember.objects
    serializer_detail = MemberOfOpportunityDetailSerializer
    serializer_update = MemberOfOpportunityUpdateSerializer

    retrieve_hidden_field = ('tenant_id', 'company_id')

    def get_opp_member_of_current_user(self, instance):
        return OpportunitySaleTeamMember.objects.filter_current(
            opportunity=instance.opportunity,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    def manual_check_obj_retrieve(self, instance, **kwargs):
        state = self.check_perm_by_obj_or_body_data(obj=instance.opportunity)
        if not state:
            # special case skip with True if current user is employee_inherit
            emp_id = self.cls_check.employee_attr.employee_current_id
            if emp_id and str(instance.opportunity.employee_inherit_id) == str(emp_id):
                return True

            obj_of_current_user = self.get_opp_member_of_current_user(instance=instance)
            if obj_of_current_user:
                return obj_of_current_user.permit_view_this_opp
        return state

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        state = self.check_perm_by_obj_or_body_data(obj=instance.opportunity)
        if not state:
            # special case skip with True if current user is employee_inherit
            emp_id = self.cls_check.employee_attr.employee_current_id
            if emp_id and str(instance.opportunity.employee_inherit_id) == str(emp_id):
                return True

            obj_of_current_user = self.get_opp_member_of_current_user(instance=instance)
            if obj_of_current_user:
                return obj_of_current_user.permit_view_this_opp
        return state

    def manual_check_obj_destroy(self, instance, **kwargs):
        state = self.check_perm_by_obj_or_body_data(obj=instance.opportunity)
        if not state:
            # special case skip with True if current user is employee_inherit
            emp_id = self.cls_check.employee_attr.employee_current_id
            if emp_id and str(instance.opportunity.employee_inherit_id) == str(emp_id):
                return True

            obj_of_current_user = self.get_opp_member_of_current_user(instance=instance)
            if obj_of_current_user:
                return obj_of_current_user.permit_view_this_opp
        return state

    def get_lookup_url_kwarg(self) -> dict:
        print({
            'opportunity_id': self.kwargs['pk_opp'],
            'member_id': self.kwargs['pk_member']
        })
        return {
            'opportunity_id': self.kwargs['pk_opp'],
            'member_id': self.kwargs['pk_member']
        }

    @swagger_auto_schema(
        operation_summary='Get member detail of OPP',
        operation_description='Check permit by OPP related',
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk_opp, pk_member, **kwargs):
        if TypeCheck.check_uuid(pk_opp) and TypeCheck.check_uuid(pk_member):
            return self.retrieve(request, *args, pk_opp, pk_member, **kwargs)
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary='Update app and permit for member',
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, pk_opp, pk_member, **kwargs):
        if TypeCheck.check_uuid(pk_opp) and TypeCheck.check_uuid(pk_member):
            return self.update(request, *args, pk_opp, pk_member, **kwargs)
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary='Remove member from opp'
    )
    @mask_view(login_require=True, auth_require=False)
    def delete(self, request, *args, pk_opp, pk_member, **kwargs):
        if TypeCheck.check_uuid(pk_opp) and TypeCheck.check_uuid(pk_member):
            return self.destroy(request, *args, pk_opp, pk_member, is_purge=True, **kwargs)
        return ResponseController.notfound_404()


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
        login_require=True, auth_require=True,
        label_code='opportunity', model_code='opportunity', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OpportunityListForCashOutFlow(BaseListMixin):
    queryset = Opportunity.objects
    filterset_fields = {
        'employee_inherit': ['exact'],
        'quotation': ['exact', 'isnull'],
        'sale_order': ['exact', 'isnull'],
        'is_close_lost': ['exact'],
        'is_deal_close': ['exact'],
        'id': ['in'],
    }
    serializer_list = OpportunityListSerializerForCashOutFlow
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
        operation_summary="Opportunity List For Cash Outflow",
        operation_description="Get Opportunity List For Cash Outflow",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='opportunity', model_code='opportunity', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        self.paginator.page_size = -1
        return self.list(request, *args, **kwargs)
