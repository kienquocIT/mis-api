from rest_framework import serializers

from apps.core.base.models import City
from apps.masterdata.saledata.models.product import UnitOfMeasureGroup, UnitOfMeasure
from apps.masterdata.saledata.models.shipping import Shipping, ShippingCondition, FormularCondition, ConditionLocation


class ShippingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = (
            'id',
            'code',
            'title',
            'margin',
            'currency',
            'cost_method',
            'fixed_price',
            'is_active',
        )


class FormularConditionCreateSerializer(serializers.ModelSerializer):
    uom_group = serializers.UUIDField(required=True, allow_null=False)
    uom = serializers.UUIDField(required=True, allow_null=False)
    threshold = serializers.IntegerField(required=True, allow_null=False)
    amount_condition = serializers.FloatField(required=True, allow_null=False)
    extra_amount = serializers.FloatField(required=True, allow_null=False)

    class Meta:
        model = FormularCondition
        fields = (
            'uom_group',
            'uom',
            'comparison_operators',
            'threshold',
            'amount_condition',
            'extra_amount',
        )

    @classmethod
    def validate_uom_group(cls, value):
        try: # noqa
            if value is not None:
                uom_group = UnitOfMeasureGroup.objects.get(
                    id=value
                )
                return {'id': str(uom_group.id), 'title': uom_group.title, 'code': uom_group.code}
        except UnitOfMeasureGroup.DoesNotExist:
            raise serializers.ValidationError({'UoM Group': "UoM Group does not exists"})
        return None

    @classmethod
    def validate_uom(cls, value):
        try:  # noqa
            if value is not None:
                uom_group = UnitOfMeasure.objects.get(
                    id=value
                )
                return {'id': str(uom_group.id), 'title': uom_group.title, 'code': uom_group.code}
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'UoM': "UoM does not exists"})
        return None

    @classmethod
    def validate_threshold(cls, value):
        if value < 0:
            raise serializers.ValidationError({'quantity': 'Not < 0'})
        return value

    @classmethod
    def validate_amount_condition(cls, value):
        if value < 0:
            raise serializers.ValidationError({'price_fixed': 'Not < 0'})
        return value

    @classmethod
    def validate_extra_amount(cls, value):
        if value < 0:
            raise serializers.ValidationError({'extra_amount': 'Not < 0'})
        return value


class ShippingConditionCreateSerializer(serializers.ModelSerializer):
    location = serializers.ListField(required=True)
    formula = FormularConditionCreateSerializer(required=True, many=True)

    class Meta:
        model = ShippingCondition
        fields = (
            'location',
            'formula',
        )

    @classmethod
    def validate_location(cls, value):
        found_objects = City.objects.filter(id__in=value)
        if len(found_objects) != len(value):
            raise serializers.ValidationError({'location': "appears location does not exist"})
        return value


class ShippingCreateSerializer(serializers.ModelSerializer):
    cost_method = serializers.IntegerField(required=True, allow_null=False)
    fixed_price = serializers.FloatField(required=False)
    formula_condition = ShippingConditionCreateSerializer(required=False, many=True)

    class Meta:
        model = Shipping
        fields = (
            'code',
            'title',
            'margin',
            'currency',
            'cost_method',
            'fixed_price',
            'formula_condition',
        )

    def validate(self, validate_data):
        if validate_data['cost_method'] == 0:
            if 'fixed_price' not in validate_data:
                raise serializers.ValidationError("Amount is required")
        if validate_data['cost_method'] == 1:
            if 'formula_condition' not in validate_data:
                raise serializers.ValidationError("Not yet condition")
            else:
                if len(validate_data['formula_condition']) == 0:
                    raise serializers.ValidationError({'condition': "Condition can't not null or blank"})
        return validate_data

    def create(self, validated_data):

        shipping = Shipping.objects.create(**validated_data)
        self.common_create_shipping_condition(validate_data=validated_data, shipping=shipping)
        return shipping

    @classmethod
    def common_create_shipping_condition(cls, validate_data, shipping):
        data_condition = validate_data['formula_condition']
        bulk_data = []
        for condition in data_condition:
            data = {
                'formular': condition['formula'],
                'shipping': shipping,
            }
            shipping_condition = ShippingCondition.objects.create(**data)
            for location in condition['location']:
                ConditionLocation.objects.create(condition=shipping_condition, location_id=location)
            data_formula = condition['formula']
            for formula in data_formula:
                data = {
                    'condition': shipping_condition,
                    'uom_group_id': formula['uom_group']['id'],
                    'uom_id': formula['uom']['id'],
                    'comparison_operators': formula['comparison_operators'],
                    'threshold': formula['threshold'],
                    'amount_condition': formula['amount_condition'],
                    'extra_amount': formula['extra_amount'],
                }
                bulk_data.append(FormularCondition(**data))
            FormularCondition.objects.bulk_create(bulk_data)
        return True


class ShippingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = '__all__'
