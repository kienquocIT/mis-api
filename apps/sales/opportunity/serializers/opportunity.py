import datetime
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.hr.models import Employee
from apps.core.process.utils import ProcessRuntimeControl
from apps.masterdata.saledata.models import Contact
from apps.masterdata.saledata.models import Account
from apps.masterdata.saledata.models.accounts import AccountActivity
from apps.sales.lead.models import LeadHint
from apps.sales.opportunity.models import (
    Opportunity, OpportunitySaleTeamMember, OpportunityConfigStage, OpportunityStage,
)
from apps.sales.opportunity.serializers.opportunity_sub import (
    OpportunityCommonFunction,
    OpportunityProductCreateSerializer, OpportunityCompetitorCreateSerializer,
    OpportunityContactRoleCreateSerializer, OpportunityStageUpdateSerializer
)
from apps.sales.quotation.models import QuotationAppConfig
from apps.sales.report.models import ReportPipeline
from apps.shared import AccountsMsg, HRMsg, SaleMsg, DisperseModel
from apps.shared.translations.opportunity import OpportunityMsg


__all__ = [
    'OpportunityListSerializer',
    'OpportunityCreateSerializer',
    'OpportunityUpdateSerializer',
    'OpportunityDetailSerializer',
]


# main
class OpportunityListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()
    is_close = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()
    quotation = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'sale_person',
            'open_date',
            'quotation',
            'sale_order',
            'opportunity_sale_team_datas',
            'close_date',
            'date_created',
            'stage',
            'is_close'
        )

    @classmethod
    def get_customer(cls, obj):
        if obj.customer:
            return {
                'id': obj.customer_id,
                'name': obj.customer.name,
                'code': obj.customer.code,
                'tax_code': obj.customer.tax_code,
                'contact_mapped': [{
                    'id': str(item.id),
                    'fullname': item.fullname,
                    'email': item.email
                } for item in obj.customer.contact_account_name.all()],
                'phone': obj.customer.phone,
                'email': obj.customer.email,
                'shipping_address': [item.address_data for item in obj.customer.account_mapped_shipping_address.all()]
            }
        return {}

    @classmethod
    def get_sale_person(cls, obj):
        if obj.employee_inherit:
            return {
                'id': obj.employee_inherit_id,
                'full_name': obj.employee_inherit.get_full_name(),
                'code': obj.employee_inherit.code,
                'first_name': obj.employee_inherit.first_name,
                'last_name': obj.employee_inherit.last_name,
                'email': obj.employee_inherit.email,
                'is_active': obj.employee_inherit.is_active,
            }
        return {}

    @classmethod
    def get_stage(cls, obj):
        return obj.current_stage_data

    @classmethod
    def get_is_close(cls, obj):
        if obj.is_deal_close or obj.is_close_lost:
            return True
        return False

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'code': obj.sale_order.code,
            'title': obj.sale_order.title,
        } if obj.sale_order else {}

    @classmethod
    def get_quotation(cls, obj):
        return {
            'id': obj.quotation_id,
            'code': obj.quotation.code,
            'title': obj.quotation.title,
        } if obj.quotation else {}


class OpportunityCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    customer = serializers.UUIDField()
    product_category = serializers.ListField(child=serializers.UUIDField(), required=False)
    employee_inherit_id = serializers.UUIDField()
    process_config = serializers.UUIDField(allow_null=True, default=None, required=False)

    class Meta:
        model = Opportunity
        fields = (
            'process_config',  # process
            'title',
            'customer',
            'product_category',
            'employee_inherit_id',
        )

    @classmethod
    def validate_process_config(cls, attrs):
        return ProcessRuntimeControl.get_process_config(process_config_id=attrs, for_opp=True) if attrs else None

    @classmethod
    def validate_customer(cls, value):
        try:
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'detail': AccountsMsg.ACCOUNT_NOT_EXIST})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            emp = Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return emp.id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    @classmethod
    def validate_config_role(cls, validate_data):
        if 'employee_inherit_id' in validate_data:
            model_cls = DisperseModel(app_model="hr.employee").get_model()
            if model_cls and hasattr(model_cls, 'objects'):
                so_config = QuotationAppConfig.objects.filter_current(fill__tenant=True, fill__company=True).first()
                employee = model_cls.objects.filter(id=validate_data['employee_inherit_id']).first()
                if so_config and employee:
                    ss_role = [role.id for role in so_config.ss_role.all()]
                    for role in employee.role.all():
                        if role.id in ss_role:
                            raise serializers.ValidationError({'detail': SaleMsg.SO_CONFIG_SS_ROLE_CHECK})
        return True

    def validate(self, validate_data):
        self.validate_config_role(validate_data=validate_data)
        init_stage = OpportunityConfigStage.objects.filter_current(
            fill__company=True, indicator='Qualification', is_delete=False
        ).first()
        if init_stage:
            validate_data['current_stage'] = init_stage
            validate_data['current_stage_data'] = {
                'id': str(init_stage.id),
                'indicator': init_stage.indicator,
                'win_rate': init_stage.win_rate
            } if init_stage else {}
            validate_data['win_rate'] = init_stage.win_rate
        else:
            raise serializers.ValidationError({'stage': _('Can not found the init Stage')})
        if 'lead' in self.context:
            lead_obj = self.context.get('lead')
            if not lead_obj:
                raise serializers.ValidationError({'lead': _('Lead not found.')})
            validate_data['lead'] = lead_obj
            lead_config = lead_obj.lead_configs.first()
            if not lead_config:
                raise serializers.ValidationError({'lead_config': _('Lead config not found.')})
            validate_data['lead_config'] = lead_config
            if lead_config.convert_opp:
                raise serializers.ValidationError({'converted': _('Already converted to opportunity.')})
        return validate_data

    def create(self, validated_data):
        # handle process
        process_config = validated_data.pop('process_config', None)

        # get data product_category
        product_categories = validated_data.pop('product_category', [])

        # get stage Qualification (auto assign stage Qualification when create Opportunity)
        init_stage = validated_data.pop('current_stage')

        employee_inherit = Employee.objects.get(id=validated_data['employee_inherit_id'])
        sale_team_data = [
            {
                'member': {
                    'id': str(employee_inherit.id),
                    'full_name': employee_inherit.get_full_name(),
                    'code': employee_inherit.code,
                    'email': employee_inherit.email,
                }
            }
        ]

        if 'lead' in self.context:
            lead_obj = validated_data.pop('lead')
            lead_config = validated_data.pop('lead_config')
            opportunity = Opportunity.objects.create(
                **validated_data,
                opportunity_sale_team_datas=sale_team_data,
                open_date=datetime.datetime.now(),
                system_status=1
            )
            OpportunityCommonFunction.convert_opportunity(lead_obj, lead_config, opportunity)
        else:
            opportunity = Opportunity.objects.create(
                **validated_data,
                opportunity_sale_team_datas=sale_team_data,
                open_date=datetime.datetime.now(),
                system_status=1
            )

        if Opportunity.objects.filter_on_company(code=opportunity.code).count() > 1:
            raise serializers.ValidationError({'detail': HRMsg.INVALID_SCHEMA})

        # create M2M Opportunity and Product Category
        OpportunityCommonFunction.create_product_category(product_categories, opportunity)
        # create stage default for Opportunity
        OpportunityStage.objects.create(stage=init_stage, opportunity=opportunity, is_current=True)
        # set sale_person in sale team
        OpportunitySaleTeamMember.objects.create(
            tenant_id=opportunity.tenant_id,
            company_id=opportunity.company_id,
            opportunity=opportunity,
            member=employee_inherit,
            permit_view_this_opp=True,
            permit_add_member=True,
            permission_by_configured=OpportunityCommonFunction.get_alias_permit_from_general(
                employee_obj=employee_inherit
            )
        )

        # push to report pipeline
        ReportPipeline.push_from_opp(
            tenant_id=opportunity.tenant_id,
            company_id=opportunity.company_id,
            opportunity_id=opportunity.id,
            employee_inherit_id=opportunity.employee_inherit_id,
        )
        # push to customer activity
        if opportunity.customer:
            AccountActivity.push_activity(
                tenant_id=opportunity.tenant_id,
                company_id=opportunity.company_id,
                account_id=opportunity.customer_id,
                app_code=opportunity._meta.label_lower,
                document_id=opportunity.id,
                title=opportunity.title,
                code=opportunity.code,
                date_activity=opportunity.date_created,
                revenue=None,
            )

        # handle process after create opp
        if process_config:
            process_obj = ProcessRuntimeControl.create_process_from_config(
                title=opportunity.title,
                remark=process_config.remark,
                config=process_config,
                opp=opportunity,
                employee_created=opportunity.employee_created,
            )
            ProcessRuntimeControl(process_obj=process_obj).play_process()
            # update Process to Opp
            opportunity.process = process_obj
            opportunity.save(update_fields=['process'])

        return opportunity


