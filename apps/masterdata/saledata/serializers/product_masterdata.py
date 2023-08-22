from rest_framework import serializers
from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models.product import (
    ProductType, ProductCategory, ExpenseType, UnitOfMeasureGroup, UnitOfMeasure, ProductMeasurements
)
from apps.shared import ProductMsg


# Product Type
class ProductTypeListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = ProductType
        fields = ('id', 'title', 'description', 'is_default')


class ProductTypeCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = ProductType
        fields = ('title', 'description')

    # @classmethod
    # def validate_title(cls, value):
    #     if ProductType.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError({"title": ProductMsg.PRODUCT_TYPE_EXIST})
    #     return value


class ProductTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('id', 'title', 'description', 'is_default')


class ProductTypeUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = ProductType
        fields = ('title', 'description')

    # def validate_title(self, value):
    #     if value != self.instance.title and ProductType.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError({"title": ProductMsg.PRODUCT_TYPE_EXIST})
    #     return value


# Product Category
class ProductCategoryListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductCategory
        fields = ('id', 'title', 'description')


class ProductCategoryCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = ProductCategory
        fields = ('title', 'description')

    # @classmethod
    # def validate_title(cls, value):
    #     if ProductCategory.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError({"title": ProductMsg.PRODUCT_CATEGORY_EXIST})
    #     return value


class ProductCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'title', 'description')


class ProductCategoryUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = ProductCategory
        fields = ('title', 'description')

    # def validate_title(self, value):
    #     if value != self.instance.title and ProductCategory.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError({"title": ProductMsg.PRODUCT_CATEGORY_EXIST})
    #     return value


# Expense Type
class ExpenseTypeListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ExpenseType
        fields = ('id', 'title', 'description')


class ExpenseTypeCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = ExpenseType
        fields = ('title', 'description')

    # @classmethod
    # def validate_title(cls, value):
    #     if ExpenseType.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError(ProductMsg.EXPENSE_TYPE_EXIST)
    #     return value


class ExpenseTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        fields = ('id', 'title', 'description')


class ExpenseTypeUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = ExpenseType
        fields = ('title', 'description')

    # def validate_title(self, value):
    #     if value != self.instance.title and ExpenseType.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError(ProductMsg.EXPENSE_TYPE_EXIST)
    #     return value


# Unit Of Measure Group
class UnitOfMeasureGroupListSerializer(serializers.ModelSerializer):
    uom = serializers.SerializerMethodField()
    referenced_unit = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('id', 'title', 'is_default', 'referenced_unit', 'uom')

    @classmethod
    def get_referenced_unit(cls, obj):
        uom_list = obj.unitofmeasure_group.all()
        result = {}
        for item in uom_list:
            if item.is_referenced_unit:
                result = {'id': item.id, 'title': item.title}
        return result

    @classmethod
    def get_uom(cls, obj):
        uom = obj.unitofmeasure_group.all()
        uom_list = []
        for item in uom:
            uom_list.append(
                {
                    'uom_id': item.id,
                    'uom_title': item.title,
                    'uom_code': item.code
                }
            )
        return uom_list


class UnitOfMeasureGroupCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('title',)

    # @classmethod
    # def validate_title(cls, value):
    #     if UnitOfMeasureGroup.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_EXIST)
    #     return value


class UnitOfMeasureGroupDetailSerializer(serializers.ModelSerializer):
    uom = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('id', 'title', 'uom')

    @classmethod
    def get_uom(cls, obj):
        uom = obj.unitofmeasure_group.all()
        uom_list = []
        for item in uom:
            uom_list.append(
                {
                    'uom_id': item.id,
                    'uom_title': item.title,
                    'uom_code': item.code
                }
            )
        return uom_list


class UnitOfMeasureGroupUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('title',)

    # def validate_title(self, value):
    #     if value != self.instance.title and UnitOfMeasureGroup.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_EXIST)
    #     return value


# Unit Of Measure
class UnitOfMeasureListSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = ('id', 'code', 'title', 'group', 'ratio')

    @classmethod
    def get_group(cls, obj):
        if obj.group:
            return {
                'id': obj.group_id,
                'title': obj.group.title,
                'is_referenced_unit': obj.is_referenced_unit
            }
        return {}


