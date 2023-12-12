# pylint: disable=C0302
import datetime
from uuid import uuid4
from rest_framework import serializers
from apps.core.hr.models import Employee, DistributionApplication
from apps.masterdata.saledata.models import Product, ProductCategory, UnitOfMeasure, Tax, Contact
from apps.masterdata.saledata.models import Account
from apps.masterdata.saledata.serializers import AccountForSaleListSerializer
from apps.sales.opportunity.models import (
    Opportunity, OpportunityProductCategory, OpportunityProduct,
    OpportunityCompetitor, OpportunityContactRole, OpportunityCustomerDecisionFactor, OpportunitySaleTeamMember,
    OpportunityConfigStage, OpportunityStage,
)
from apps.shared import AccountsMsg, HRMsg
from apps.shared.translations.opportunity import OpportunityMsg

__all__ = [
    'OpportunityListSerializer', 'OpportunityCreateSerializer', 'OpportunityUpdateSerializer',
    'OpportunityDetailSerializer', 'OpportunityForSaleListSerializer', 'OpportunityDetailSimpleSerializer',
    'CommonOpportunityUpdate'
]


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
            'stage',
            'is_close'
        )

    @classmethod
    def get_customer(cls, obj):
        if obj.customer:
            return {
                'id': obj.customer_id,
                'title': obj.customer.name,
                'code': obj.customer.code,
                'shipping_address': [
                    {'id': shipping.id, 'full_address': shipping.full_address}
                    for shipping in obj.customer.account_mapped_shipping_address.all()
                ],
                'billing_address': [
                    {'id': billing.id, 'full_address': billing.full_address}
                    for billing in obj.customer.account_mapped_billing_address.all()
                ],
                'contact_mapped': [{
                    'id': str(item.id),
                    'fullname': item.fullname,
                    'email': item.email
                } for item in obj.customer.contact_account_name.all()],
                'payment_term_customer_mapped': {
                    'id': obj.customer.payment_term_customer_mapped_id,
                    'title': obj.customer.payment_term_customer_mapped.title,
                    'code': obj.customer.payment_term_customer_mapped.code
                } if obj.customer.payment_term_customer_mapped else {},
                'price_list_mapped': {
                    'id': obj.customer.price_list_mapped_id,
                    'title': obj.customer.price_list_mapped.title,
                    'code': obj.customer.price_list_mapped.code
                } if obj.customer.price_list_mapped else {},
            }
        return {}

    @classmethod
    def get_sale_person(cls, obj):
        if obj.employee_inherit:
            return {
                'id': obj.employee_inherit_id,
                'full_name': obj.employee_inherit.get_full_name(),
                'code': obj.employee_inherit.code,
            }
        return {}

    @classmethod
    def get_stage(cls, obj):
        if obj.opportunity_stage_opportunity:
            stages = obj.opportunity_stage_opportunity.all()
            return [
                {
                    'id': stage.stage.id,
                    'is_current': stage.is_current,
                    'indicator': stage.stage.indicator
                } for stage in stages]
        return []

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
    title = serializers.CharField()
    customer = serializers.UUIDField()
    product_category = serializers.ListField(child=serializers.UUIDField(), required=False)
    employee_inherit_id = serializers.UUIDField()

    class Meta:
        model = Opportunity
        fields = (
            'title',
            'customer',
            'product_category',
            'employee_inherit_id',
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
    def get_alias_permit_from_general(cls, employee_obj):
        # Le Dieu Hoa - 10/17 11:17 AM
        #   Task: tạo - xem - sửa - xóa (cho chính nó / mọi người)
        #       e66cfb5a-b3ce-4694-a4da-47618f53de4c
        #   Quotation: tạo - xem - sửa - xóa (cho chính nó)
        #       b9650500-aba7-44e3-b6e0-2542622702a3
        #   Sales Order: tạo - xem - sửa - xóa (cho chính nó)
        #       a870e392-9ad2-4fe2-9baa-298a38691cf2
        #   Contract: tạo - xem - sửa - xóa (cho chính nó)
        #       31c9c5b0-717d-4134-b3d0-cc4ca174b168
        #   Advanced Payment: tạo - xem - sửa - xóa (cho chính nó / mọi người)
        #       57725469-8b04-428a-a4b0-578091d0e4f5
        #   Payment: tạo - xem - sửa - xóa (cho chính nó / mọi người)
        #       1010563f-7c94-42f9-ba99-63d5d26a1aca
        #   Return Payment: tạo - xem - sửa - xóa (cho chính nó / mọi người)
        #       65d36757-557e-4534-87ea-5579709457d7

        result = []
        app_id_get = [
            "e66cfb5a-b3ce-4694-a4da-47618f53de4c",  # Task
            "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
            "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sales Order
            "31c9c5b0-717d-4134-b3d0-cc4ca174b168",  # Contract
            "57725469-8b04-428a-a4b0-578091d0e4f5",  # Advanced Payment
            "1010563f-7c94-42f9-ba99-63d5d26a1aca",  # Payment
            "65d36757-557e-4534-87ea-5579709457d7",  # Return Payment
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

    def create(self, validated_data):
        # get data product_category
        product_categories = validated_data.pop('product_category', [])

        # get stage Qualification (auto assign stage Qualification when create Opportunity)
        stage = OpportunityConfigStage.objects.get_current(fill__company=True, indicator='Qualification')
        win_rate = stage.win_rate

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

        opportunity = Opportunity.objects.create(
            **validated_data,
            opportunity_sale_team_datas=sale_team_data,
            win_rate=win_rate,
            open_date=datetime.datetime.now()
        )

        if Opportunity.objects.filter_current(fill__tenant=True, fill__company=True, code=opportunity.code).count() > 1:
            raise serializers.ValidationError({'detail': HRMsg.INVALID_SCHEMA})

        # create M2M Opportunity and Product Category
        CommonOpportunityUpdate.create_product_category(product_categories, opportunity)
        # create stage default for Opportunity
        OpportunityStage.objects.create(stage=stage, opportunity=opportunity, is_current=True)
        # set sale_person in sale team
        OpportunitySaleTeamMember.objects.create(
            tenant_id=opportunity.tenant_id,
            company_id=opportunity.company_id,
            opportunity=opportunity,
            member=employee_inherit,
            permit_view_this_opp=True,
            permit_add_member=True,
            permission_by_configured=self.get_alias_permit_from_general(employee_obj=employee_inherit)
        )
        return opportunity


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


def get_instance_stage(instance):
    instance_stage = []
    # Quotation Confirm
    quotation_confirm = instance.quotation.is_customer_confirm if instance.quotation else None
    instance_stage.append('Quotation.confirm=0' if quotation_confirm else 'Quotation.confirm!=0')
    # Sale Order Status
    sale_order_status = instance.sale_order.system_status if instance.sale_order else None
    instance_stage.append('SaleOrder.status=0' if sale_order_status == 3 else 'SaleOrder.status!=0')
    # Sale Order Delivery Status
    delivery_status = instance.sale_order.delivery_status if instance.sale_order else None
    instance_stage.append('SaleOrder.Delivery.Status!=0' if delivery_status else 'SaleOrder.Delivery.Status=0')
    # Customer Annual Revenue
    customer_revenue = instance.customer.annual_revenue if instance.customer else None
    instance_stage.append('Customer=0' if not customer_revenue else 'Customer!=0')
    if 'Customer!=0' in instance_stage:
        instance_stage.append('Customer='+customer_revenue)
    # Product Category
    product_category = instance.product_category.all()
    instance_stage.append('Product Category=0' if product_category.count() == 0 else 'Product Category!=0')
    # Budget
    instance_stage.append('Budget=0' if instance.budget_value <= 0 else 'Budget!=0')
    # Open Date
    instance_stage.append('Open Date=0' if not instance.open_date else 'Open Date!=0')
    # Close Date
    instance_stage.append('Close Date=0' if not instance.close_date else 'Close Date!=0')
    # Decision Maker
    instance_stage.append('Decision maker=0' if not instance.decision_maker else 'Decision maker!=0')
    # Product Line Detail
    product_line = instance.opportunity_product_opportunity.all()
    instance_stage.append('Product.Line.Detail=0' if product_line.count() == 0 else 'Product.Line.Detail!=0')
    # Competitor Win
    competitors = instance.opportunity_competitor_opportunity.all()
    instance_stage.append('Competitor.Win!=0' if competitors.count() == 0 else 'Competitor.Win=0')
    # Lost By Other Reason
    instance_stage.append('Lost By Other Reason=0' if instance.lost_by_other_reason else 'Lost By Other Reason!=0')
    return instance_stage


class CommonOpportunityUpdate(serializers.ModelSerializer):
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
    def update_opportunity_stage(cls, data, instance):
        OpportunityStage.objects.filter(opportunity=instance).delete()

        data_bulk = []
        for item in data:
            opportunity_stage = OpportunityStage(
                opportunity=instance,
                stage_id=item['stage'],
                is_current=item['is_current']
            )
            data_bulk.append(opportunity_stage)
        OpportunityStage.objects.bulk_create(data_bulk)
        return True

    @classmethod
    def update_opportunity_stage_for_list(cls, instance):
        opp_config_stage = []
        for item in OpportunityConfigStage.objects.filter_current(fill__company=True):
            condition_datas = []
            for data in item.condition_datas:
                condition_datas.append(
                    data['condition_property']['title']
                    + str(data['comparison_operator'].encode('utf-8'))
                    .replace("b'='", '=')
                    .replace("b'\\xe2\\x89\\xa0'", '!=')
                    + str(data['compare_data'])
                )
            opp_config_stage.append({
                'id': item.id,
                'indicator': item.indicator,
                'win_rate': item.win_rate,
                'logical_operator': item.logical_operator,
                'condition': condition_datas
            })

        instance_stage = get_instance_stage(instance)

        instance_current_stage = []
        for stage in opp_config_stage:
            if stage['logical_operator']:
                flag = False
                for item in stage['condition']:
                    if item in instance_stage:
                        flag = True
                        break
                if flag:
                    instance_current_stage.append({
                        'id': stage['id'], 'indicator': stage['indicator'], 'win_rate': stage['win_rate'], 'current': 0
                    })
            else:
                flag = True
                for item in stage['condition']:
                    if item not in instance_stage:
                        flag = False
                if flag:
                    instance_current_stage.append({
                        'id': stage['id'], 'indicator': stage['indicator'], 'win_rate': stage['win_rate'], 'current': 0
                    })
        instance_current_stage = sorted(instance_current_stage, key=lambda x: x['win_rate'], reverse=True)
        instance_current_stage[0]['current'] = 1

        OpportunityStage.objects.filter(opportunity=instance).delete()
        data_bulk = []
        for item in instance_current_stage:
            opportunity_stage = OpportunityStage(opportunity=instance, stage_id=item['id'], is_current=item['current'])
            data_bulk.append(opportunity_stage)
        OpportunityStage.objects.bulk_create(data_bulk)
        return True


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
                    id=value
                )
                return obj.id
        except OpportunityConfigStage.DoesNotExist:
            raise serializers.ValidationError({'stage': OpportunityMsg.NOT_EXIST})
        return None


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
    title = serializers.CharField(required=False)
    is_input_rate = serializers.BooleanField(required=False)
    employee_inherit = serializers.UUIDField(required=False)
    stage = serializers.UUIDField(required=False)
    lost_by_other_reason = serializers.BooleanField(required=False)
    list_stage = OpportunityStageUpdateSerializer(required=False, many=True)

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
            'is_deal_close'
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
                fill__tenant=False,
                fill__company=True,
                id=value
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
            CommonOpportunityUpdate.update_product_category(
                product_categories,
                instance
            )

        if 'opportunity_product_datas' in validated_data:
            CommonOpportunityUpdate.update_opportunity_product(
                validated_data['opportunity_product_datas'],
                instance
            )

        if 'opportunity_competitors_datas' in validated_data:
            CommonOpportunityUpdate.update_opportunity_competitor(
                validated_data['opportunity_competitors_datas'],
                instance
            )

        if 'opportunity_contact_role_datas' in validated_data:
            CommonOpportunityUpdate.update_opportunity_contact_role(
                validated_data['opportunity_contact_role_datas'],
                instance
            )

        if 'customer_decision_factor' in validated_data:
            factors = validated_data.pop('customer_decision_factor', [])
            CommonOpportunityUpdate.update_customer_decision_factor(
                factors,
                instance
            )

        # if 'list_stage' in validated_data:
        #     list_stage = validated_data.pop('list_stage', [])
        #     CommonOpportunityUpdate.update_opportunity_stage(
        #         list_stage,
        #         instance
        #     )

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        CommonOpportunityUpdate.update_opportunity_stage_for_list(instance)
        return instance


class OpportunityDetailSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = (
            'id',
            'title',
            'code',
        )


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
            'is_input_rate',
            'customer_decision_factor',
            'sale_person',
            'stage',
            'lost_by_other_reason',
            'sale_order',
            'quotation',
            'is_close_lost',
            'is_deal_close',
            'members'
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
                    'title': obj.employee_inherit.group.title
                } if obj.employee_inherit.group else {}
            }
        return {}

    @classmethod
    def get_sale_order(cls, obj):
        if obj.sale_order:
            try:
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
            except Exception as err:
                print(err)
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
        stage = obj.stage.all()
        if stage:
            return [
                {
                    'id': item.id,
                    'is_deal_closed': item.is_deal_closed,
                    'indicator': item.indicator,
                } for item in stage
            ]
        return []

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
            } for item in obj.members.all()
        ] if allow_get_member else []


class OpportunityForSaleListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()
    is_close = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'sale_person',
            'open_date',
            'quotation_id',
            'sale_order_id',
            'opportunity_sale_team_datas',
            'close_date',
            'stage',
            'is_close'
        )

    @classmethod
    def get_customer(cls, obj):
        if obj.customer:
            return AccountForSaleListSerializer(obj.customer).data
        return {}

    @classmethod
    def get_sale_person(cls, obj):
        if obj.sale_person:
            return {
                'id': obj.sale_person_id,
                'full_name': obj.sale_person.get_full_name(),
                'code': obj.sale_person.code,
            }
        return {}

    @classmethod
    def get_stage(cls, obj):
        if obj.opportunity_stage_opportunity:
            stages = obj.opportunity_stage_opportunity.all()
            return [
                {
                    'id': stage.stage.id,
                    'is_current': stage.is_current,
                    'indicator': stage.stage.indicator
                } for stage in stages]
        return []

    @classmethod
    def get_is_close(cls, obj):
        if obj.is_deal_close or obj.is_close_lost:
            return True
        return False