class OpportunityDetailSerializer(serializers.ModelSerializer):
    decision_maker = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()
    quotation = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    end_customer = serializers.SerializerMethodField()
    product_category = serializers.SerializerMethodField()
    customer_decision_factor = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'end_customer',
            'product_category',
            'budget_value',
            'open_date',
            'close_date',
            'decision_maker',
            'opportunity_product_datas',
            'total_product_pretax_amount',
            'total_product_tax',
            'total_product',
            'opportunity_competitors_datas',
            'opportunity_contact_role_datas',
            'win_rate',
            'current_stage_data',
            'is_input_rate',
            'customer_decision_factor',
            'sale_person',
            'stage',
            'lost_by_other_reason',
            'sale_order',
            'quotation',
            'is_close_lost',
            'is_deal_close',
            'members',
            'estimated_gross_profit_percent',
            'estimated_gross_profit_value',
            'process'
        )

    @classmethod
    def get_decision_maker(cls, obj):
        if obj.decision_maker:
            return {
                'id': obj.decision_maker.id,
                'name': obj.decision_maker.fullname,
            }
        return {}

    @classmethod
    def get_sale_person(cls, obj):
        if obj.employee_inherit:
            return {
                'id': obj.employee_inherit_id,
                'full_name': obj.employee_inherit.get_full_name(),
                'code': obj.employee_inherit.code,
                'group': {
                    'id': obj.employee_inherit.group_id,
                    'code': obj.employee_inherit.group.code,
                    'title': obj.employee_inherit.group.title
                } if obj.employee_inherit.group else {}
            }
        return {}

    @classmethod
    def get_sale_order(cls, obj):
        if obj.sale_order:
            if hasattr(obj.sale_order, 'delivery_of_sale_order'):
                delivery = obj.sale_order.delivery_of_sale_order
                return {
                    'id': obj.sale_order_id,
                    'code': obj.sale_order.code,
                    'title': obj.sale_order.title,
                    'system_status': obj.sale_order.system_status,
                    'delivery': {
                        'id': delivery.id,
                        'code': delivery.code,
                    }
                }
            return {
                'id': obj.sale_order_id,
                'code': obj.sale_order.code,
                'title': obj.sale_order.title,
                'system_status': obj.sale_order.system_status,
            }
        return {}

    @classmethod
    def get_quotation(cls, obj):
        if obj.quotation:
            return {
                'id': obj.quotation_id,
                'code': obj.quotation.code,
                'title': obj.quotation.title,
                'system_status': obj.quotation.system_status,
                'is_customer_confirm': obj.quotation.is_customer_confirm,
            }
        return {}

    @classmethod
    def get_stage(cls, obj):
        return [{
            'id': item.id,
            'is_deal_closed': item.is_deal_closed,
            'is_closed_lost': item.is_closed_lost,
            'is_delivery': item.is_delivery,
            'indicator': item.indicator,
            'win_rate': item.win_rate,
        } for item in obj.stage.all()]

    @classmethod
    def get_customer(cls, obj):
        if obj.customer:
            return {
                'id': obj.customer_id,
                'code': obj.code,
                'name': obj.customer.name,
                'annual_revenue': obj.customer.annual_revenue,
                'shipping_address': [{
                    'full_address': item.full_address,
                    'is_default': item.is_default
                } for item in obj.customer.account_mapped_shipping_address.all()],
                'contact_mapped': [{
                    'id': str(item.id),
                    'fullname': item.fullname,
                    'email': item.email
                } for item in obj.customer.contact_account_name.all()]
            }
        return {}

    @classmethod
    def get_end_customer(cls, obj):
        if obj.end_customer:
            return {
                'id': obj.end_customer_id,
                'name': obj.end_customer.name,
            }
        return {}

    @classmethod
    def get_product_category(cls, obj):
        if obj.product_category:
            categories = obj.product_category.all()
            return [{
                'id': category.id,
                'title': category.title,
            } for category in categories]
        return []

    @classmethod
    def get_customer_decision_factor(cls, obj):
        factor = obj.customer_decision_factor.all()
        if factor:
            return [
                {
                    'id': item.id,
                    'title': item.title,
                } for item in factor
            ]
        return []

    def get_members(self, obj):
        allow_get_member = self.context.get('allow_get_member', False)
        return [
            {
                "id": item.id,
                "first_name": item.first_name,
                "last_name": item.last_name,
                "full_name": item.get_full_name(),
                "email": item.email,
                "avatar": item.avatar,
                "is_active": item.is_active,
                "group": {
                    'id': item.group_id,
                    'code': item.group.code,
                    'title': item.group.title
                } if item.group else {}
            } for item in obj.members.all().select_related('group')
        ] if allow_get_member else []

    @classmethod
    def get_process(cls, obj):
        return {
            'id': obj.process_id,
            'title': obj.process.title,
            'remark': obj.process.remark,
        } if obj.process else {}


