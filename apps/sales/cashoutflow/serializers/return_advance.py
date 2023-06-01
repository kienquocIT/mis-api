from rest_framework import serializers
from apps.sales.cashoutflow.models import ReturnAdvance, ReturnAdvanceCost, AdvancePaymentCost
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
        if obj.status == 0:
            return "Approved"
        return obj.status


class ReturnAdvanceCostCreateSerializer(serializers.ModelSerializer):
    advance_payment_cost = serializers.UUIDField(required=True)

    class Meta:
        model = ReturnAdvanceCost
        fields = (
            'advance_payment_cost',
            'remain_value',
            'return_value',
        )

    @classmethod
    def validate_remain_value(cls, value):
        if value < 0:
            raise serializers.ValidationError({'remain total': ReturnAdvanceMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_return_value(cls, value):
        if value < 0:
            raise serializers.ValidationError({'input return': ReturnAdvanceMsg.GREATER_THAN_ZERO})
        return value

    def validate(self, validate_data):
        if validate_data['remain_value'] < validate_data['return_value']:
            raise serializers.ValidationError({'input return': ReturnAdvanceMsg.RETURN_GREATER_THAN_REMAIN})
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
            raise serializers.ValidationError({'expense': ReturnAdvanceMsg.NOT_MAP_AP})
        return validate_data

    @classmethod
    def common_create_return_advance_cost(cls, validate_data, return_advance):
        data_bulk = [
            ReturnAdvanceCost(
                return_advance=return_advance,
                advance_payment_cost_id=data['advance_payment_cost'],
                remain_value=data['remain_value'],
                return_value=data['return_value']
            ) for data in validate_data
        ]
        ReturnAdvanceCost.objects.bulk_create(data_bulk)
        return True

    def create(self, validated_data):
        data_cost = validated_data.pop('cost')
        shipping = ReturnAdvance.objects.create(**validated_data)
        self.common_create_return_advance_cost(
            validate_data=data_cost,
            return_advance=shipping
        )
        return shipping


class ReturnAdvanceDetailSerializer(serializers.ModelSerializer):
    cost = serializers.SerializerMethodField()

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
    def get_cost(cls, obj):
        advance_payment = obj.advance_payment
        list_return_advance = advance_payment.return_advance_payment.all()

        dict_money_returned = {}

        for item in advance_payment.advance_payment.all():
            dict_money_returned[item.id] = item.after_tax_price

        for item in list_return_advance:
            if item.status == 0:
                for cost in item.return_advance.all():
                    if cost.advance_payment_cost_id in dict_money_returned:
                        dict_money_returned[cost.advance_payment_cost_id] -= cost.return_value

        result = []
        for item in obj.return_advance.all():
            remain_total = dict_money_returned[item.advance_payment_cost_id]
            if obj.status == 0:
                remain_total = item.remain_value
            result.append(
                {
                    'expense': {
                        'id': item.advance_payment_cost.expense_id,
                        'code': item.advance_payment_cost.expense.code,
                        'title': item.advance_payment_cost.expense.title
                    },
                    'expense_type': item.advance_payment_cost.expense.expense.expense_type.title,
                    'remain_total': remain_total,
                    'return_price': item.return_value,
                }
            )
        return result
