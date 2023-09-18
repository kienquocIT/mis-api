from rest_framework import serializers
from apps.sales.cashoutflow.models import ReturnAdvance, ReturnAdvanceCost, AdvancePaymentCost
from apps.shared import RETURN_ADVANCE_STATUS
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
        if obj.money_received:
            return "Received"
        return "Waiting"

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
            'creator',
            'beneficiary',
            'status',
            'money_received',
            'cost',
            'return_total',
        )

    def validate(self, validate_data):
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
            ap_updated = AdvancePaymentCost.objects.filter(id=data['advance_payment_cost']).first()
            ap_updated.sum_return_value = ap_updated.sum_return_value + float(data['return_value'])
            ap_updated.save()
        ReturnAdvanceCost.objects.bulk_create(data_bulk)
        return True

    def create(self, validated_data):
        data_cost = validated_data.pop('cost')
        return_advance = ReturnAdvance.objects.create(**validated_data)
        self.common_create_return_advance_cost(
            validate_data=data_cost,
            return_advance=return_advance
        )
        return return_advance


class ReturnAdvanceDetailSerializer(serializers.ModelSerializer):
    cost = serializers.SerializerMethodField()
    advance_payment = serializers.SerializerMethodField()
    beneficiary = serializers.SerializerMethodField()

    class Meta:
        model = ReturnAdvance
        fields = (
            'id',
            'code',
            'title',
            'advance_payment',
            'creator',
            'beneficiary',
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
                'title': obj.advance_payment.title
            }
        return {}

    @classmethod
    def get_beneficiary(cls, obj):
        if obj.beneficiary:
            return {
                'id': obj.beneficiary_id,
                'name': obj.beneficiary.get_full_name(),
            }
        return {}

    @classmethod
    def get_cost(cls, obj):
        costs = ReturnAdvanceCost.objects.filter(return_advance=obj).select_related('expense_type')
        list_result = []
        for cost in costs:
            list_result.append({
                'advance_payment_cost': cost.advance_payment_cost_id,
                'expense_name': cost.expense_name,
                'expense_type': {
                    'id': cost.expense_type_id,
                    'title': cost.expense_type.title,
                },
                'remain_total': cost.remain_value,
                'return_value': cost.return_value,
            })
        return list_result


class ReturnAdvanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnAdvance
        fields = (
            'money_received',
        )
