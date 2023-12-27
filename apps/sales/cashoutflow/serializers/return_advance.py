from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.cashoutflow.models import ReturnAdvance, ReturnAdvanceCost, AdvancePaymentCost
from apps.sales.opportunity.models import OpportunityActivityLogs
from apps.shared import RETURN_ADVANCE_MONEY_RECEIVED, SaleMsg, AbstractDetailSerializerModel
from apps.shared.translations.return_advance import ReturnAdvanceMsg


class ReturnAdvanceListSerializer(serializers.ModelSerializer):
    advance_payment = serializers.SerializerMethodField()
    money_received = serializers.SerializerMethodField()

    class Meta:
        model = ReturnAdvance
        fields = (
            'id',
            'code',
            'title',
            'advance_payment',
            'system_status',
            'money_received',
            'date_created',
            'return_total',
        )

    @classmethod
    def get_advance_payment(cls, obj):
        if obj.advance_payment:
            return {
                'id': obj.advance_payment.id,
                'code': obj.advance_payment.code,
                'title': obj.advance_payment.title
            }
        return {}

    @classmethod
    def get_money_received(cls, obj):
        return str(dict(RETURN_ADVANCE_MONEY_RECEIVED).get(obj.money_received))


class ReturnAdvanceCostCreateSerializer(serializers.ModelSerializer):
    advance_payment_cost = serializers.UUIDField(required=True)
    expense_type = serializers.UUIDField()

    class Meta:
        model = ReturnAdvanceCost
        fields = (
            'advance_payment_cost',
            'expense_name',
            'expense_type',
            'remain_value',
            'return_value',
        )

    @classmethod
    def validate_remain_value(cls, value):
        if value < 0:
            raise serializers.ValidationError({'Remain total': ReturnAdvanceMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_return_value(cls, value):
        if value < 0:
            raise serializers.ValidationError({'Input return': ReturnAdvanceMsg.GREATER_THAN_ZERO})
        return value

    def validate(self, validate_data):
        if validate_data['remain_value'] < validate_data['return_value']:
            raise serializers.ValidationError({'Input return': ReturnAdvanceMsg.RETURN_GREATER_THAN_REMAIN})
        return validate_data


class ReturnAdvanceCreateSerializer(serializers.ModelSerializer):
    cost = ReturnAdvanceCostCreateSerializer(required=True, many=True)

    class Meta:
        model = ReturnAdvance
        fields = (
            'title',
            'advance_payment',
            'method',
            'employee_created_id',
            'employee_inherit',
            'system_status',
            'money_received',
            'cost',
        )

    def validate(self, validate_data):
        if validate_data.get('advance_payment', None):
            if validate_data['advance_payment'].system_status != 3:
                raise serializers.ValidationError({'detail': SaleMsg.ADVANCE_PAYMENT_NOT_FINISH})
            if validate_data['advance_payment'].opportunity_mapped:
                opp = validate_data['advance_payment'].opportunity_mapped
                if opp.is_close_lost is True or opp.is_deal_close:
                    raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        count_expense = AdvancePaymentCost.objects.filter(
            advance_payment_id=validate_data['advance_payment'],
        ).count()
        if len(validate_data['cost']) != count_expense:
            raise serializers.ValidationError({'Expense': ReturnAdvanceMsg.NOT_MAP_AP})
        return validate_data

    @classmethod
    def common_create_return_advance_cost(cls, validate_data, return_advance):
        data_bulk = []
        return_total = 0
        for data in validate_data:
            return_total += data['return_value']
            data_bulk.append(
                ReturnAdvanceCost(
                    return_advance=return_advance,
                    advance_payment_cost_id=data['advance_payment_cost'],
                    expense_name=data['expense_name'],
                    expense_type_id=data['expense_type'],
                    remain_value=data['remain_value'],
                    return_value=data['return_value']
                )
            )
        ReturnAdvanceCost.objects.filter(return_advance=return_advance).delete()
        ReturnAdvanceCost.objects.bulk_create(data_bulk)
        return_advance.return_total = return_total
        return_advance.save(update_fields=['return_total'])
        return True

    @decorator_run_workflow
    def create(self, validated_data):
        data_cost = validated_data.pop('cost')
        return_ad = ReturnAdvance.objects.create(**validated_data)
        self.common_create_return_advance_cost(validate_data=data_cost, return_advance=return_ad)

        # create activity log for opportunity
        if return_ad.advance_payment.opportunity_mapped:
            OpportunityActivityLogs.create_opportunity_log_application(
                tenant_id=return_ad.tenant_id,
                company_id=return_ad.company_id,
                opportunity_id=return_ad.advance_payment.opportunity_mapped_id,
                employee_created_id=return_ad.employee_created_id,
                app_code=str(return_ad.__class__.get_model_code()),
                doc_id=return_ad.id,
                title=return_ad.title,
            )

        return return_ad


class ReturnAdvanceDetailSerializer(AbstractDetailSerializerModel):
    cost = serializers.SerializerMethodField()
    advance_payment = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = ReturnAdvance
        fields = (
            'id',
            'code',
            'title',
            'advance_payment',
            'employee_created',
            'employee_inherit',
            'method',
            'system_status',
            'money_received',
            'date_created',
            'cost',
            'return_total'
        )

    @classmethod
    def get_advance_payment(cls, obj):
        if obj.advance_payment:
            return {
                'id': obj.advance_payment_id,
                'title': obj.advance_payment.title,
                'opportunity_mapped': {
                    'id': obj.advance_payment.opportunity_mapped_id,
                    'code': obj.advance_payment.opportunity_mapped.code,
                    'title': obj.advance_payment.opportunity_mapped.title,
                } if obj.advance_payment.opportunity_mapped else {},
                'quotation_mapped': {
                    'id': obj.advance_payment.quotation_mapped_id,
                    'code': obj.advance_payment.quotation_mapped.code,
                    'title': obj.advance_payment.quotation_mapped.title,
                } if obj.advance_payment.quotation_mapped else {},
                'sale_order_mapped': {
                    'id': obj.advance_payment.sale_order_mapped_id,
                    'code': obj.advance_payment.sale_order_mapped.code,
                    'title': obj.advance_payment.sale_order_mapped.title,
                } if obj.advance_payment.sale_order_mapped else {}
            }
        return {}

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                'id': obj.employee_inherit_id,
                'name': obj.employee_inherit.get_full_name(),
            }
        return {}

    @classmethod
    def get_cost(cls, obj):
        costs = ReturnAdvanceCost.objects.filter(return_advance=obj).select_related('expense_type')
        list_result = []
        for cost in costs:
            list_result.append(
                {
                    'id': cost.advance_payment_cost_id,
                    'expense_name': cost.expense_name,
                    'expense_type': {
                        'id': cost.expense_type_id,
                        'title': cost.expense_type.title,
                    },
                    'remain_total': cost.remain_value,
                    'return_value': cost.return_value,
                }
            )
        return list_result


class ReturnAdvanceUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    method = serializers.IntegerField(required=False)
    money_received = serializers.BooleanField(required=False)
    cost = ReturnAdvanceCostCreateSerializer(many=True)

    class Meta:
        model = ReturnAdvance
        fields = (
            'title',
            'method',
            'money_received',
            'cost',
            'system_status'
        )

    def update(self, instance, validated_data):
        if instance.advance_payment.system_status != 3:
            raise serializers.ValidationError({'detail': SaleMsg.ADVANCE_PAYMENT_NOT_FINISH})
        count_expense = AdvancePaymentCost.objects.filter(advance_payment=instance.advance_payment).count()
        if len(validated_data['cost']) != count_expense:
            raise serializers.ValidationError({'Expense': ReturnAdvanceMsg.NOT_MAP_AP})

        data_cost = validated_data.pop('cost')
        ReturnAdvanceCreateSerializer.common_create_return_advance_cost(
            validate_data=data_cost,
            return_advance=instance
        )
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