class UnitOfMeasureCreateSerializer(serializers.ModelSerializer):
    group = serializers.UUIDField(required=True, allow_null=False)
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)

    class Meta:
        model = UnitOfMeasure
        fields = ('code', 'title', 'group', 'ratio', 'rounding', 'is_referenced_unit')

    @classmethod
    def validate_code(cls, value):
        if UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_CODE_EXIST)
        return value

    # @classmethod
    # def validate_title(cls, value):
    #     if UnitOfMeasure.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_EXIST)
    #     return value

    @classmethod
    def validate_group(cls, attrs):
        try:
            if attrs is not None:
                return UnitOfMeasureGroup.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=attrs
                )
        except UnitOfMeasureGroup.DoesNotExist:
            raise serializers.ValidationError({'group': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST})
        return None

    @classmethod
    def validate_ratio(cls, attrs):
        if attrs is not None and attrs > 0:
            return attrs
        raise serializers.ValidationError(ProductMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)

    def validate(self, validate_data):
        has_referenced_unit = UnitOfMeasure.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            group=validate_data['group'],
            is_referenced_unit=True
        ).exists()
        if has_referenced_unit and validate_data.get('is_referenced_unit', None):
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_HAD_REFERENCE)
        return validate_data

    def create(self, validated_data):
        uom = UnitOfMeasure.objects.create(**validated_data)
        # update uom_reference of group if this uom.is_referenced_unit is True
        if uom:
            if uom.is_referenced_unit is True and uom.group:
                uom.group.uom_reference = uom
                uom.group.save(update_fields=['uom_reference'])
        return uom


class UnitOfMeasureDetailSerializer(serializers.ModelSerializer):  # noqa
    group = serializers.SerializerMethodField()
    ratio = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = ('id', 'code', 'title', 'group', 'ratio', 'rounding')

    @classmethod
    def get_group(cls, obj):
        if obj.group:
            uom = UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                group=obj.group,
                is_referenced_unit=True
            ).first()
            if uom:
                return {
                    'id': obj.group_id,
                    'title': obj.group.title,
                    'is_referenced_unit': obj.is_referenced_unit,
                    'referenced_unit_title': uom.title,
                }
        return {}

    @classmethod
    def get_ratio(cls, obj):
        return round(obj.ratio, int(obj.rounding))


class UnitOfMeasureUpdateSerializer(serializers.ModelSerializer):
    group = serializers.UUIDField(required=True, allow_null=False)
    title = serializers.CharField(max_length=150)

    class Meta:
        model = UnitOfMeasure
        fields = ('title', 'group', 'ratio', 'rounding', 'is_referenced_unit')

    @classmethod
    def validate_code(cls, value):
        if UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_CODE_EXIST)
        return value

    # def validate_title(self, value):
    #     if value != self.instance.title and UnitOfMeasure.objects.filter_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             title=value
    #     ).exists():
    #         raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_EXIST)
    #     return value

    @classmethod
    def validate_group(cls, attrs):
        try:
            if attrs is not None:
                return UnitOfMeasureGroup.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=attrs
                )
        except UnitOfMeasureGroup.DoesNotExist:
            raise serializers.ValidationError({'group': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST})
        return None

    @classmethod
    def validate_ratio(cls, attrs):
        if attrs is not None and attrs > 0:
            return attrs
        raise serializers.ValidationError(ProductMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)

    def update(self, instance, validated_data):
        is_referenced_unit = self.initial_data.get('is_referenced_unit', None)
        if is_referenced_unit:
            old_unit = UnitOfMeasure.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                group=self.initial_data.get('group', None),
                is_referenced_unit=True
            )
            old_unit.is_referenced_unit = False
            old_unit.save()

            old_ratio = instance.ratio
            for item in UnitOfMeasure.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    group=instance.group_id
            ):
                if item != instance:
                    item.ratio = item.ratio / old_ratio
                    item.save()

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # update uom_reference of group if this uom.is_referenced_unit is True
        if instance.is_referenced_unit is True and instance.group:
            instance.group.uom_reference = instance
            instance.group.save(update_fields=['uom_reference'])
        return instance


class ProductMeasurementsCreateSerializer(serializers.ModelSerializer):
    unit = serializers.UUIDField(required=True, allow_null=False)

    class Meta:
        model = ProductMeasurements
        fields = (
            'unit',
            'value',
        )

    @classmethod
    def validate_unit(cls, value):
        try:  # noqa
            if value is not None:
                unit = BaseItemUnit.objects.get(
                    id=value, title__in=['volume', 'weight']
                )
                return {
                    'id': str(unit.id),
                    'title': unit.title,
                    'measure': unit.measure
                }
        except BaseItemUnit.DoesNotExist:
            raise serializers.ValidationError({'Unit': ProductMsg.NOT_SAVE})
        return None

    @classmethod
    def validate_value(cls, value):
        if value <= 0:
            raise serializers.ValidationError({'volume or weight': ProductMsg.VALUE_GREATER_THAN_ZERO})
        return value
