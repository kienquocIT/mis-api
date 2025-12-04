from uuid import uuid4

from rest_framework import serializers

from apps.core.hr.models import DistributionApplication
from apps.core.hr.serializers.common import validate_license_used
from apps.core.tenant.models import TenantPlan
from apps.masterdata.saledata.models import Product, ProductCategory, UnitOfMeasure, Tax, Contact
from apps.masterdata.saledata.models import Account
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.lead.models import LeadParser, LeadOpportunity, LeadStage, LeadChartInformation
from apps.sales.opportunity.models import (
    OpportunityProductCategory, OpportunityProduct,
    OpportunityCompetitor, OpportunityContactRole, OpportunityCustomerDecisionFactor, OpportunitySaleTeamMember,
    OpportunityConfigStage, OpportunityStage, PlanMemberOpportunity, Opportunity, OpportunityConfig,
)
from apps.shared import DisperseModel, Caching
from apps.shared.permissions.util import PermissionController
from apps.shared.translations.opportunity import OpportunityMsg


__all__ = [
    'OpportunityProductCreateSerializer',
    'OpportunityCompetitorCreateSerializer',
    'OpportunityContactRoleCreateSerializer',
    'OpportunityStageUpdateSerializer',
    'OpportunityMemberCreateSerializer',
    'OpportunityMemberDetailSerializer',
    'OpportunityMemberUpdateSerializer',
    'OpportunityStageCheckingSerializer',
    'OpportunityContractSummarySerializer',
    'OpportunityCommonFunction'
]


class OpportunityProductCreateSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(allow_null=True)
    product_category = serializers.UUIDField(allow_null=False, required=True)
    uom = serializers.UUIDField(allow_null=False)
    tax = serializers.UUIDField(allow_null=False, required=False)

    class Meta:
        model = OpportunityProduct
        fields = (
            'product',
            'product_category',
            'uom',
            'tax',
            'product_name',
            'product_quantity',
            'product_unit_price',
            'product_subtotal_price',
        )

    @classmethod
    def validate_product(cls, value):
        try:  # noqa
            if value is not None:
                obj = Product.objects.get(
                    id=value
                )
                return {
                    'id': str(obj.id),
                    'title': obj.title,
                }
        except Product.DoesNotExist:
            raise serializers.ValidationError({'Product': OpportunityMsg.NOT_EXIST})
        return None

    @classmethod
    def validate_product_category(cls, value):
        try:  # noqa
            if value is not None:
                obj = ProductCategory.objects.get(
                    id=value
                )
                return {
                    'id': str(obj.id),
                    'title': obj.title,
                }
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError({'Product Category': OpportunityMsg.NOT_EXIST})
        return None

    @classmethod
    def validate_uom(cls, value):
        try:  # noqa
            if value is not None:
                obj = UnitOfMeasure.objects.get(
                    id=value
                )
                return {
                    'id': str(obj.id),
                    'title': obj.title,
                }
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': OpportunityMsg.NOT_EXIST})
        return None

    @classmethod
    def validate_tax(cls, value):
        try:  # noqa
            if value is not None:
                obj = Tax.objects.get(
                    id=value
                )
                return {
                    'id': str(obj.id),
                    'title': obj.title,
                    'rate': obj.rate,
                }
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'Tax': OpportunityMsg.NOT_EXIST})
        return None

    @classmethod
    def validate_product_quantity(cls, value):
        if value < 0:
            raise serializers.ValidationError({'quantity': OpportunityMsg.VALUE_GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_product_unit_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'unit price': OpportunityMsg.VALUE_GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_product_subtotal_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'subtotal price': OpportunityMsg.VALUE_GREATER_THAN_ZERO})
        return value


class OpportunityCompetitorCreateSerializer(serializers.ModelSerializer):
    competitor = serializers.UUIDField(allow_null=False)

    class Meta:
        model = OpportunityCompetitor
        fields = (
            'competitor',
            'strength',
            'weakness',
            'win_deal'
        )

    @classmethod
    def validate_competitor(cls, value):
        try:  # noqa
            if value is not None:
                obj = Account.objects.get(
                    id=value
                )
                return {
                    'id': str(obj.id),
                    'name': obj.name,
                }
        except Account.DoesNotExist:
            raise serializers.ValidationError({'competitor': OpportunityMsg.NOT_EXIST})
        return None


