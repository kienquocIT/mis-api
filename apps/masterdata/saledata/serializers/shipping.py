from rest_framework import serializers

from apps.core.base.models import City
from apps.masterdata.saledata.models import UnitOfMeasureGroup, UnitOfMeasure
from apps.masterdata.saledata.models import Shipping, ShippingCondition, FormulaCondition, ConditionLocation
from apps.shared.translations.shipping import ShippingMsg


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


class FormulaConditionCreateSerializer(serializers.ModelSerializer):
    uom_group = serializers.UUIDField(required=True, allow_null=False)
    uom = serializers.UUIDField(required=True, allow_null=False)
    threshold = serializers.IntegerField(required=True, allow_null=False)
    amount_condition = serializers.FloatField(required=True, allow_null=False)
    extra_amount = serializers.FloatField(required=True, allow_null=False)

    class Meta:
        model = FormulaCondition
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
        try:  # noqa
            if value is not None:
                uom_group = UnitOfMeasureGroup.objects.get(
                    id=value
                )
                return {'id': str(uom_group.id), 'title': uom_group.title, 'code': uom_group.code}
        except UnitOfMeasureGroup.DoesNotExist:
            raise serializers.ValidationError({'UoM Group': ShippingMsg.UOM_GROUP_NOT_EXIST})
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
            raise serializers.ValidationError({'UoM': ShippingMsg.UOM_NOT_EXIST})
        return None

    @classmethod
    def validate_threshold(cls, value):
        if value < 0:
            raise serializers.ValidationError({'threshold in condition': ShippingMsg.GREAT_THAN_ZERO})
        return value

    @classmethod
    def validate_amount_condition(cls, value):
        if value < 0:
            raise serializers.ValidationError({'price_fixed in condition': ShippingMsg.GREAT_THAN_ZERO})
        return value

    @classmethod
    def validate_extra_amount(cls, value):
        if value < 0:
            raise serializers.ValidationError({'extra_amount in condition': ShippingMsg.GREAT_THAN_ZERO})
        return value


class ShippingConditionCreateSerializer(serializers.ModelSerializer):
    location = serializers.ListField(required=True)
    formula = FormulaConditionCreateSerializer(required=True, many=True)

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
            raise serializers.ValidationError({'location in condition': ShippingMsg.LOCATION_NOT_EXIST})
        return value


class ShippingCreateSerializer(serializers.ModelSerializer):
    cost_method = serializers.IntegerField(required=True, allow_null=False)
    fixed_price = serializers.FloatField(required=False)
    formula_condition = ShippingConditionCreateSerializer(required=False, many=True)

    class Meta:
        model = Shipping
        fields = (
            'title',
            'margin',
            'currency',
            'cost_method',
            'fixed_price',
            'formula_condition',
        )

    @classmethod
    def validate_margin(cls, value):
        if value < 0:
            raise serializers.ValidationError({'margin': ShippingMsg.GREAT_THAN_ZERO})
        return value

    @classmethod
    def validate_fixed_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'price_fixed': ShippingMsg.GREAT_THAN_ZERO})
        return value

    def validate(self, validate_data):
        if validate_data['cost_method'] == 0: # noqa
            if 'fixed_price' not in validate_data:
                raise serializers.ValidationError({'Amount': ShippingMsg.REQUIRED_AMOUNT})
        if validate_data['cost_method'] == 1:
            if 'formula_condition' not in validate_data:
                raise serializers.ValidationError({'condition': ShippingMsg.NOT_YET_CONDITION})
            if len(validate_data['formula_condition']) == 0:
                raise serializers.ValidationError({'condition': ShippingMsg.CONDITION_NOT_NULL})
        return validate_data

    def create(self, validated_data):

        shipping = Shipping.objects.create(**validated_data)
        self.common_create_shipping_condition(validate_data=validated_data, shipping=shipping)
        return shipping

    @staticmethod
    def common_create_shipping_condition(validate_data, shipping):
        data_condition = validate_data['formula_condition']
        bulk_data = []
        for condition in data_condition:
            data = {
                'formula': condition['formula'],
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
                bulk_data.append(FormulaCondition(**data))

        FormulaCondition.objects.bulk_create(bulk_data)
        return True


class ShippingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = '__all__'


class ShippingUpdateSerializer(serializers.ModelSerializer):
    cost_method = serializers.IntegerField(required=True, allow_null=False)
    fixed_price = serializers.FloatField(required=False)
    formula_condition = ShippingConditionCreateSerializer(required=False, many=True)

    class Meta:
        model = Shipping
        fields = (
            'title',
            'margin',
            'currency',
            'cost_method',
            'fixed_price',
            'formula_condition',
        )

    @classmethod
    def validate_margin(cls, value):
        if value < 0:
            raise serializers.ValidationError({'margin': ShippingMsg.GREAT_THAN_ZERO})
        return value

    @classmethod
    def validate_fixed_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'price_fixed': ShippingMsg.GREAT_THAN_ZERO})
        return value

    def validate(self, validate_data):
        if validate_data['cost_method'] == 0: # noqa
            if 'fixed_price' not in validate_data:
                raise serializers.ValidationError({'Amount': ShippingMsg.REQUIRED_AMOUNT})
        if validate_data['cost_method'] == 1:
            if 'formula_condition' not in validate_data:
                raise serializers.ValidationError({'condition': ShippingMsg.NOT_YET_CONDITION})
            if len(validate_data['formula_condition']) == 0:
                raise serializers.ValidationError({'condition': ShippingMsg.CONDITION_NOT_NULL})
        return validate_data

    def update(self, instance, validated_data):
        is_change_condition = self.initial_data['is_change_condition']
        if is_change_condition:
            self.common_delete_condition(instance=instance)
            ShippingCreateSerializer.common_create_shipping_condition(validate_data=validated_data, shipping=instance)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    @classmethod
    def common_delete_condition(cls, instance):
        FormulaCondition.objects.filter(condition__shipping=instance).delete()
        ConditionLocation.objects.filter(condition__shipping=instance).delete()
        instance.formula_shipping_condition.all().delete()
        return True
