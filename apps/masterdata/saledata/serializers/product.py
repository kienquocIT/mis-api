from rest_framework import serializers

from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models.product import (
    ProductType, ProductCategory, ExpenseType, UnitOfMeasureGroup, UnitOfMeasure, Product,
    ProductGeneral, ProductSale, ProductInventory, ProductMeasurements
)
from apps.masterdata.saledata.models.price import ProductPriceList, Tax, Currency
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

    @classmethod
    def validate_title(cls, value):
        if ProductType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError({"title": ProductMsg.PRODUCT_TYPE_EXIST})
        return value


class ProductTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('id', 'title', 'description', 'is_default')


class ProductTypeUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = ProductType
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and ProductType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError({"title": ProductMsg.PRODUCT_TYPE_EXIST})
        return value


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

    @classmethod
    def validate_title(cls, value):
        if ProductCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError({"title": ProductMsg.PRODUCT_CATEGORY_EXIST})
        return value


class ProductCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'title', 'description')


class ProductCategoryUpdateSerializer(serializers.ModelSerializer): # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = ProductCategory
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and ProductCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError({"title": ProductMsg.PRODUCT_CATEGORY_EXIST})
        return value


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

    @classmethod
    def validate_title(cls, value):
        if ExpenseType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.EXPENSE_TYPE_EXIST)
        return value


class ExpenseTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        fields = ('id', 'title', 'description')


class ExpenseTypeUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = ExpenseType
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and ExpenseType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.EXPENSE_TYPE_EXIST)
        return value


# Unit Of Measure Group
class UnitOfMeasureGroupListSerializer(serializers.ModelSerializer):
    referenced_unit = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('id', 'title', 'referenced_unit')

    @classmethod
    def get_referenced_unit(cls, obj):
        uom_obj = UnitOfMeasure.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            group=obj,
            is_referenced_unit=True
        ).first()

        if uom_obj:
            return {'id': uom_obj.id, 'title': uom_obj.title}
        return {}


class UnitOfMeasureGroupCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('title',)

    @classmethod
    def validate_title(cls, value):
        if UnitOfMeasureGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_EXIST)
        return value


class UnitOfMeasureGroupDetailSerializer(serializers.ModelSerializer):
    uom = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasureGroup
        fields = ('id', 'title', 'uom')

    @classmethod
    def get_uom(cls, obj):
        uom = UnitOfMeasure.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            group=obj,
        )
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

    def validate_title(self, value):
        if value != self.instance.title and UnitOfMeasureGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value
        ).exists():
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_EXIST)
        return value


# Unit Of Measure
class UnitOfMeasureListSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = ('id', 'code', 'title', 'group')

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

    @classmethod
    def validate_title(cls, value):
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

    def validate_title(self, value):
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


# Product
class ProductGeneralInformationCreateSerializer(serializers.ModelSerializer):
    product_type = serializers.JSONField(required=True)
    product_category = serializers.JSONField(required=True)
    uom_group = serializers.JSONField(required=True)

    class Meta:
        model = ProductGeneral
        fields = ('product_type', 'product_category', 'uom_group',)

    @classmethod
    def validate_product_type(cls, value):
        if value:
            product_type = ProductType.objects.filter(id=value).first()
            if product_type:
                return {'id': str(product_type.id), 'title': product_type.title, 'code': product_type.code}
        raise serializers.ValidationError(ProductMsg.PRODUCT_TYPE_DOES_NOT_EXIST)

    @classmethod
    def validate_product_category(cls, value):
        if value:
            product_category = ProductCategory.objects.filter(id=value).first()
            if product_category:
                return {'id': str(product_category.id), 'title': product_category.title, 'code': product_category.code}
        raise serializers.ValidationError(ProductMsg.PRODUCT_CATEGORY_DOES_NOT_EXIST)

    @classmethod
    def validate_uom_group(cls, value):
        if value:
            uom_group = UnitOfMeasureGroup.objects.filter(id=value).first()
            if uom_group:
                return {'id': str(uom_group.id), 'title': uom_group.title, 'code': uom_group.code}
        raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST)


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