class OpportunityContactRoleCreateSerializer(serializers.ModelSerializer):
    contact = serializers.UUIDField(allow_null=False)
    job_title = serializers.CharField(allow_blank=True)

    class Meta:
        model = OpportunityContactRole
        fields = (
            'type_customer',
            'role',
            'contact',
            'job_title'
        )

    @classmethod
    def validate_contact(cls, value):
        try:  # noqa
            if value is not None:
                obj = Contact.objects.get(
                    id=value
                )
                return {
                    'id': str(obj.id),
                    'fullname': obj.fullname,
                }
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': OpportunityMsg.NOT_EXIST})
        return None


class OpportunityStageUpdateSerializer(serializers.ModelSerializer):
    stage = serializers.UUIDField(allow_null=False)
    is_current = serializers.BooleanField()

    class Meta:
        model = OpportunitySaleTeamMember
        fields = (
            'stage',
            'is_current'
        )

    @classmethod
    def validate_stage(cls, value):
        try:  # noqa
            if value is not None:
                obj = OpportunityConfigStage.objects.get(
                    id=value, is_delete=False
                )
                return obj.id
        except OpportunityConfigStage.DoesNotExist:
            raise serializers.ValidationError({'stage': OpportunityMsg.NOT_EXIST})
        return None


# related
class OpportunityMemberCreateSerializer(serializers.Serializer):  # noqa
    members = serializers.ListField(
        child=serializers.UUIDField()
    )

    @classmethod
    def validate_members(cls, attrs):
        if len(attrs) > 0:
            objs = DisperseModel(app_model='hr.Employee').get_model().objects.filter_on_company(id__in=attrs)
            if objs.count() == len(attrs):
                return objs
            raise serializers.ValidationError({'members': OpportunityMsg.MEMBER_NOT_EXIST})
        raise serializers.ValidationError({'members': OpportunityMsg.MEMBER_REQUIRED})

    def create(self, validated_data):
        opportunity_id = validated_data.get('opportunity_id')
        tenant_id = validated_data.get('tenant_id')
        company_id = validated_data.get('company_id')
        members = validated_data.pop('members')
        objs = []
        for member_obj in members:
            obj = OpportunitySaleTeamMember.objects.create(
                opportunity_id=opportunity_id,
                member=member_obj,
                tenant_id=tenant_id,
                company_id=company_id,
            )
            objs.append(obj)
        return objs[0]


class OpportunityMemberDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunitySaleTeamMember
        fields = (
            'id', 'date_modified', 'permit_view_this_opp', 'permit_add_member',
            'permission_by_configured',
        )


