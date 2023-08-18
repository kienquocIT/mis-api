from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Product, ProductCategory, UnitOfMeasure, Tax, Contact
from apps.masterdata.saledata.models import Account
from apps.masterdata.saledata.serializers import AccountForSaleListSerializer
from apps.sales.opportunity.models import Opportunity, OpportunityProductCategory, OpportunityProduct, \
    OpportunityCompetitor, OpportunityContactRole, OpportunityCustomerDecisionFactor, OpportunitySaleTeamMember, \
    OpportunityConfigStage, OpportunityStage
from apps.shared import AccountsMsg, HRMsg
from apps.shared.translations.opportunity import OpportunityMsg


class OpportunityListSerializer(serializers.ModelSerializer):
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
            return {
                'id': obj.customer_id,
                'title': obj.customer.name,
                'code': obj.customer.code,
                'shipping_address': obj.customer.shipping_address
            }
        return {}

    @classmethod
    def get_sale_person(cls, obj):
        if obj.employee_inherit:
            return {
                'id': obj.employee_inherit_id,
                'name': obj.employee_inherit.get_full_name(),
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


class OpportunityCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    customer = serializers.UUIDField()
    product_category = serializers.ListField(child=serializers.UUIDField(), required=False)
    sale_person = serializers.UUIDField()

    class Meta:
        model = Opportunity
        fields = (
            'title',
            'customer',
            'product_category',
            'sale_person',
            'open_date',
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
    def validate_sale_person(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    def create(self, validated_data):
        # get data product_category
        product_categories = validated_data.pop('product_category', [])

        # get stage Qualification (auto assign stage Qualification when create Opportunity)
        stage = OpportunityConfigStage.objects.get_current(fill__company=True, indicator='Qualification')
        win_rate = stage.win_rate

        opportunity = Opportunity.objects.create(**validated_data, win_rate=win_rate)
        CommonOpportunityUpdate.create_product_category(product_categories, opportunity)
        OpportunityStage.objects.create(stage=stage, opportunity=opportunity, is_current=True)
        return opportunity


class OpportunityProductCreateSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(allow_null=True)
    product_category = serializers.UUIDField(allow_null=False, required=True)
    uom = serializers.UUIDField(allow_null=False)
    tax = serializers.UUIDField(allow_null=False)

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
                    tax_id=item['tax']['id'],
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
    def update_opportunity_sale_team(cls, data, instance):
        # delete old record
        OpportunitySaleTeamMember.objects.filter(opportunity=instance).delete()
        # create new
        bulk_data = []
        for item in data:
            bulk_data.append(
                OpportunitySaleTeamMember(
                    opportunity=instance,
                    member_id=item['member']['id']
                )
            )
        OpportunitySaleTeamMember.objects.bulk_create(bulk_data)
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
                    'title': obj.title,
                }
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': OpportunityMsg.NOT_EXIST})
        return None


class OpportunitySaleTeamMemberCreateSerializer(serializers.ModelSerializer):
    member = serializers.UUIDField(allow_null=False)

    class Meta:
        model = OpportunitySaleTeamMember
        fields = (
            'member',
        )

    @classmethod
    def validate_member(cls, value):
        try:  # noqa
            if value is not None:
                obj = Employee.objects.get(
                    id=value
                )
                return {
                    'id': str(obj.id),
                    'name': obj.get_full_name(),
                    'email': obj.email,
                }
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee': OpportunityMsg.NOT_EXIST})
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
    sale_person = serializers.UUIDField(required=False)
    opportunity_sale_team_datas = OpportunitySaleTeamMemberCreateSerializer(required=False, many=True)
    stage = serializers.UUIDField(required=False)
    lost_by_other_reason = serializers.BooleanField(required=False)
    list_stage = OpportunityStageUpdateSerializer(required=False, many=True)

    class Meta:
        model = Opportunity
        fields = (
            'title',
            'customer',
            'product_category',
            'sale_person',
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
            'opportunity_sale_team_datas',
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
    def validate_sale_person(cls, value):
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

        if 'opportunity_sale_team_datas' in validated_data:
            CommonOpportunityUpdate.update_opportunity_sale_team(
                validated_data['opportunity_sale_team_datas'],
                instance
            )

        if 'list_stage' in validated_data:
            list_stage = validated_data.pop('list_stage', [])
            CommonOpportunityUpdate.update_opportunity_stage(
                list_stage,
                instance
            )

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class OpportunityDetailSerializer(serializers.ModelSerializer):
    decision_maker = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()
    quotation = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()

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
            'opportunity_sale_team_datas',
            'stage',
            'lost_by_other_reason',
            'sale_order',
            'quotation',
            'is_close_lost',
            'is_deal_close',
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
        if obj.sale_person:
            return {
                'id': obj.sale_person_id,
                'name': obj.sale_person.get_full_name(),
                'code': obj.sale_person.code,
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
                'system_status': obj.sale_order.system_status,
            }
        return {}

    @classmethod
    def get_quotation(cls, obj):
        if obj.quotation:
            return {
                'id': obj.quotation_id,
                'code': obj.quotation.code,
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
                'name': obj.sale_person.get_full_name(),
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
