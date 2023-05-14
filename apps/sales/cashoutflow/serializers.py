from rest_framework import serializers
from apps.sales.cashoutflow.models import AdvancePayment
from apps.shared import AdvancePaymentMsg


class AdvancePaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancePayment
        fields = (
            'id',
            'title',
            'code',
        )


class AdvancePaymentCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AdvancePayment
        fields = (
            'title',
            'sale_code',
            'sale_code_type',
            'type',
            'supplier',
            'method',
            'creator_name',
            'beneficiary',
            'return_date',
        )

    @classmethod
    def validate_sale_code_type(cls, attrs):
        if attrs in [0, 1, 2]:
            return attrs
        raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)

    @classmethod
    def validate_type(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError(AdvancePaymentMsg.TYPE_ERROR)

    @classmethod
    def validate_method(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)

    def create(self, validated_data):
        if AdvancePayment.objects.all().count() == 0:
            new_code = 'AP.CODE.0001'
        else:
            latest_code = AdvancePayment.objects.latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1  # "AP.CODE.00034" > "00034" > 34 > 35 > "AP.CODE.00035"
            new_code = 'AP.CODE.000' + str(new_code)

        AdvancePayment.objects.create(**validated_data, code=new_code)
        return True


class AdvancePaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancePayment
        fields = (
            'id',
            'title',
            'code',
        )
