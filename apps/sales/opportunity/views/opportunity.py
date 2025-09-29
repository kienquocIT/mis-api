from typing import Union
from django.conf import settings
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from apps.sales.opportunity.filters import OpportunityListFilters
from apps.sales.lead.models import Lead
from apps.sales.opportunity.models import (
    Opportunity, OpportunitySaleTeamMember, OpportunityConfigStage, OpportunityStage, OpportunityConfig
)
from apps.sales.opportunity.serializers import (
    OpportunityListSerializer, OpportunityUpdateSerializer,
    OpportunityCreateSerializer, OpportunityDetailSerializer
)
from apps.sales.opportunity.serializers.opportunity_sub import (
    OpportunityMemberCreateSerializer, OpportunityMemberDetailSerializer, OpportunityMemberUpdateSerializer,
    OpportunityStageCheckingSerializer, OpportunityContractSummarySerializer,
)
from apps.shared import (
    BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, TypeCheck,
    ResponseController, BaseDestroyMixin,
)


class OpportunityList(BaseListMixin, BaseCreateMixin):
    queryset = Opportunity.objects
    filterset_class = OpportunityListFilters
    search_fields = ['title', 'code', 'customer__name']
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
            "employee_inherit",
            "quotation",
            "sale_order",
        ).prefetch_related(
            "opportunity_stage_opportunity__stage",
            "customer__contact_account_name",
            "customer__account_mapped_shipping_address"
        )

    @classmethod
    def get_opp_allowed(cls, item_data):
        if item_data and isinstance(item_data, dict) and 'opp' in item_data and isinstance(item_data['opp'], dict):
            ids = list(item_data['opp'].keys())
            if TypeCheck.check_uuid_list(data=ids):
                return item_data['opp'].keys()
        return []

    def get_opp_has_view_this(self):
        return [
            str(item) for item in OpportunitySaleTeamMember.objects.filter_current(
                fill__tenant=True, fill__company=True,
                member_id=self.cls_check.employee_attr.employee_current_id,
                permit_view_this_opp=True,
            ).values_list('opportunity_id', flat=True)
        ]

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:
        """
        Check case get list opp for feature or list by configured.
        query_params: from_app=app_label-model_code
        """
        state_from_app, data_from_app = self.has_get_list_from_app()
        if state_from_app is True:
            if data_from_app and isinstance(data_from_app, list) and len(data_from_app) == 3:
                return self.filter_kwargs_q__from_app(data_from_app)
            return self.list_empty()
        # check permit config exists if from_app not calling...
        opp_has_view_ids = self.get_opp_has_view_this()
        if self.cls_check.permit_cls.config_data__exist or opp_has_view_ids:
            return self.filter_kwargs_q__from_config() | Q(id__in=opp_has_view_ids)
        return self.list_empty()

    def filter_kwargs_q__from_app(self, arr_from_app) -> Q:
        # permit_data = {"employee": [], "roles": []}
        opp_ids = []
        if arr_from_app and isinstance(arr_from_app, list) and len(arr_from_app) == 3:
            permit_data = self.cls_check.permit_cls.config_data__by_code(
                label_code=arr_from_app[0],
                model_code=arr_from_app[1],
                perm_code=arr_from_app[2],
                has_roles=False,
            )
            if 'employee' in permit_data:
                opp_ids += self.get_opp_allowed(item_data=permit_data['employee'])
            if 'roles' in permit_data and isinstance(permit_data['roles'], list):
                for item_data in permit_data['roles']:
                    opp_ids += self.get_opp_allowed(item_data=item_data)
            if settings.DEBUG_PERMIT:
                print('=> opp_ids:                :', '[HAS FROM APP]', opp_ids)
        return Q(id__in=list(set(opp_ids)))

    @swagger_auto_schema(
        operation_summary="Opportunity List",
        operation_description="Get Opportunity List",
    )
    @mask_view(
        login_require=True, auth_require=False,
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
        if all(['convert_opp' in request.data, 'lead_id' in request.data]):
            # create a new Opp with selected Customer
            lead = Lead.objects.filter_on_company(id=request.data.get('lead_id')).first()
            if lead:
                request.data['title'] = f'Opportunity from {lead.code}'
                request.data['customer'] = request.data.get('account_mapped')
                request.data['employee_inherit_id'] = request.data.get('employee_inherit_id')
                self.ser_context = {'lead': lead}
        return self.create(request, *args, **kwargs)


class OpportunityDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Opportunity.objects
    serializer_detail = OpportunityDetailSerializer
    serializer_update = OpportunityUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    def go_to_stage_handle(self):
        if 'current_stage_id_manual_update' in self.request.query_params:
            opp_obj = self.get_object()
            if not opp_obj:
                raise ValidationError({'detail': _("Cannot find this Opportunity.")})

            opp_cfg_obj = OpportunityConfig.objects.filter(company=opp_obj.company).first()
            is_select_stage = False
            is_input_win_rate = False
            if opp_cfg_obj:
                is_select_stage = opp_cfg_obj.is_select_stage
                is_input_win_rate = opp_cfg_obj.is_input_win_rate

            if is_select_stage:
                if opp_obj.is_deal_close:
                    raise ValidationError({'detail': _("This opportunity is in 'Deal Close' stage.")})

                stage_id = self.request.query_params.get('current_stage_id_manual_update')
                stage_obj = OpportunityConfigStage.objects.filter(id=stage_id).first()
                if not stage_obj:
                    raise ValidationError({'detail': _("Cannot find this stage.")})

                stage_data = {
                    'id': str(stage_obj.id),
                    'indicator': stage_obj.indicator,
                    'win_rate': stage_obj.win_rate
                }

                if stage_obj.indicator == "Closed Won":
                    if not opp_obj.sale_order:
                        raise ValidationError({'detail': _("Cannot find any Sale Order in this Opportunity.")})
                    if not opp_obj.sale_order.system_status != 3:
                        raise ValidationError({'detail': _("Sale Order in this Opportunity have not approved.")})

                if stage_obj.indicator == 'Delivery':
                    if not opp_obj.sale_order or opp_obj.sale_order.delivery_status not in [2, 3]:
                        raise ValidationError({'detail': _("Cannot find any Delivery that is in progress.")})

                opp_obj.current_stage = stage_obj
                opp_obj.current_stage_data = stage_data
                opp_obj.win_rate = stage_obj.win_rate
                opp_obj.active_go_to_stage = True

                # Nếu OPP check tự nhập winrate + config check tự nhập winrate thì không update winrate theo stage,
                # để nó tự nhập, còn false 1 trong 2 thì winrate buộc phải theo stage
                opp_obj.save(update_fields=[
                    'current_stage', 'active_go_to_stage', 'current_stage_data'
                ] if opp_obj.is_input_rate and is_input_win_rate else [
                    'current_stage', 'active_go_to_stage', 'current_stage_data', 'win_rate'
                ])
                opp_obj.opportunity_stage_opportunity.filter(stage__win_rate__gte=stage_obj.win_rate).delete()
                OpportunityStage.objects.create(
                    opportunity=opp_obj, stage=stage_obj, stage_data=stage_data, is_current=True
                )
                print(f'{opp_obj.code} ---> {stage_obj.indicator}')
                return True
            raise ValidationError({'detail': _("You are not allowed to select stage manually.")})
        return True

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "decision_maker",
            "end_customer",
            "employee_inherit__group",
            "sale_order__delivery_of_sale_order",
            "quotation",
            'process',
        ).prefetch_related(
            "stage",
            "members",
            "customer_decision_factor"
        )

    def manual_check_obj_retrieve(self, instance, **kwargs) -> Union[None, bool]:  # pylint: disable=R0911,R0912
        self.ser_context = {
            'allow_get_member': False,
        }

        # owner
        if str(instance.employee_inherit_id) == str(self.cls_check.employee_attr.employee_current_id):
            self.ser_context['allow_get_member'] = True

        # is member
        opp_member = OpportunitySaleTeamMember.objects.filter_current(
            fill__tenant=True, fill__company=True,
            opportunity=instance, permit_view_this_opp=True,
            member_id=self.cls_check.employee_attr.employee_current_id,
        )
        if opp_member.exists():
            self.ser_context['allow_get_member'] = True
            return True

        # has view opp with space all
        config_data = self.cls_check.permit_cls.config_data
        if config_data and isinstance(config_data, dict):  # pylint: disable=R1702
            range_has_space_1 = []

            employee_data = self.cls_check.permit_cls.config_data.get('employee', {})
            if employee_data and isinstance(employee_data, dict) and 'general' in employee_data:
                general_data = employee_data.get('general', {})
                if general_data and isinstance(general_data, dict):
                    for permit_range, permit_config in general_data.items():
                        if (
                                isinstance(permit_config, dict)
                                and permit_config
                                and 'space' in permit_config
                                and permit_config['space'] == '1'
                        ):
                            range_has_space_1.append(permit_range)

            roles_data = self.cls_check.permit_cls.config_data.get('roles', [])
            if roles_data and isinstance(roles_data, list):
                for role_detail in roles_data:
                    general_data = role_detail.get('general', {}) if isinstance(role_detail, dict) else {}
                    if general_data and isinstance(general_data, dict):
                        for permit_range, permit_config in general_data.items():
                            if (
                                    isinstance(permit_config, dict)
                                    and permit_config
                                    and 'space' in permit_config
                                    and permit_config['space'] == '1'
                            ):
                                range_has_space_1.append(permit_range)

            if range_has_space_1:
                self.ser_context['allow_get_member'] = True
                try:
                    opp_inherit_id = str(instance.employee_inherit_id)
                    if '1' in range_has_space_1:
                        if str(self.cls_check.employee_attr.employee_current_id) == opp_inherit_id:
                            return True

                    if '2' in range_has_space_1:
                        if opp_inherit_id in self.cls_check.employee_attr.employee_staff_ids__exclude_me():
                            return True

                    if '3' in range_has_space_1:
                        if opp_inherit_id in self.cls_check.employee_attr.employee_same_group_ids__exclude_me():
                            return True

                    if '4' in range_has_space_1:
                        if str(instance.company_id) == str(self.cls_check.employee_attr.company_id):
                            return True
                except ValueError:
                    return False

        return False

    def manual_check_obj_update(self, instance, body_data, **kwargs) -> Union[None, bool]:
        if str(instance.employee_inherit_id) == str(self.cls_check.employee_attr.employee_current_id):
            return True
        return False

    @swagger_auto_schema(
        operation_summary="Opportunity detail",
        operation_description="Get Opportunity detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False, employee_required=True,
        label_code='opportunity', model_code='opportunity', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        self.go_to_stage_handle()
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Opportunity",
        operation_description="Update Opportunity by ID",
        request_body=OpportunityUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='opportunity', model_code='opportunity', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OpportunityMemberList(BaseCreateMixin):
    queryset = OpportunitySaleTeamMember
    serializer_create = OpportunityMemberCreateSerializer

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


class OpportunityMemberDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = OpportunitySaleTeamMember.objects
    serializer_detail = OpportunityMemberDetailSerializer
    serializer_update = OpportunityMemberUpdateSerializer

    retrieve_hidden_field = ('tenant_id', 'company_id')

    def check_has_permit_of_space_all(self, opp_obj):  # pylint: disable=R0912
        config_data = self.cls_check.permit_cls.config_data
        if config_data and isinstance(config_data, dict):  # pylint: disable=R1702
            if 'employee' in config_data and isinstance(config_data['employee'], dict):
                if 'general' in config_data['employee']:  # fix bug keyError: 'general'
                    general_data = config_data['employee']['general']
                    if general_data and isinstance(general_data, dict):
                        for _permit_code, permit_config in general_data.items():
                            if permit_config and isinstance(permit_config, dict) and 'space' in permit_config:
                                if (
                                        permit_config['space'] == '1'
                                        and str(opp_obj.company_id) == self.cls_check.employee_attr.company_id
                                ):
                                    return True
            if 'roles' in config_data and isinstance(config_data['roles'], list):
                for role_data in config_data['roles']:
                    general_data = role_data['general']
                    if general_data and isinstance(general_data, dict):
                        for _permit_code, permit_config in general_data.items():
                            if permit_config and isinstance(permit_config, dict) and 'space' in permit_config:
                                if (
                                        permit_config['space'] == '1'
                                        and str(opp_obj.company_id) == self.cls_check.employee_attr.company_id
                                ):
                                    return True
        return False

    def get_opp_member_of_current_user(self, instance):
        return OpportunitySaleTeamMember.objects.filter_current(
            opportunity=instance.opportunity,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    def manual_check_obj_retrieve(self, instance, **kwargs):
        state = self.check_has_permit_of_space_all(opp_obj=instance.opportunity)
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
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        if emp_id and str(instance.opportunity.employee_inherit_id) == str(emp_id):
            return True

        obj_of_current_user = self.get_opp_member_of_current_user(instance=instance)
        if obj_of_current_user:
            return obj_of_current_user.permit_add_member
        return False

    def manual_check_obj_destroy(self, instance, **kwargs):
        if instance.member_id == instance.opportunity.employee_inherit_id:
            return False

        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id

        if emp_id == instance.member_id:
            # deny delete member is owner opp.
            return False

        if emp_id and str(instance.opportunity.employee_inherit_id) == str(emp_id):
            # owner auto allow in member
            return True

        obj_of_current_user = self.get_opp_member_of_current_user(instance=instance)
        if obj_of_current_user:
            return obj_of_current_user.permit_view_this_opp
        return False

    def get_lookup_url_kwarg(self) -> dict:
        return {
            'opportunity_id': self.kwargs['pk_opp'],
            'member_id': self.kwargs['pk_member']
        }

    @swagger_auto_schema(
        operation_summary='Get member detail of OPP',
        operation_description='Check permit by OPP related',
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='opportunity', model_code='opportunity', perm_code="view",
    )
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


class OpportunityStageChecking(BaseListMixin):
    queryset = Opportunity.objects
    serializer_list = OpportunityStageCheckingSerializer
    retrieve_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        if 'opportunity_id' in self.request.query_params:
            return super().get_queryset().filter(
                id=self.request.query_params.get('opportunity_id')
            ).select_related().prefetch_related()
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Opportunity Stage Check",
        operation_description="Opportunity Stage Check",
    )
    @mask_view(
        login_require=True, auth_require=False, employee_required=True,
        label_code='opportunity', model_code='opportunity', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        self.ser_context = self.request.query_params
        return self.list(request, *args, **kwargs)


class OpportunityContractSummary(BaseListMixin):
    queryset = Opportunity.objects
    serializer_list = OpportunityContractSummarySerializer
    retrieve_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        if 'opportunity_id' in self.request.query_params:
            return super().get_queryset().filter(
                id=self.request.query_params.get('opportunity_id')
            ).select_related().prefetch_related()
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Opportunity Contract Summary",
        operation_description="Opportunity Contract Summary",
    )
    @mask_view(
        login_require=True, auth_require=False, employee_required=True,
        label_code='opportunity', model_code='opportunity', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
