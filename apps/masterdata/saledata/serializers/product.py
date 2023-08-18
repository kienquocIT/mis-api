from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models.product import (
    ProductType, ProductCategory, ExpenseType, UnitOfMeasureGroup, UnitOfMeasure, Product,
    ProductMeasurements
)
from apps.shared import ProductMsg
from .product_sub import CommonCreateUpdateProduct

PRODUCT_OPTION = [
    (0, _('Sale')),
    (1, _('Inventory')),
    (2, _('Purchase')),
]


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
    referenced_unit = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('id', 'title', 'is_default', 'referenced_unit')

    @classmethod
    def get_referenced_unit(cls, obj):
        uom_list = obj.unitofmeasure_group.all()
        result = {}
        for item in uom_list:
            if item.is_referenced_unit:
                result = {'id': item.id, 'title': item.title}
        return result


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


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'general_information',
            'sale_information',
            'product_choice'
        )


class ProductCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)
    product_choice = serializers.ListField(
        child=serializers.ChoiceField(choices=PRODUCT_OPTION),
    )

    product_type = serializers.UUIDField(required=True)
    product_category = serializers.UUIDField(required=True)
    uom_group = serializers.UUIDField(required=True)

    measure = ProductMeasurementsCreateSerializer(required=False, many=True)
    default_uom = serializers.UUIDField(required=False)
    tax_code = serializers.UUIDField(required=False)
    currency_using = serializers.UUIDField(required=False)
    inventory_uom = serializers.UUIDField(required=False)
    price_list = serializers.ListField(required=False)

    class Meta:
        model = Product
        fields = (
            'code',
            'title',
            'product_choice',

            'product_type',
            'product_category',
            'uom_group',

            'default_uom',
            'tax_code',
            'currency_using',
            'length',
            'height',
            'width',
            'measure',
            'price_list',

            'inventory_uom',
            'inventory_level_max',
            'inventory_level_min',
        )

    @classmethod
    def validate_code(cls, value):
        if Product.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.CODE_EXIST)
        return value

    # For general
    @classmethod
    def validate_product_type(cls, value):
        return CommonCreateUpdateProduct.validate_product_type(value)

    @classmethod
    def validate_product_category(cls, value):
        return CommonCreateUpdateProduct.validate_product_category(value)

    @classmethod
    def validate_uom_group(cls, value):
        return CommonCreateUpdateProduct.validate_uom_group(value)

    # For Sale
    @classmethod
    def validate_default_uom(cls, value):
        return CommonCreateUpdateProduct.validate_default_uom(value)

    @classmethod
    def validate_tax_code(cls, value):
        return CommonCreateUpdateProduct.validate_tax_code(value)

    @classmethod
    def validate_currency_using(cls, value):
        return CommonCreateUpdateProduct.validate_currency_using(value)

    @classmethod
    def validate_length(cls, value):
        return CommonCreateUpdateProduct.validate_length(value)

    @classmethod
    def validate_width(cls, value):
        return CommonCreateUpdateProduct.validate_width(value)

    @classmethod
    def validate_height(cls, value):
        return CommonCreateUpdateProduct.validate_height(value)

    # For inventory
    @classmethod
    def validate_inventory_uom(cls, value):
        return CommonCreateUpdateProduct.validate_inventory_uom(value)

    @classmethod
    def validate_inventory_level_min(cls, value):
        return CommonCreateUpdateProduct.validate_inventory_level_min(value)

    @classmethod
    def validate_inventory_level_max(cls, value):
        return CommonCreateUpdateProduct.validate_inventory_level_max(value)

    def validate(self, validated_data):
        inventory_level_min = validated_data.get('inventory_level_min', None)  # noqa
        inventory_level_max = validated_data.get('inventory_level_max', None)
        if inventory_level_min and inventory_level_max:
            if validated_data['inventory_level_min'] > validated_data['inventory_level_max']:
                raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)

        validated_data['general_information'] = CommonCreateUpdateProduct.validate_general_information(validated_data)
        validated_data['sale_information'] = CommonCreateUpdateProduct.validate_sale_information(
            validated_data
        ) if 0 in validated_data['product_choice'] else {}

        validated_data['inventory_information'] = CommonCreateUpdateProduct.validate_inventory_information(
            validated_data
        ) if 1 in validated_data['product_choice'] else {}
        return validated_data

    def create(self, validated_data):
        price_list_information = validated_data.pop('price_list') if 'price_list' in validated_data else None
        measure_data = validated_data.pop('measure') if 'measure' in validated_data else None
        product = Product.objects.create(**validated_data)
        if 0 in validated_data['product_choice']:
            CommonCreateUpdateProduct.create_price_list(product, price_list_information, validated_data)
            if 1 in validated_data['product_choice']:
                CommonCreateUpdateProduct.create_measure(product, measure_data)
        return product


