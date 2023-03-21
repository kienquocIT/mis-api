import string
from rest_framework import serializers
from apps.sale.saledata.models.product import (
    ProductType, ProductCategory, ExpenseType, UnitOfMeasureGroup, UnitOfMeasure,
)
from apps.shared.translations.product import ProductMsg


# Product Type
class ProductTypeListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductType
        fields = ('id', 'title', 'description')


class ProductTypeCreateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductType
        fields = ('title', 'description')

    @classmethod
    def validate_title(cls, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if ProductType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value.title()
        ).exists():
            raise serializers.ValidationError(ProductMsg.PRODUCT_TYPE_EXIST)
        return value


class ProductTypeDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductType
        fields = ('id', 'title', 'description')


class ProductTypeUpdateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductType
        fields = ('title', 'description')

    def validate_title(self, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if value != self.instance.title and ProductType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.PRODUCT_TYPE_EXIST)
        return value


# Product Category
class ProductCategoryListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductCategory
        fields = ('id', 'title', 'description')


class ProductCategoryCreateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductCategory
        fields = ('title', 'description')

    @classmethod
    def validate_title(cls, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if ProductCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.PRODUCT_CATEGORY_EXIST)
        return value


class ProductCategoryDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductCategory
        fields = ('id', 'title', 'description')


class ProductCategoryUpdateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductCategory
        fields = ('title', 'description')

    def validate_title(self, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if value != self.instance.title and ProductCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.PRODUCT_CATEGORY_EXIST)
        return value


# Expense Type
class ExpenseTypeListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ExpenseType
        fields = ('id', 'title', 'description')


class ExpenseTypeCreateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ExpenseType
        fields = ('title', 'description')

    @classmethod
    def validate_title(cls, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if ExpenseType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.EXPENSE_TYPE_EXIST)
        return value


class ExpenseTypeDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ExpenseType
        fields = ('id', 'title', 'description')


class ExpenseTypeUpdateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ExpenseType
        fields = ('title', 'description')

    def validate_title(self, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if value != self.instance.title and ExpenseType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.EXPENSE_TYPE_EXIST)
        return value


# Unit Of Measure Group
class UnitOfMeasureGroupListSerializer(serializers.ModelSerializer):  # noqa
    referenced_unit = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('id', 'title', 'referenced_unit')

    @classmethod
    def get_referenced_unit(cls, obj):
        if obj.referenced_unit_id:
            return {'id': obj.referenced_unit_id, 'title': obj.referenced_unit.title}
        return {}


class UnitOfMeasureGroupCreateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('title', 'referenced_unit')

    @classmethod
    def validate_title(cls, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if UnitOfMeasureGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_EXIST)
        return value


class UnitOfMeasureGroupDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('id', 'title', 'referenced_unit')


class UnitOfMeasureGroupUpdateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('title',)

    def validate_title(self, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if value != self.instance.title and UnitOfMeasureGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_EXIST)
        return value


# Unit Of Measure
class UnitOfMeasureListSerializer(serializers.ModelSerializer):  # noqa
    group = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = ('id', 'code', 'title', 'group')

    @classmethod
    def get_group(cls, obj):
        if obj.group:
            is_referenced_unit = 0
            if obj.group.referenced_unit_id == obj.id:
                is_referenced_unit = 1
            return {
                'id': obj.group_id,
                'title': obj.group.title,
                'is_referenced_unit': is_referenced_unit
            }
        return {}


class UnitOfMeasureCreateSerializer(serializers.ModelSerializer):  # noqa
    group = serializers.UUIDField(required=True, allow_null=False)
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)

    class Meta:
        model = UnitOfMeasure
        fields = ('code', 'title', 'group', 'ratio', 'rounding')

    @classmethod
    def validate_code(cls, value):
        value = value.strip()
        if UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_CODE_EXIST)
        return value

    @classmethod
    def validate_title(cls, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_EXIST)
        return value

    @classmethod
    def validate_group(cls, attrs):
        try:
            if attrs is not None:
                return UnitOfMeasureGroup.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=attrs
                )
        except UnitOfMeasureGroup.DoesNotExist as exc:
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST) from exc
        return None

    @classmethod
    def validate_ratio(cls, attrs):
        if attrs is not None and attrs >= 0:
            return attrs
        raise serializers.ValidationError(ProductMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)

    def create(self, validated_data):
        # create UoM
        obj = UnitOfMeasure.objects.create(**validated_data)

        # update referenced_unit for group
        group = obj.group
        if not group.referenced_unit:
            group.referenced_unit = obj
            group.save()
        return obj


class UnitOfMeasureDetailSerializer(serializers.ModelSerializer):  # noqa
    group = serializers.SerializerMethodField()
    ratio = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = ('id', 'code', 'title', 'group', 'ratio', 'rounding')

    @classmethod
    def get_group(cls, obj):
        if obj.group:
            is_referenced_unit = 0
            if obj.group.referenced_unit_id == obj.id:
                is_referenced_unit = 1
            return {
                'id': obj.group_id,
                'title': obj.group.title,
                'is_referenced_unit': is_referenced_unit,
                'referenced_unit_title': obj.group.referenced_unit.title,
            }
        return {}

    @classmethod
    def get_ratio(cls, obj):
        return round(obj.ratio, int(obj.rounding))


class UnitOfMeasureUpdateSerializer(serializers.ModelSerializer):  # noqa
    group = serializers.UUIDField(required=True, allow_null=False)

    class Meta:
        model = UnitOfMeasure
        fields = ('title', 'group', 'ratio', 'rounding')

    @classmethod
    def validate_code(cls, value):
        value = value.strip()
        if UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_CODE_EXIST)
        return value

    def validate_title(self, value):
        value = value.translate(str.maketrans('', '', string.punctuation)).title().strip()
        if value != self.instance.title and UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_EXIST)
        return value

    @classmethod
    def validate_group(cls, attrs):
        try:
            if attrs is not None:
                return UnitOfMeasureGroup.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=attrs
                )
        except UnitOfMeasureGroup.DoesNotExist as exc:
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST) from exc
        return None

    @classmethod
    def validate_ratio(cls, attrs):
        if attrs is not None and attrs >= 0:
            return attrs
        raise serializers.ValidationError(ProductMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)

    def update(self, instance, validated_data):
        is_referenced_unit = self.initial_data.get('is_referenced_unit', None)
        if is_referenced_unit and is_referenced_unit == 'on':
            group = UnitOfMeasureGroup.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=self.initial_data.get('group', None)
            )
            group.referenced_unit = instance
            group.save()

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

        return instance