class OpportunityUpdateSerializer(serializers.ModelSerializer):
    opportunity_product_datas = OpportunityProductCreateSerializer(required=False, many=True)
    opportunity_competitors_datas = OpportunityCompetitorCreateSerializer(required=False, many=True)
    customer = serializers.UUIDField(required=False)
    product_category = serializers.ListField(required=False, child=serializers.UUIDField())
    budget_value = serializers.FloatField(required=False)
    open_date = serializers.DateTimeField(required=False)
    close_date = serializers.DateTimeField(required=False)
    end_customer = serializers.UUIDField(required=False, allow_null=True)
    decision_maker = serializers.UUIDField(required=False, allow_null=True)
    total_product = serializers.FloatField(required=False, )
    total_product_pretax_amount = serializers.FloatField(required=False)
    total_product_tax = serializers.FloatField(required=False)
    win_rate = serializers.FloatField(required=False)
    customer_decision_factor = serializers.ListField(required=False, child=serializers.UUIDField())
    opportunity_contact_role_datas = OpportunityContactRoleCreateSerializer(many=True, required=False)
    title = serializers.CharField(max_length=100)
    is_input_rate = serializers.BooleanField(required=False)
    employee_inherit = serializers.UUIDField(required=False)
    stage = serializers.UUIDField(required=False)
    lost_by_other_reason = serializers.BooleanField(required=False)
    list_stage = OpportunityStageUpdateSerializer(required=False, many=True)
    estimated_gross_profit_percent = serializers.FloatField(required=False)
    estimated_gross_profit_value = serializers.FloatField(required=False)

    class Meta:
        model = Opportunity
        fields = (
            'title',
            'customer',
            'product_category',
            'employee_inherit',
            'budget_value',
            'open_date',
            'is_input_rate',
            'close_date',
            'decision_maker',
            'end_customer',
            'opportunity_product_datas',
            'total_product',
            'total_product_pretax_amount',
            'total_product_tax',
            'win_rate',
            'opportunity_competitors_datas',
            'opportunity_contact_role_datas',
            'customer_decision_factor',
            'stage',
            'lost_by_other_reason',
            'list_stage',
            'is_close_lost',
            'is_deal_close',
            'estimated_gross_profit_percent',
            'estimated_gross_profit_value'
        )

    @classmethod
    def validate_customer(cls, value):
        try:
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'detail': AccountsMsg.ACCOUNT_NOT_EXIST})

    @classmethod
    def validate_stage(cls, value):
        try:
            return OpportunityConfigStage.objects.get_current(
                id=value, is_delete=False
            )
        except OpportunityConfigStage.DoesNotExist:
            raise serializers.ValidationError({'stage': OpportunityMsg.NOT_EXIST})

    @classmethod
    def validate_end_customer(cls, value):
        if value:
            try:
                return Account.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=value
                )
            except Account.DoesNotExist:
                raise serializers.ValidationError({'detail': AccountsMsg.ACCOUNT_NOT_EXIST})
        return None

    @classmethod
    def validate_decision_maker(cls, value):
        if value:
            try:
                return Contact.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=value
                )
            except Contact.DoesNotExist:
                raise serializers.ValidationError({'contact': AccountsMsg.CONTACT_NOT_EXIST})
        return None

    @classmethod
    def validate_total_product(cls, value):
        if value < 0:
            raise serializers.ValidationError({'total product price': OpportunityMsg.VALUE_GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_total_product_tax(cls, value):
        if value < 0:
            raise serializers.ValidationError({'total product price': OpportunityMsg.VALUE_GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_total_product_pretax_amount(cls, value):
        if value < 0:
            raise serializers.ValidationError({'total product price': OpportunityMsg.VALUE_GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_win_rate(cls, value):
        if value < 0:
            raise serializers.ValidationError({'total product price': OpportunityMsg.VALUE_GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_employee_inherit(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    def update(self, instance, validated_data):
        if 'product_category' in validated_data:
            product_categories = validated_data.pop('product_category', [])
            OpportunityCommonFunction.update_product_category(
                product_categories,
                instance
            )

        if 'opportunity_product_datas' in validated_data:
            OpportunityCommonFunction.update_opportunity_product(
                validated_data['opportunity_product_datas'],
                instance
            )

        if 'opportunity_competitors_datas' in validated_data:
            OpportunityCommonFunction.update_opportunity_competitor(
                validated_data['opportunity_competitors_datas'],
                instance
            )

        if 'opportunity_contact_role_datas' in validated_data:
            OpportunityCommonFunction.update_opportunity_contact_role(
                validated_data['opportunity_contact_role_datas'],
                instance
            )

        if 'customer_decision_factor' in validated_data:
            factors = validated_data.pop('customer_decision_factor', [])
            OpportunityCommonFunction.update_customer_decision_factor(
                factors,
                instance
            )

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        OpportunityCommonFunction.update_opportunity_stage(instance)

        LeadHint.check_and_create_lead_hint(instance, None)

        return instance