class ProductDetailSerializer(serializers.ModelSerializer):
    sale_information = serializers.SerializerMethodField()  # noqa

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'general_information',
            'inventory_information',
            'sale_information',
            'purchase_information',
            'product_choice',
        )

    @classmethod
    def get_sale_information(cls, obj):
        product_price_list = obj.product_price_product.all()
        price_list_detail = []
        for item in product_price_list:
            if item.uom_using_id == obj.default_uom_id:
                price_list_detail.append(
                    {
                        'id': item.price_list_id,
                        'price': item.price,
                        'currency_using': item.currency_using.abbreviation,
                        'is_primary': item.currency_using.is_primary,
                        'title': item.price_list.title,
                        'is_auto_update': item.get_price_from_source
                    }
                )
        if len(price_list_detail) > 0:
            obj.sale_information['price_list'] = price_list_detail
        return obj.sale_information


class ProductUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150, required=False)
    product_choice = serializers.ListField(
        child=serializers.ChoiceField(choices=PRODUCT_OPTION),
        required=False
    )

    product_type = serializers.UUIDField(required=False)
    product_category = serializers.UUIDField(required=False)
    uom_group = serializers.UUIDField(required=False)

    measure = ProductMeasurementsCreateSerializer(required=False, many=True)
    default_uom = serializers.UUIDField(required=False)
    tax_code = serializers.UUIDField(required=False)
    currency_using = serializers.UUIDField(required=False)
    inventory_uom = serializers.UUIDField(required=False)
    price_list = serializers.ListField(required=False)

    class Meta:
        model = Product
        fields = (
            'title',
            'product_choice',

            'product_type',
            'product_category',
            'uom_group',

            'default_uom',
            'tax_code',
            'currency_using',
            'length',
            'height',
            'width',
            'measure',
            'price_list',

            'inventory_uom',
            'inventory_level_max',
            'inventory_level_min',
        )

    @classmethod
    def validate_code(cls, value):
        if Product.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.CODE_EXIST)
        return value

    # For general
    @classmethod
    def validate_product_type(cls, value):
        return CommonCreateUpdateProduct.validate_product_type(value)

    @classmethod
    def validate_product_category(cls, value):
        return CommonCreateUpdateProduct.validate_product_category(value)

    @classmethod
    def validate_uom_group(cls, value):
        return CommonCreateUpdateProduct.validate_uom_group(value)

    # For Sale
    @classmethod
    def validate_default_uom(cls, value):
        return CommonCreateUpdateProduct.validate_default_uom(value)

    @classmethod
    def validate_tax_code(cls, value):
        return CommonCreateUpdateProduct.validate_tax_code(value)

    @classmethod
    def validate_currency_using(cls, value):
        return CommonCreateUpdateProduct.validate_currency_using(value)

    @classmethod
    def validate_length(cls, value):
        return CommonCreateUpdateProduct.validate_length(value)

    @classmethod
    def validate_width(cls, value):
        return CommonCreateUpdateProduct.validate_width(value)

    @classmethod
    def validate_height(cls, value):
        return CommonCreateUpdateProduct.validate_height(value)

    # For inventory
    @classmethod
    def validate_inventory_uom(cls, value):
        return CommonCreateUpdateProduct.validate_inventory_uom(value)

    @classmethod
    def validate_inventory_level_min(cls, value):
        return CommonCreateUpdateProduct.validate_inventory_level_min(value)

    @classmethod
    def validate_inventory_level_max(cls, value):
        return CommonCreateUpdateProduct.validate_inventory_level_max(value)

    def validate(self, validated_data):
        inventory_level_min = validated_data.get('inventory_level_min', None)  # noqa
        inventory_level_max = validated_data.get('inventory_level_max', None)
        if inventory_level_min and inventory_level_max:
            if validated_data['inventory_level_min'] > validated_data['inventory_level_max']:
                raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)

        validated_data['general_information'] = CommonCreateUpdateProduct.validate_general_information(validated_data)
        validated_data['sale_information'] = CommonCreateUpdateProduct.validate_sale_information(
            validated_data
        ) if 0 in validated_data['product_choice'] else {}

        validated_data['inventory_information'] = CommonCreateUpdateProduct.validate_inventory_information(
            validated_data
        ) if 1 in validated_data['product_choice'] else {}
        return validated_data

    def update(self, instance, validated_data):
        price_list_information = validated_data.pop('price_list') if 'price_list' in validated_data else None
        measure_data = validated_data.pop('measure') if 'measure' in validated_data else None

        instance.product_measure.all().delete()
        CommonCreateUpdateProduct.delete_price_list(instance)

        if 0 in validated_data['product_choice']:
            CommonCreateUpdateProduct.update_price_list(instance, price_list_information, validated_data)
            if 1 in validated_data['product_choice']:
                CommonCreateUpdateProduct.create_measure(instance, measure_data)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance


class ProductForSaleListSerializer(serializers.ModelSerializer):
    price_list = serializers.SerializerMethodField()
    product_choice = serializers.JSONField()
    sale_information = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'general_information',
            'sale_information',
            'price_list',
            'product_choice',
        )

    @classmethod
    def check_status_price(cls, valid_time_start, valid_time_end):
        current_time = timezone.now()
        if (not valid_time_start >= current_time) and (valid_time_end >= current_time):
            return 'Valid'
        if valid_time_end < current_time:
            return 'Expired'
        if valid_time_start >= current_time:
            return 'Invalid'
        return 'Undefined'

    @classmethod
    def get_price_list(cls, obj):
        return [
            {
                'id': price.price_list_id,
                'title': price.price_list.title,
                'value': price.price,
                'is_default': price.price_list.is_default,
                'price_status': cls.check_status_price(
                    price.price_list.valid_time_start,
                    price.price_list.valid_time_end
                ),
                'price_type': price.price_list.price_list_type,
            }
            for price in obj.product_price_product.all()
        ]

    @classmethod
    def get_sale_information(cls, obj):
        return {
            'default_uom': {
                'id': obj.default_uom_id,
                'title': obj.default_uom.title,
                'code': obj.default_uom.code
            } if obj.default_uom else {},
            'tax_code': {
                'id': obj.tax_code_id,
                'title': obj.tax_code.title,
                'code': obj.tax_code.code,
                'rate': obj.tax_code.rate
            } if obj.tax_code else {},
            'currency_using': {
                'id': obj.currency_using_id,
                'title': obj.currency_using.title,
                'code': obj.currency_using.code,
            } if obj.currency_using else {},
            'length': obj.length,
            'width': obj.width,
            'height': obj.height,
        }


class UnitOfMeasureOfGroupLaborListSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = (
            'id',
            'title',
            'code',
            'group',
            'ratio',
        )

    @classmethod
    def get_group(cls, obj):
        if obj.group:
            return {
                'id': obj.group_id,
                'title': obj.group.title,
                'is_referenced_unit': obj.is_referenced_unit
            }
        return {}