class ProductSaleInformationCreateSerializer(serializers.ModelSerializer):
    default_uom = serializers.JSONField(required=True)
    tax_code = serializers.JSONField(required=True)
    currency_using = serializers.JSONField(required=True)
    length = serializers.FloatField(required=False, allow_null=True)
    width = serializers.FloatField(required=False, allow_null=True)
    height = serializers.FloatField(required=False, allow_null=True)
    measure = ProductMeasurementsCreateSerializer(required=True, many=True)

    class Meta:
        model = ProductSale
        fields = (
            'default_uom',
            'tax_code',
            'currency_using',
            'length',
            'width',
            'height',
            'measure',
        )

    @classmethod
    def validate_default_uom(cls, value):
        if value:
            default_uom = UnitOfMeasure.objects.filter(id=value).first()
            if default_uom:
                return {'id': str(default_uom.id), 'title': default_uom.title, 'code': default_uom.code}
        raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_NOT_EXIST)

    @classmethod
    def validate_tax_code(cls, value):
        if value:
            tax_code = Tax.objects.filter(id=value).first()
            if tax_code:
                return {'id': str(tax_code.id), 'title': tax_code.title, 'code': tax_code.code, 'rate': tax_code.rate}
        raise serializers.ValidationError(ProductMsg.TAX_DOES_NOT_EXIST)

    @classmethod
    def validate_currency_using(cls, value):
        if value:
            currency_using = Currency.objects.filter(id=value).first()
            if currency_using:
                return {
                    'id': str(currency_using.id),
                    'title': currency_using.title,
                    'code': currency_using.code,
                    'abbreviation': currency_using.abbreviation
                }
        raise serializers.ValidationError(ProductMsg.CURRENCY_DOES_NOT_EXIST)

    @classmethod
    def validate_length(cls, value):
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError({'length': ProductMsg.VALUE_GREATER_THAN_ZERO})
            return value
        return None

    @classmethod
    def validate_width(cls, value):
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError({'width': ProductMsg.VALUE_GREATER_THAN_ZERO})
            return value
        return None

    @classmethod
    def validate_height(cls, value):
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError({'height': ProductMsg.VALUE_GREATER_THAN_ZERO})
            return value
        return None


class ProductInventoryInformationCreateSerializer(serializers.ModelSerializer):
    uom = serializers.JSONField(required=True)

    class Meta:
        model = ProductInventory
        fields = ('uom', 'inventory_level_min', 'inventory_level_max',)

    @classmethod
    def validate_uom(cls, value):
        if value:
            uom = UnitOfMeasure.objects.filter(id=value).first()
            if uom:
                return {'id': str(uom.id), 'title': uom.title, 'code': uom.code}
        raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_NOT_EXIST)

    @classmethod
    def validate_inventory_level_min(cls, value):
        if value:
            if value <= 0:
                raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)
            return value
        return None

    @classmethod
    def validate_inventory_level_max(cls, value):
        if value:
            if value <= 0:
                raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)
            return value
        return None

    def validate(self, validated_data):
        inventory_level_min = validated_data.get('inventory_level_min', None)
        inventory_level_max = validated_data.get('inventory_level_max', None)
        if inventory_level_min and inventory_level_max:
            if validated_data['inventory_level_min'] > validated_data['inventory_level_max']:
                raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)
        return validated_data


def common_create_update_product(validated_data, instance):
    if 'general_information' in validated_data:
        ProductGeneral.objects.create(
            product=instance,
            product_type_id=validated_data['general_information'].get('product_type', {}).get('id', None),
            product_category_id=validated_data['general_information'].get('product_category', {}).get('id', None),
            uom_group_id=validated_data['general_information'].get('uom_group', {}).get('id', None)
        )
    else:
        raise serializers.ValidationError(ProductMsg.SALE_INFORMATION_MISSING)

    if 'sale_information' in validated_data:
        ProductSale.objects.create(
            product=instance,
            default_uom_id=validated_data['sale_information'].get('default_uom', {}).get('id', None),
            tax_code_id=validated_data['sale_information'].get('tax_code', {}).get('id', None),
            currency_using_id=validated_data['sale_information'].get('currency_using', {}).get('id', None),
            length=validated_data['sale_information']['length'],
            width=validated_data['sale_information']['width'],
            height=validated_data['sale_information']['height'],
        )
        data_bulk = [ProductMeasurements(
            product=instance,
            measure_id=item['unit']['id'],
            value=item['value']
        ) for item in validated_data['sale_information']['measure']]

        ProductMeasurements.objects.bulk_create(data_bulk)
    else:
        instance.sale_information = {}

    if 'inventory_information' in validated_data:
        ProductInventory.objects.create(
            product=instance,
            uom_id=validated_data['inventory_information'].get('uom', {}).get('id', None),
            inventory_level_min=validated_data['inventory_information'].get('inventory_level_min', None),
            inventory_level_max=validated_data['inventory_information'].get('inventory_level_max', None)
        )
    else:
        instance.inventory_information = {}

    instance.save()
    return True


