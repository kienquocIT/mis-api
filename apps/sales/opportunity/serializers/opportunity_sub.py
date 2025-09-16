from rest_framework import serializers
from apps.masterdata.saledata.models import Product, ProductCategory, UnitOfMeasure, Tax, Contact
from apps.masterdata.saledata.models import Account
from apps.sales.opportunity.models import (
    OpportunityProductCategory, OpportunityProduct,
    OpportunityCompetitor, OpportunityContactRole, OpportunityCustomerDecisionFactor, OpportunitySaleTeamMember,
    OpportunityConfigStage, OpportunityStage,
)
from apps.shared.translations.opportunity import OpportunityMsg


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
    def update_opportunity_stage_for_list(cls, instance):
        opp_config_stage = CheckOppStageFunction.get_opp_config_stage(instance)
        instance_stage = CheckOppStageFunction.get_instance_stage(instance)
        instance_current_stage = CheckOppStageFunction.get_instance_current_stage(
            opp_config_stage, instance_stage, instance
        )

        OpportunityStage.objects.filter(opportunity=instance).delete()
        data_bulk = []
        for item in instance_current_stage:
            data_bulk.append(
                OpportunityStage(opportunity=instance, stage_id=item['id'], is_current=item['current'])
            )
        if len(data_bulk) > 0:
            if data_bulk[-1].stage.indicator == 'Closed Lost' and 'SaleOrder Status=0' in instance_stage:
                raise serializers.ValidationError(
                    {'Closed Lost': 'Can not update to stage "Closed Lost". You are having an Approved Sale Order.'}
                )
        OpportunityStage.objects.bulk_create(data_bulk)
        return True


class CheckOppStageFunction:
    @classmethod
    def get_opp_config_stage(cls, instance):
        opp_config_stage = []
        for item in OpportunityConfigStage.objects.filter_current(
                company=instance.company, is_delete=False
        ):
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
        return opp_config_stage

    @classmethod
    def get_instance_stage(cls, instance):
        instance_stage = []
        quotation_status = instance.quotation.system_status if instance.quotation else None
        # Quotation Status
        instance_stage.append('Quotation Status=0' if quotation_status == 3 else 'Quotation Status!=0')
        # Sale Order Status
        sale_order_status = instance.sale_order.system_status if instance.sale_order else None
        instance_stage.append('SaleOrder Status=0' if sale_order_status == 3 else 'SaleOrder Status!=0')
        # Sale Order Delivery Status
        delivery_status = instance.sale_order.delivery_status if instance.sale_order else None
        instance_stage.append('SaleOrder Delivery Status=0' if delivery_status == 3 else 'SaleOrder Delivery Status!=0')
        # Customer Annual Revenue
        customer = instance.customer if instance.customer else None
        instance_stage.append('Customer=0' if not customer else 'Customer!=0')
        if 'Customer!=0' in instance_stage:
            instance_stage.append('Customer=' + str(customer.total_employees))
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
        instance_stage.append('Decision Maker=0' if not instance.decision_maker else 'Decision Maker!=0')
        # Product Line Detail
        product_line = instance.opportunity_product_opportunity.all()
        instance_stage.append('Product Line Detail=0' if product_line.count() == 0 else 'Product Line Detail!=0')
        # Competitor Win
        competitors = instance.opportunity_competitor_opportunity.filter(win_deal=True)
        instance_stage.append('Competitor Win!=0' if competitors.count() == 0 else 'Competitor Win=0')
        # Lost By Other Reason
        instance_stage.append('Lost By Other Reason=0' if instance.lost_by_other_reason else 'Lost By Other Reason!=0')
        return instance_stage

    @classmethod
    def get_instance_current_stage_range(cls, stages, current_stage_indicator):
        new_instance_current_stage = []
        for stage in stages:
            if stage.indicator in ['Closed Lost', 'Delivery', 'Deal Close']:
                if stage.indicator in current_stage_indicator:
                    if not stage.win_rate:
                        new_instance_current_stage[0]['current'] = 0
                        new_instance_current_stage.append({
                            'id': stage.id,
                            'indicator': stage.indicator,
                            'win_rate': stage.win_rate,
                            'current': 1
                        })
                    else:
                        new_instance_current_stage.append({
                            'id': stage.id,
                            'indicator': stage.indicator,
                            'win_rate': stage.win_rate,
                            'current': 1 if len(new_instance_current_stage) == 0 else 0
                        })
            else:
                if not stage.win_rate:
                    new_instance_current_stage[0]['current'] = 0
                    new_instance_current_stage.append({
                        'id': stage.id,
                        'indicator': stage.indicator,
                        'win_rate': stage.win_rate,
                        'current': 1
                    })
                else:
                    new_instance_current_stage.append({
                        'id': stage.id,
                        'indicator': stage.indicator,
                        'win_rate': stage.win_rate,
                        'current': 1 if len(new_instance_current_stage) == 0 else 0
                    })
        return new_instance_current_stage

    @classmethod
    def check_or(cls, stage_condition, instance_stage):
        flag = False
        for item in stage_condition:
            if item in instance_stage:
                flag = True
                break
        return flag

    @classmethod
    def check_and(cls, stage_condition, instance_stage):
        flag = True
        for item in stage_condition:
            if item not in instance_stage:
                flag = False
        return flag

    @classmethod
    def get_instance_current_stage(cls, opp_config_stage, instance_stage, instance):
        instance_current_stage = []
        current_stage_indicator = []
        for stage in opp_config_stage:
            if stage['logical_operator']:
                if cls.check_or(stage['condition'], instance_stage):
                    current_stage_indicator.append(stage['indicator'])
                    instance_current_stage.append({
                        'id': stage['id'], 'indicator': stage['indicator'], 'win_rate': stage['win_rate'], 'current': 0
                    })
            else:
                if cls.check_and(stage['condition'], instance_stage):
                    current_stage_indicator.append(stage['indicator'])
                    instance_current_stage.append({
                        'id': stage['id'], 'indicator': stage['indicator'], 'win_rate': stage['win_rate'], 'current': 0
                    })

            if stage['indicator'] == 'Deal Close' and instance.is_deal_close:
                current_stage_indicator.append(stage['indicator'])
                instance_current_stage.append({
                    'id': stage['id'], 'indicator': stage['indicator'], 'win_rate': stage['win_rate'], 'current': 0
                })

        if len(instance_current_stage) > 0:
            instance_current_stage = sorted(instance_current_stage, key=lambda x: x['win_rate'], reverse=True)
            if instance_current_stage[-1]['win_rate'] == 0:
                instance_current_stage[-1]['current'] = 1
            else:
                instance_current_stage[0]['current'] = 1

            stages = OpportunityConfigStage.objects.filter(
                company_id=instance.company_id,
                win_rate__lte=instance_current_stage[0]['win_rate'],
                is_delete=False
            ).order_by('-win_rate')
            new_instance_current_stage = cls.get_instance_current_stage_range(stages, current_stage_indicator)

            return new_instance_current_stage
        raise serializers.ValidationError({'current stage': OpportunityMsg.ERROR_WHEN_GET_NULL_CURRENT_STAGE})