class OpportunityMemberUpdateSerializer(serializers.ModelSerializer):
    permission_by_configured = serializers.JSONField(
        required=False,
        help_text=str(
            [{
                "id": "UUID or None",
                "app_id": "UUID",
                "plan_data": "UUID",
                "create": bool,
                "view": bool,
                "edit": bool,
                "delete": bool,
                "range": 'CHOICE("1", "2", "3", "4")',
            }]
        ),
    )

    def validate_permission_by_configured(self, attrs):
        return PermissionController(tenant_id=self.instance.tenant_id).valid(attrs=attrs, has_space=False)

    class Meta:
        model = OpportunitySaleTeamMember
        fields = ('permit_view_this_opp', 'permit_add_member', 'permission_by_configured')

    def validate(self, validate_data):
        return validate_license_used(validate_data=validate_data)

    @staticmethod
    def set_up_data_plan_app(validated_data, instance=None):
        cls_query = PlanMemberOpportunity
        filter_query = {'opportunity_member': instance}
        plan_application_dict = {}
        plan_app_data = []
        bulk_info = []
        if 'plan_app' in validated_data:
            plan_app_data = validated_data['plan_app']
            del validated_data['plan_app']
            if instance:
                # delete old M2M PlanEmployee
                plan_x_old = cls_query.objects.filter(**filter_query)
                if plan_x_old:
                    plan_x_old.delete()
        if plan_app_data:
            for plan_app in plan_app_data:
                plan_code = None
                app_code_list = []
                if 'plan' in plan_app:
                    plan_code = plan_app['plan'].code if plan_app['plan'] else None
                if 'application' in plan_app:
                    app_code_list = [app.code for app in plan_app['application']] if plan_app['application'] else []
                if plan_code and app_code_list:
                    plan_application_dict.update({plan_code: app_code_list})
                    bulk_info.append(
                        cls_query(
                            **{
                                'plan': plan_app['plan'],
                                'application': [str(app.id) for app in plan_app['application']]
                            }
                        )
                    )
        return plan_application_dict, plan_app_data, bulk_info

    @staticmethod
    def create_plan_update_tenant_plan(instance, plan_app_data, bulk_info):
        if instance and plan_app_data and bulk_info:
            # create M2M PlanEmployee
            for info in bulk_info:
                info.opportunity_member = instance
            PlanMemberOpportunity.objects.bulk_create(bulk_info)
            # update TenantPlan
            for plan_data in plan_app_data:
                if 'plan' in plan_data and 'license_used' in plan_data:
                    tenant_plan = TenantPlan.objects.filter(
                        tenant=instance.tenant,
                        plan=plan_data['plan']
                    ).first()
                    if tenant_plan:
                        tenant_plan.license_used = plan_data['license_used']
                        tenant_plan.save()
        Caching().clean_by_prefix_many(table_name_list=['hr_PlanEmployee', 'tenant_TenantPlan'])
        return True

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


# stage checking
class OpportunityStageCheckingSerializer(serializers.ModelSerializer):
    current_stage = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = (
            'id',
            'current_stage'
        )

    def get_current_stage(self, obj):
        stages = OpportunityConfigStage.objects.filter(company_id=obj.company_id, is_delete=False).order_by('win_rate')
        stage_lost = None
        stage_delivery = None
        stage_close = None
        list_stage = []
        # sort stage [stage 1, stage 2, ...., stage Close Lost, stage Delivery, stage Deal Close
        for item in stages:
            if item.is_closed_lost:
                stage_lost = item
            elif item.is_delivery:
                stage_delivery = item
            elif item.is_deal_closed:
                stage_close = item
            else:
                list_stage.append(item)
        if stage_lost:
            list_stage.append(stage_lost)
        if stage_delivery:
            list_stage.append(stage_delivery)
        if stage_close:
            list_stage.append(stage_close)
        # list stage instance
        list_stage_instance = obj.parse_stage(list_stage=list_stage, obj=obj)
        # check stage
        stage_index = []
        for idx, item in enumerate(list_stage):
            if item.logical_operator == 0 and all(element in list_stage_instance for element in item.condition_datas):
                stage_index.append(idx)
            if item.logical_operator != 0 and any(element in list_stage_instance for element in item.condition_datas):
                stage_index.append(idx)

        current_stage = list_stage[stage_index[-1]]
        return {
            'id': str(current_stage.id),
            'is_deal_closed': current_stage.is_deal_closed,
            'is_closed_lost': current_stage.is_closed_lost,
            'is_delivery': current_stage.is_delivery,
            'indicator': current_stage.indicator,
            'win_rate': current_stage.win_rate,
        } if current_stage else {}