def common_delete_product_information(instance):
    instance.product_general.all().delete()
    instance.product_sale.all().delete()
    instance.product_inventory.all().delete()
    instance.product_measure.all().delete()
    return True


class ProductListSerializer(serializers.ModelSerializer):
    price_list = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'general_information',
            'sale_information',
            'price_list'
        )

    @classmethod
    def get_price_list(cls, obj):
        price_list = obj.product_price_product.all().values_list('price_list__title', 'price')
        if price_list:
            return [
                {'title': price[0], 'value': price[1]}
                for price in price_list
            ]
        return []


class ProductCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)
    general_information = ProductGeneralInformationCreateSerializer(required=False)
    inventory_information = ProductInventoryInformationCreateSerializer(required=False)
    sale_information = ProductSaleInformationCreateSerializer(required=False)

    class Meta:
        model = Product
        fields = (
            'code',
            'title',
            'general_information',
            'inventory_information',
            'sale_information',
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

    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
        common_create_update_product(validated_data=validated_data, instance=product)

        price_list_information = self.initial_data.get('price_list', None)

        if price_list_information:
            objs = []
            for item in price_list_information:
                get_price_from_source = False
                if item.get('is_auto_update', None) == '1':
                    get_price_from_source = True
                objs.append(
                    ProductPriceList(
                        price_list_id=item.get('price_list_id', None),
                        product=product,
                        price=float(item.get('price_value', None)),
                        currency_using_id=validated_data['sale_information'].get('currency_using', {}).get('id', None),
                        uom_using_id=validated_data['sale_information'].get('default_uom', {}).get('id', None),
                        uom_group_using_id=validated_data['general_information'].get('uom_group', {}).get('id', None),
                        get_price_from_source=get_price_from_source
                    )
                )
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)
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
        )

    @classmethod
    def get_sale_information(cls, obj):
        product_price_list = obj.product_price_product.all()
        price_list_detail = []
        for item in product_price_list:
            price_list_detail.append(
                {
                    'id': item.price_list_id,
                    'price': item.price,
                    'currency_using': item.currency_using.abbreviation,
                    'is_auto_update': item.get_price_from_source
                }
            )
        if len(price_list_detail) > 0:
            obj.sale_information['price_list'] = price_list_detail
        return obj.sale_information


class ProductUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)
    general_information = ProductGeneralInformationCreateSerializer(required=False)
    inventory_information = ProductInventoryInformationCreateSerializer(required=False)
    sale_information = ProductSaleInformationCreateSerializer(required=False)

    class Meta:
        model = Product
        fields = (
            'title',
            'general_information',
            'inventory_information',
            'sale_information',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        common_delete_product_information(instance=instance)
        common_create_update_product(validated_data=validated_data, instance=instance)

        price_list_information = self.initial_data.get('price_list', None)
        if price_list_information:
            objs = []
            for item in price_list_information:
                get_price_from_source = False
                if item.get('is_auto_update', None) == '1':
                    get_price_from_source = True

                product_price_list_item = ProductPriceList.objects.filter(
                    product=instance,
                    price_list_id=item.get('price_list_id', None),
                    currency_using_id=validated_data['sale_information'].get('currency_using', {}).get('id', None),
                ).first()
                if product_price_list_item:
                    product_price_list_item.delete()
                    currency_using_id = validated_data['sale_information'].get('currency_using', {}).get('id', None)
                    default_uom_id = validated_data['sale_information'].get('default_uom', {}).get('id', None)
                    uom_group_id = validated_data['general_information'].get('uom_group', {}).get('id', None)
                    objs.append(
                        ProductPriceList(
                            price_list_id=item.get('price_list_id', None),
                            product=instance,
                            price=float(item.get('price_value', None)),
                            currency_using_id=currency_using_id,
                            uom_using_id=default_uom_id,
                            uom_group_using_id=uom_group_id,
                            get_price_from_source=get_price_from_source
                        )
                    )
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)
        return instance
