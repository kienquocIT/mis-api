from rest_framework import serializers
from apps.sales.cashoutflow.models import ReturnAdvance, ReturnAdvanceCost, AdvancePaymentCost, AdvancePayment
from apps.sales.opportunity.models import OpportunityActivityLogs
from apps.shared import RETURN_ADVANCE_STATUS, RETURN_ADVANCE_MONEY_RECEIVED, HRMsg, SaleMsg
from apps.shared.translations.return_advance import ReturnAdvanceMsg


class ReturnAdvanceListSerializer(serializers.ModelSerializer):
    advance_payment = serializers.SerializerMethodField()
    money_received = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = ReturnAdvance
        fields = (
            'id',
            'code',
            'title',
            'advance_payment',
            'status',
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

    @classmethod
    def get_status(cls, obj):
        return str(dict(RETURN_ADVANCE_STATUS).get(obj.status))


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
            'status',
            'money_received',
            'cost',
            'return_total',
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
        for data in validate_data:
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
            if return_advance.money_received:
                ap_updated = AdvancePaymentCost.objects.filter(id=data['advance_payment_cost']).first()
                ap_updated.sum_return_value = ap_updated.sum_return_value + float(data['return_value'])
                ap_updated.save()
        ReturnAdvanceCost.objects.bulk_create(data_bulk)
        return True

    def create(self, validated_data):
        data_cost = validated_data.pop('cost')
        return_ad = ReturnAdvance.objects.create(**validated_data)
        if ReturnAdvance.objects.filter_current(fill__tenant=True, fill__company=True, code=return_ad.code).count() > 1:
            raise serializers.ValidationError({'detail': HRMsg.INVALID_SCHEMA})
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


class ReturnAdvanceDetailSerializer(serializers.ModelSerializer):
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
            'status',
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
    advance_payment = serializers.UUIDField(required=False)
    method = serializers.IntegerField(required=False)
    money_received = serializers.BooleanField(required=False)
    cost = ReturnAdvanceCostCreateSerializer(many=True)

    class Meta:
        model = ReturnAdvance
        fields = (
            'title',
            'advance_payment',
            'method',
            'money_received',
            'cost',
            'return_total',
        )

    @classmethod
    def validate_advance_payment(cls, value):
        try:
            return AdvancePayment.objects.get(id=value)
        except AdvancePayment.DoesNotExist:
            raise serializers.ValidationError({'contact': ReturnAdvanceMsg.ADVANCE_PAYMENT_NOT_EXIST})

    def validate(self, validate_data):
        if validate_data['advance_payment'].system_status != 3:
            raise serializers.ValidationError({'detail': SaleMsg.ADVANCE_PAYMENT_NOT_FINISH})
        count_expense = AdvancePaymentCost.objects.filter(
            advance_payment=validate_data['advance_payment'],
        ).count()
        if len(validate_data['cost']) != count_expense:
            raise serializers.ValidationError({'Expense': ReturnAdvanceMsg.NOT_MAP_AP})
        return validate_data

    @classmethod
    def delete_old_cost(cls, instance):
        objs = ReturnAdvanceCost.objects.select_related('advance_payment_cost').filter(return_advance=instance)
        for item in objs:
            item.advance_payment_cost.sum_return_value -= item.return_value
            item.advance_payment_cost.save(update_fields=['sum_return_value'])
        objs.delete()
        return True

    def update(self, instance, validated_data):
        data_cost = validated_data.pop('cost')
        self.delete_old_cost(instance)
        ReturnAdvanceCreateSerializer.common_create_return_advance_cost(
            validate_data=data_cost,
            return_advance=instance
        )
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