# contract summary
class OpportunityContractSummarySerializer(serializers.ModelSerializer):
    customer_data = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    sale_order_contract_summary_data = serializers.SerializerMethodField()
    lease_order_contract_summary_data = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = (
            'id',
            'code',
            'title',
            'customer_data',
            'sale_person',
            'open_date',
            'close_date',
            'sale_order_contract_summary_data',
            'lease_order_contract_summary_data',
        )

    @classmethod
    def get_customer_data(cls, obj):
        return {
            'id': obj.customer_id,
            'name': obj.customer.name,
            'code': obj.customer.code,
            'tax_code': obj.customer.tax_code,
        } if obj.customer else {}

    @classmethod
    def get_sale_person(cls, obj):
        return obj.employee_inherit.get_detail_with_group() if obj.employee_inherit else {}

    @classmethod
    def get_sale_order_contract_summary_data(cls, obj):
        sale_order_contract_summary_data = []
        so_list_mapped = obj.sale_order_opportunity.all()
        for so_obj in so_list_mapped:
            for item in so_obj.sale_order_indicator_sale_order.all():
                sale_order_contract_summary_data.append({
                    'id': str(item.id),
                    'indicator_value': item.indicator_value,
                    'indicator_rate': item.indicator_rate,
                    'quotation_indicator_data': item.quotation_indicator_data,
                    'quotation_indicator_value': item.quotation_indicator_value,
                    'quotation_indicator_rate': item.quotation_indicator_rate,
                    'difference_indicator_value': item.difference_indicator_value,
                })
        return sale_order_contract_summary_data

    @classmethod
    def get_lease_order_contract_summary_data(cls, obj):
        lease_order_contract_summary_data = []
        lo_list_mapped = obj.lease_opportunity.all()
        for lo_obj in lo_list_mapped:
            for item in lo_obj.lease_order_indicator_lease_order.all():
                lease_order_contract_summary_data.append({
                    'id': str(item.id),
                    'indicator_value': item.indicator_value,
                    'indicator_rate': item.indicator_rate,
                    'quotation_indicator_data': item.quotation_indicator_data,
                    'quotation_indicator_value': item.quotation_indicator_value,
                    'quotation_indicator_rate': item.quotation_indicator_rate,
                    'difference_indicator_value': item.difference_indicator_value,
                })
        return lease_order_contract_summary_data


