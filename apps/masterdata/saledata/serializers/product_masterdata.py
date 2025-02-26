from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models.product import (
    ProductType, ProductCategory, UnitOfMeasureGroup, UnitOfMeasure, ProductMeasurements
)
from apps.shared import ProductMsg


# Product Type
class ProductTypeListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = ProductType
        fields = (
            'id',
            'code',
            'title',
            'description',
            'is_default',
            'is_goods',
            'is_finished_goods',
            'is_material',
            'is_tool',
            'is_service',
        )


class ProductTypeCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = ProductType
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": ProductMsg.TITLE_NOT_NULL})

    @classmethod
    def validate_code(cls, value):
        if value:
            if ProductType.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError(ProductMsg.PRODUCT_CODE_EXIST)
            return value
        raise serializers.ValidationError({"code": ProductMsg.CODE_NOT_NULL})


class ProductTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('id', 'code', 'title', 'description', 'is_default')


class ProductTypeUpdateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = ProductType
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": ProductMsg.TITLE_NOT_NULL})

    def validate_code(self, value):
        if ProductType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(ProductMsg.PRODUCT_CODE_EXIST)
        return value

# Product Category
class ProductCategoryListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductCategory
        fields = ('id', 'code', 'title', 'description')


class ProductCategoryCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = ProductCategory
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": ProductMsg.TITLE_NOT_NULL})

    @classmethod
    def validate_code(cls, value):
        if value:
            if ProductCategory.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError(ProductMsg.PRODUCT_CODE_EXIST)
            return value
        raise serializers.ValidationError({"code": ProductMsg.CODE_NOT_NULL})


class ProductCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'code', 'title', 'description')


class ProductCategoryUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=100)
    code = serializers.CharField(max_length=100)
    class Meta:
        model = ProductCategory
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": ProductMsg.TITLE_NOT_NULL})

    def validate_code(self, value):
        if ProductCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(ProductMsg.PRODUCT_CODE_EXIST)
        return value


# Unit Of Measure Group
class UnitOfMeasureGroupListSerializer(serializers.ModelSerializer):
    uom = serializers.SerializerMethodField()
    referenced_unit = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('id', 'code', 'title', 'is_default', 'referenced_unit', 'uom')

    @classmethod
    def get_referenced_unit(cls, obj):
        return {
            'id': obj.uom_reference_id,
            'code': obj.uom_reference.code,
            'title': obj.uom_reference.title
        } if obj.uom_reference else {}

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
    title = serializers.CharField(max_length=100)

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('title', 'code')

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": ProductMsg.TITLE_NOT_NULL})

    @classmethod
    def validate_code(cls, value):
        if value:
            if UnitOfMeasureGroup.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_CODE_EXIST)
            return value
        raise serializers.ValidationError({"code": ProductMsg.CODE_NOT_NULL})


class UnitOfMeasureGroupDetailSerializer(serializers.ModelSerializer):
    uom = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('id', 'code', 'title', 'uom')

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
    title = serializers.CharField(max_length=100)
    uom_reference = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('title', 'code', 'uom_reference')

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": ProductMsg.TITLE_NOT_NULL})

    def validate_code(self, value):
        if UnitOfMeasureGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_CODE_EXIST)
        return value

    @classmethod
    def validate_uom_reference(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({"uom_reference": ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})
        return None

    def validate(self, validate_data):
        if self.instance.is_default:
            raise serializers.ValidationError({'is_default': _('Can not update default data')})
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        instance.unitofmeasure_group.all().update(is_referenced_unit=False)
        if instance.uom_reference:
            instance.uom_reference.is_referenced_unit = True
            instance.uom_reference.ratio = 1
            instance.uom_reference.save(update_fields=['is_referenced_unit', 'ratio'])
        return instance


# Unit Of Measure
class UnitOfMeasureListSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = ('id', 'code', 'title', 'group', 'ratio', 'is_default')

    @classmethod
    def get_group(cls, obj):
        return {
            'id': obj.group_id,
            'title': obj.group.title,
            'is_referenced_unit': obj.is_referenced_unit
        } if obj.group else {}


class UnitOfMeasureCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    class Meta:
        model = UnitOfMeasure
        fields = ('code', 'title', 'group', 'ratio', 'rounding', 'is_referenced_unit')

    @classmethod
    def validate_code(cls, value):
        if value:
            if UnitOfMeasure.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_CODE_EXIST)
            return value
        raise serializers.ValidationError({"code": ProductMsg.CODE_NOT_NULL})

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": ProductMsg.TITLE_NOT_NULL})

    @classmethod
    def validate_group(cls, value):
        if value:
            return value
        raise serializers.ValidationError({'group': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_NULL})

    @classmethod
    def validate_ratio(cls, attrs):
        if attrs is not None and attrs > 0:
            return attrs
        raise serializers.ValidationError(ProductMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)

    def validate(self, validate_data):
        if validate_data['group'].code == 'Import':
            raise serializers.ValidationError({'group': ProductMsg.CAN_NOT_CREATE_UOM_FOR_IMPORT_GROUP})

        has_referenced_unit = UnitOfMeasure.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            group=validate_data['group'],
            is_referenced_unit=True
        ).exists()
        if has_referenced_unit and validate_data.get('is_referenced_unit', None):
            raise serializers.ValidationError({'is_referenced_unit': ProductMsg.UNIT_OF_MEASURE_GROUP_HAD_REFERENCE})
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
        return {
            'id': obj.group_id,
            'title': obj.group.title,
            'is_referenced_unit': obj.is_referenced_unit,
            'referenced_unit_title': obj.group.uom_reference.title if obj.group.uom_reference else '',
        } if obj.group else {}

    @classmethod
    def get_ratio(cls, obj):
        return round(obj.ratio, int(obj.rounding))


class UnitOfMeasureUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    class Meta:
        model = UnitOfMeasure
        fields = ('code', 'title', 'group', 'ratio', 'rounding')

    def validate_code(self, value):
        if UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_CODE_EXIST)
        return value

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": ProductMsg.TITLE_NOT_NULL})

    @classmethod
    def validate_group(cls, value):
        if value:
            return value
        raise serializers.ValidationError({'group': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_NULL})

    @classmethod
    def validate_ratio(cls, attrs):
        if attrs is not None and attrs > 0:
            return attrs
        raise serializers.ValidationError(ProductMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)

    def validate(self, validate_data):
        if self.instance.is_default:
            raise serializers.ValidationError({'is_default': _('Can not update default data')})
        if validate_data.get('ratio', 0) != 1 and self.instance.is_referenced_unit:
            raise serializers.ValidationError({'ratio': _('Ratio must be 1 for referenced unit')})
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
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
