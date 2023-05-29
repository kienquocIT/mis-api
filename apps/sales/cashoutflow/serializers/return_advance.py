from rest_framework import serializers
from apps.sales.cashoutflow.models import ReturnAdvance, ReturnAdvanceCost, AdvancePaymentCost
from apps.shared.translations.return_advance import ReturnAdvanceMsg


class ReturnAdvanceListSerializer(serializers.ModelSerializer):
    advance_payment = serializers.SerializerMethodField()
    return_value = serializers.SerializerMethodField()
    money_received = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = ReturnAdvance
        fields = (
            'id',
            'code',
            'title',
            'advance_payment',
            'return_value',
            'status',
            'money_received',
            'date_created',
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
    def get_return_value(cls, obj):
        return sum(cost.return_price for cost in obj.return_advance.all())

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
    expense = serializers.UUIDField(required=True)

    class Meta:
        model = ReturnAdvanceCost
        fields = (
            'expense',
            'remain_total',
            'return_price'
        )

    @classmethod
    def validate_remain_total(cls, value):
        if value < 0:
            raise serializers.ValidationError({'remain total': ReturnAdvanceMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_return_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'input return': ReturnAdvanceMsg.GREATER_THAN_ZERO})
        return value

    def validate(self, validate_data):
        if validate_data['remain_total'] < validate_data['return_price']:
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
            'cost'
        )

    def validate(self, validate_data):
        count_expense = AdvancePaymentCost.objects.filter(
            advance_payment_id=validate_data['advance_payment'],
            expense_id__in=[item['expense'] for item in validate_data['cost']]
        ).count()
        if len(validate_data['cost']) != count_expense:
            raise serializers.ValidationError({'expense': ReturnAdvanceMsg.NOT_MAP_AP})
        return validate_data

    @classmethod
    def common_create_return_advance_cost(cls, validate_data, return_advance):
        data_bulk = [
            ReturnAdvanceCost(
                return_advance=return_advance,
                expense_id=data['expense'],
                remain_total=data['remain_total'],
                return_price=data['return_price']
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
            'cost'
        )

    @classmethod
    def get_cost(cls, obj):
        result = []
        for item in obj.return_advance.all():
            result.append(
                {
                    'expense': {'id': item.expense_id, 'code': item.expense.code, 'title': item.expense.title},
                    'expense_type': item.expense.expense.expense_type.title,
                    'remain_total': item.remain_total,
                    'return_price': item.return_price,
                }
            )
        return result