class OpportunityCommonFunction:
    @classmethod
    def create_product_category(cls, data, opportunity):
        data_bulk = []
        for product_category_id in data:
            opportunity_product_category = OpportunityProductCategory(
                product_category_id=product_category_id,
                opportunity=opportunity
            )
            data_bulk.append(opportunity_product_category)
        OpportunityProductCategory.objects.bulk_create(data_bulk)
        return True

    @classmethod
    def update_opportunity_product(cls, data, instance):
        # delete old record
        OpportunityProduct.objects.filter(opportunity=instance).delete()
        # create new
        bulk_data = []
        for item in data:
            product_id = None
            if item['product']:
                product_id = item['product']['id']
            bulk_data.append(
                OpportunityProduct(
                    opportunity=instance,
                    product_id=product_id,
                    product_category_id=item['product_category']['id'],
                    uom_id=item['uom']['id'],
                    tax_id=item['tax']['id'] if 'tax' in item else None,
                    product_name=item['product_name'],
                    product_quantity=item['product_quantity'],
                    product_unit_price=item['product_unit_price'],
                    product_subtotal_price=item['product_subtotal_price'],
                )
            )
        OpportunityProduct.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def update_product_category(cls, data, instance):
        # delete old record
        OpportunityProductCategory.objects.filter(opportunity=instance).delete()
        # create new
        cls.create_product_category(data, instance)
        return True

    @classmethod
    def update_customer_decision_factor(cls, data, instance):
        OpportunityCustomerDecisionFactor.objects.filter(opportunity=instance)
        bulk_data = []
        for factor_id in data:
            bulk_data.append(
                OpportunityCustomerDecisionFactor(
                    opportunity=instance,
                    factor_id=factor_id
                )
            )
        OpportunityCustomerDecisionFactor.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def update_opportunity_competitor(cls, data, instance):
        # delete old record
        OpportunityCompetitor.objects.filter(opportunity=instance).delete()
        # create new
        bulk_data = []
        for item in data:
            bulk_data.append(
                OpportunityCompetitor(
                    opportunity=instance,
                    competitor_id=item['competitor']['id'],
                    strength=item['strength'],
                    weakness=item['weakness'],
                    win_deal=item['win_deal'],
                )
            )
        OpportunityCompetitor.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def update_opportunity_contact_role(cls, data, instance):
        # delete old record
        OpportunityContactRole.objects.filter(opportunity=instance).delete()
        # create new
        bulk_data = []
        for item in data:
            bulk_data.append(
                OpportunityContactRole(
                    opportunity=instance,
                    type_customer=item['type_customer'],
                    contact_id=item['contact']['id'],
                    job_title=item['job_title'],
                    role=item['role']
                )
            )
        OpportunityContactRole.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def update_opportunity_stage(cls, opp_obj):
        """
        Hàm cập nhập trạng thái cho OPP (tạo record vào bảng Many + update trạng thái của OPP vào list)
        """

        opp_cfg_obj = OpportunityConfig.objects.filter(company=opp_obj.company).first()
        is_select_stage = False
        is_input_win_rate = False
        if opp_cfg_obj:
            is_select_stage = opp_cfg_obj.is_select_stage
            is_input_win_rate = opp_cfg_obj.is_input_win_rate

        # Chỉ cập nhập trạng thái nếu OPP này không chọn update thủ công hoặc config không cho update thủ công
        if not opp_obj.active_go_to_stage or not is_select_stage:
            # Cập nhập stage tự động
            opp_config_stage_data_list = CheckOppStageFunction.get_opp_config_stage_data_list(opp_obj)
            opp_condition_data_list = CheckOppStageFunction.get_opp_condition_data_list(opp_obj)
            new_opp_stage_data_list = CheckOppStageFunction.get_new_opp_stage_data_list(
                opp_config_stage_data_list, opp_condition_data_list, opp_obj
            )
            data_bulk = []
            current_stage_item = None
            for item in new_opp_stage_data_list:
                if item.get('current'):
                    current_stage_item = item
                data_bulk.append(
                    OpportunityStage(
                        opportunity=opp_obj,
                        stage_id=str(item.get('id')),
                        stage_data={
                            'id': str(item.get('id')),
                            'indicator': item.get('indicator'),
                            'win_rate': item.get('win_rate')
                        },
                        is_current=item.get('current')
                    )
                )
            if len(data_bulk) > 0:
                if data_bulk[-1].stage.indicator == 'Closed Lost' and 'Order Status=0' in opp_condition_data_list:
                    raise serializers.ValidationError(
                        {'Closed Lost': 'Can not update to stage "Closed Lost". You are having an Approved Order.'}
                    )
            OpportunityStage.objects.filter(opportunity=opp_obj).delete()
            OpportunityStage.objects.bulk_create(data_bulk)

            # update stage và winrate cho OPP
            if current_stage_item:
                opp_obj.active_go_to_stage = False
                opp_obj.win_rate = current_stage_item.get('win_rate')
                opp_obj.current_stage_id = current_stage_item.get('id')
                opp_obj.current_stage_data = {
                    'id': str(current_stage_item.get('id')),
                    'indicator': current_stage_item.get('indicator'),
                    'win_rate': current_stage_item.get('win_rate')
                }
                # Nếu OPP check tự nhập winrate + config check tự nhập winrate thì không update winrate theo stage,
                # còn không thì winrate buộc phải theo stage
                opp_obj.save(update_fields=[
                    'current_stage', 'active_go_to_stage', 'current_stage_data'
                ] if opp_obj.is_input_rate and is_input_win_rate else [
                    'current_stage', 'active_go_to_stage', 'current_stage_data', 'win_rate'
                ])
        else:
            # chỉ cập nhập winrate
            if opp_obj.current_stage:
                opp_obj.win_rate = opp_obj.current_stage.win_rate
                opp_obj.save(update_fields=['win_rate'] if not opp_obj.is_input_rate else [])
        return True

    @classmethod
    def get_alias_permit_from_general(cls, employee_obj):
        result = []
        app_id_get = [
            "e66cfb5a-b3ce-4694-a4da-47618f53de4c",  # Task
            "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
            "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sales Order
            # "31c9c5b0-717d-4134-b3d0-cc4ca174b168",  # Contract
            "57725469-8b04-428a-a4b0-578091d0e4f5",  # Advanced Payment
            "1010563f-7c94-42f9-ba99-63d5d26a1aca",  # Payment
            "65d36757-557e-4534-87ea-5579709457d7",  # Return Payment
            "2de9fb91-4fb9-48c8-b54e-c03bd12f952b",  # BOM
            "ad1e1c4e-2a7e-4b98-977f-88d069554657",  # Bidding
            "58385bcf-f06c-474e-a372-cadc8ea30ecc",  # Contract approval
            "14dbc606-1453-4023-a2cf-35b1cd9e3efd",  # Call log
            "2fe959e3-9628-4f47-96a1-a2ef03e867e3",  # Meeting
            "dec012bf-b931-48ba-a746-38b7fd7ca73b",  # Email
            "3a369ba5-82a0-4c4d-a447-3794b67d1d02",  # Consulting Document
            "010404b3-bb91-4b24-9538-075f5f00ef14",  # Lease Order
            "c51857ef-513f-4dbf-babd-26d68950ad6e",  # COF
            "36f25733-a6e7-43ea-b710-38e2052f0f6d",  # service order
        ]
        for obj in DistributionApplication.objects.select_related('app').filter(
                employee=employee_obj, app_id__in=app_id_get
        ):
            permit_has_1_range = []
            permit_has_4_range = []
            for permit_code, permit_config in obj.app.permit_mapping.items():
                if '1' in permit_config.get('range', []):
                    permit_has_1_range.append(permit_code)
                elif '4' in permit_config.get('range', []):
                    permit_has_4_range.append(permit_code)

            has_1 = False
            data_tmp_for_1 = {
                'id': str(uuid4()),
                'app_id': str(obj.app_id),
                'view': False,
                'create': False,
                'edit': False,
                'delete': False,
                'range': '1',
                'space': '0',
            }
            has_4 = False
            data_tmp_for_4 = {
                'id': str(uuid4()),
                'app_id': str(obj.app_id),
                'view': False,
                'create': False,
                'edit': False,
                'delete': False,
                'range': '4',
                'space': '0',
            }

            for key in ['view', 'create', 'edit', 'delete']:
                if key in permit_has_1_range:
                    has_1 = True
                    data_tmp_for_1[key] = True
                elif key in permit_has_4_range:
                    has_4 = True
                    data_tmp_for_4[key] = True

            if has_1 is True:
                result.append(data_tmp_for_1)
            if has_4 is True:
                result.append(data_tmp_for_4)
        return result

    @classmethod
    def convert_opportunity(cls, lead_obj, lead_config, opp_mapped_obj):
        # convert to a new opp (existed account)
        current_stage = LeadStage.objects.filter_on_company(level=4).first()
        lead_obj.current_lead_stage = current_stage
        lead_obj.current_lead_stage_data = LeadParser.parse_data(current_stage, 'lead_stage')
        lead_obj.lead_status = 4
        lead_obj.save(update_fields=['current_lead_stage', 'current_lead_stage_data', 'lead_status'])

        lead_config.opp_mapped = opp_mapped_obj
        lead_config.opp_mapped_data = LeadParser.parse_data(opp_mapped_obj, 'opportunity')
        lead_config.account_mapped = opp_mapped_obj.customer
        lead_config.account_mapped_data = LeadParser.parse_data(opp_mapped_obj.customer, 'account')
        lead_config.assign_to_sale_config = opp_mapped_obj.employee_inherit
        lead_config.assign_to_sale_config_data = LeadParser.parse_data(
            opp_mapped_obj.employee_inherit, 'assign_to_sale'
        )
        lead_config.convert_opp = True
        lead_config.convert_opp_create = True
        lead_config.save(update_fields=[
            'opp_mapped', 'opp_mapped_data',
            'account_mapped', 'account_mapped_data',
            'assign_to_sale_config', 'assign_to_sale_config_data',
            'convert_opp', 'convert_opp_create'
        ])

        LeadOpportunity.objects.create(
            company=lead_obj.company,
            tenant=lead_obj.tenant,
            lead=lead_obj,
            lead_data=LeadParser.parse_data(lead_obj, 'lead_mapped_opp'),
            opportunity=opp_mapped_obj,
            employee_created=lead_obj.employee_created,
            employee_inherit=lead_obj.employee_inherit
        )
        LeadChartInformation.create_update_chart_information(opp_mapped_obj.tenant_id, opp_mapped_obj.company_id)
        return True


class CheckOppStageFunction:
    @classmethod
    def get_opp_config_stage_data_list(cls, opp_obj):
        opp_config_stage_data_list = []
        for item in OpportunityConfigStage.objects.filter(company=opp_obj.company, is_delete=False):
            condition_datas = []
            for data in item.condition_datas:
                condition_datas.append(
                    data['condition_property']['title']
                    + str(data['comparison_operator'].encode('utf-8'))
                    .replace("b'='", '=')
                    .replace("b'\\xe2\\x89\\xa0'", '!=')
                    + str(data['compare_data'])
                )
            opp_config_stage_data_list.append({
                'id': str(item.id),
                'indicator': item.indicator,
                'win_rate': item.win_rate,
                'logical_operator': item.logical_operator,
                'condition': condition_datas
            })
        return opp_config_stage_data_list

    @classmethod
    def get_opp_condition_data_list(cls, opp_obj):
        opp_condition_data_list = []
        quotation_status = opp_obj.quotation.system_status if opp_obj.quotation else None
        # Quotation Status
        opp_condition_data_list.append('Quotation Status=0' if quotation_status == 3 else 'Quotation Status!=0')
        # Order Status
        so_mapped = opp_obj.sale_order_opportunity.filter(system_status=3)
        lo_mapped = opp_obj.lease_opportunity.filter(system_status=3)
        svr_mapped = opp_obj.serviceorder_serviceorder_opp.filter(system_status=3)
        order_status= 'Order Status!=0'
        if so_mapped.count() > 0 or lo_mapped.count() > 0 or svr_mapped.count() > 0:
            order_status = 'Order Status=0'
        opp_condition_data_list.append(order_status)
        # Order Delivery Status
        so_delivery_mapped = OrderDeliverySub.objects.filter(
            sale_order_id__in=so_mapped.values_list('id', flat=True), system_status=3
        )
        lo_delivery_mapped = OrderDeliverySub.objects.filter(
            lease_order_id__in=lo_mapped.values_list('id', flat=True), system_status=3
        )
        svr_delivery_mapped = OrderDeliverySub.objects.filter(
            service_order_id__in=svr_mapped.values_list('id', flat=True), system_status=3
        )
        delivery_status = 'Order Delivery Status!=0'
        if so_delivery_mapped.count() > 0 or lo_delivery_mapped.count() > 0 or svr_delivery_mapped.count() > 0:
            delivery_status = 'Order Delivery Status=0'
        opp_condition_data_list.append(delivery_status)
        # Customer Annual Revenue
        customer = opp_obj.customer if opp_obj.customer else None
        opp_condition_data_list.append('Customer=0' if not customer else 'Customer!=0')
        if 'Customer!=0' in opp_condition_data_list:
            opp_condition_data_list.append('Customer=' + str(customer.total_employees))
        # Product Category
        product_category = opp_obj.product_category.all()
        opp_condition_data_list.append('Product Category=0' if product_category.count() == 0 else 'Product Category!=0')
        # Budget
        opp_condition_data_list.append('Budget=0' if opp_obj.budget_value <= 0 else 'Budget!=0')
        # Open Date
        opp_condition_data_list.append('Open Date=0' if not opp_obj.open_date else 'Open Date!=0')
        # Close Date
        opp_condition_data_list.append('Close Date=0' if not opp_obj.close_date else 'Close Date!=0')
        # Decision Maker
        opp_condition_data_list.append('Decision Maker=0' if not opp_obj.decision_maker else 'Decision Maker!=0')
        # Product Line Detail
        product_line = opp_obj.opportunity_product_opportunity.all()
        opp_condition_data_list.append(
            'Product Line Detail=0' if product_line.count() == 0 else 'Product Line Detail!=0'
        )
        # Competitor Win
        competitors = opp_obj.opportunity_competitor_opportunity.filter(win_deal=True)
        opp_condition_data_list.append('Competitor Win!=0' if competitors.count() == 0 else 'Competitor Win=0')
        # Lost By Other Reason
        opp_condition_data_list.append(
            'Lost By Other Reason=0' if opp_obj.lost_by_other_reason else 'Lost By Other Reason!=0'
        )
        return opp_condition_data_list

    @classmethod
    def index_current_stage(cls, passed_stage_list, current_stage_indicator, current_stage_id):
        new_opp_stage_data_list = []
        for stage in passed_stage_list:
            if stage.get('indicator') in ['Closed Lost', 'Delivery', 'Deal Close']:
                if stage.get('indicator') in current_stage_indicator:
                    current = 1 if str(stage.get('id')) == current_stage_id else 0
                    new_opp_stage_data_list.append({
                        'id': str(stage.get('id')),
                        'indicator': stage.get('indicator'),
                        'win_rate': stage.get('win_rate'),
                        'current': current
                    })
            else:
                current = 1 if str(stage.get('id')) == current_stage_id else 0
                new_opp_stage_data_list.append({
                    'id': str(stage.get('id')),
                    'indicator': stage.get('indicator'),
                    'win_rate': stage.get('win_rate'),
                    'current': current
                })
        return new_opp_stage_data_list

    @classmethod
    def check_or_logic(cls, stage_condition, opp_condition_data_list):
        flag = False
        for item in stage_condition:
            if item in opp_condition_data_list:
                flag = True
                break
        return flag

    @classmethod
    def check_and_logic(cls, stage_condition, opp_condition_data_list):
        flag = True
        for item in stage_condition:
            if item not in opp_condition_data_list:
                flag = False
        return flag

    @classmethod
    def get_new_opp_stage_data_list(cls, opp_config_stage_data_list, opp_condition_data_list, opp_obj):
        opp_range_stage_list = []
        current_stage_indicator = []
        for stage in opp_config_stage_data_list:
            if stage.get('logical_operator') == 1:
                if cls.check_or_logic(stage.get('condition'), opp_condition_data_list):
                    current_stage_indicator.append(stage.get('indicator'))
                    opp_range_stage_list.append({
                        'id': str(stage.get('id')),
                        'indicator': stage.get('indicator'),
                        'win_rate': stage.get('win_rate'),
                        'current': 0
                    })
            else:
                if cls.check_and_logic(stage.get('condition'), opp_condition_data_list):
                    current_stage_indicator.append(stage.get('indicator'))
                    opp_range_stage_list.append({
                        'id': str(stage.get('id')),
                        'indicator': stage.get('indicator'),
                        'win_rate': stage.get('win_rate'),
                        'current': 0
                    })

            if stage.get('indicator') == 'Deal Close' and opp_obj.is_deal_closed:
                current_stage_indicator.append(stage.get('indicator'))
                opp_range_stage_list.append({
                    'id': str(stage.get('id')),
                    'indicator': stage.get('indicator'),
                    'win_rate': stage.get('win_rate'),
                    'current': 0
                })

        if len(opp_range_stage_list) > 0:
            # lớn tới bé
            current_stage_id = None
            sorted_opp_range_stage_list = sorted(opp_range_stage_list, key=lambda x: x['win_rate'], reverse=True)
            if sorted_opp_range_stage_list[-1].get('win_rate') == 0:
                sorted_opp_range_stage_list[-1]['current'] = 1
                current_stage_id = str(sorted_opp_range_stage_list[-1]['id'])
            else:
                sorted_opp_range_stage_list[0]['current'] = 1
                current_stage_id = str(sorted_opp_range_stage_list[0]['id'])

            print('sorted_opp_range_stage_list')
            for item in sorted_opp_range_stage_list:
                print(item)
            passed_stage_list = [
                item for item in opp_config_stage_data_list if
                item.get('win_rate', 0) <= sorted_opp_range_stage_list[0].get('win_rate')
            ]
            print('passed_stage_list')
            for item in passed_stage_list:
                print(item)
            new_opp_stage_data_list = cls.index_current_stage(
                passed_stage_list, current_stage_indicator, current_stage_id
            )
            print('new_opp_stage_data_list')
            for item in new_opp_stage_data_list:
                print(item)
            return new_opp_stage_data_list
        raise serializers.ValidationError({'current stage': OpportunityMsg.ERROR_WHEN_GET_NULL_CURRENT_STAGE})
