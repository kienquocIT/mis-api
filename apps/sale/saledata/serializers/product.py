from rest_framework import serializers
from apps.sale.saledata.models.product import (
    ProductType, ProductCategory, ExpenseType, UnitOfMeasureGroup, UnitOfMeasure, Product
)
from apps.sale.saledata.models.price import ProductPriceList, Price, Currency
from apps.shared import ProductMsg, PriceMsg


# Product Type
class ProductTypeListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductType
        fields = ('id', 'title', 'description', 'is_default')


class ProductTypeCreateSerializer(serializers.ModelSerializer):  # noqa
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
            raise serializers.ValidationError(ProductMsg.PRODUCT_TYPE_EXIST)
        return value


class ProductTypeDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductType
        fields = ('id', 'title', 'description', 'is_default')


class ProductTypeUpdateSerializer(serializers.ModelSerializer):  # noqa
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
            raise serializers.ValidationError(ProductMsg.PRODUCT_TYPE_EXIST)
        return value


# Product Category
class ProductCategoryListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductCategory
        fields = ('id', 'title', 'description')


class ProductCategoryCreateSerializer(serializers.ModelSerializer):  # noqa
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
            raise serializers.ValidationError(ProductMsg.PRODUCT_CATEGORY_EXIST)
        return value


class ProductCategoryDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductCategory
        fields = ('id', 'title', 'description')


class ProductCategoryUpdateSerializer(serializers.ModelSerializer):  # noqa
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
            raise serializers.ValidationError(ProductMsg.PRODUCT_CATEGORY_EXIST)
        return value


# Expense Type
class ExpenseTypeListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ExpenseType
        fields = ('id', 'title', 'description')


class ExpenseTypeCreateSerializer(serializers.ModelSerializer):  # noqa
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


class ExpenseTypeDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ExpenseType
        fields = ('id', 'title', 'description')


class ExpenseTypeUpdateSerializer(serializers.ModelSerializer):  # noqa
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
class UnitOfMeasureGroupListSerializer(serializers.ModelSerializer):  # noqa
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


class UnitOfMeasureGroupCreateSerializer(serializers.ModelSerializer):  # noqa
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


class UnitOfMeasureGroupDetailSerializer(serializers.ModelSerializer):  # noqa
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


class UnitOfMeasureGroupUpdateSerializer(serializers.ModelSerializer):  # noqa
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
class UnitOfMeasureListSerializer(serializers.ModelSerializer):  # noqa
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


class UnitOfMeasureCreateSerializer(serializers.ModelSerializer):  # noqa
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
        except UnitOfMeasureGroup.DoesNotExist as exc:
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST) from exc
        return None

    @classmethod
    def validate_ratio(cls, attrs):
        if attrs is not None and attrs > 0:
            return attrs
        raise serializers.ValidationError(ProductMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)


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


class UnitOfMeasureUpdateSerializer(serializers.ModelSerializer):  # noqa
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
        except UnitOfMeasureGroup.DoesNotExist as exc:
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST) from exc
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
class ProductListSerializer(serializers.ModelSerializer):  # noqa
    general_information = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'general_information',
            # 'inventory_information',
            # 'sale_information',
            # 'purchase_information'
        )

    @classmethod
    def get_general_information(cls, obj):
        if obj.general_information:
            product_type_id = obj.general_information.get('product_type', None)
            product_category_id = obj.general_information.get('product_category', None)

            product_type_title = ProductType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=product_type_id
            ).first()
            product_category_title = ProductCategory.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=product_category_id
            ).first()

            if product_type_title and product_category_title:
                return {
                    'uom_group': obj.general_information.get('uom_group', None),
                    'product_type': {'id': product_type_id, 'title': product_type_title.title},
                    'product_category': {'id': product_category_id, 'title': product_category_title.title}
                }
        return {}


class ProductCreateSerializer(serializers.ModelSerializer):  # noqa
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)
    general_information = serializers.JSONField(required=True)
    inventory_information = serializers.JSONField(required=False)
    sale_information = serializers.JSONField(required=False)
    purchase_information = serializers.JSONField(required=False)

    class Meta:
        model = Product
        fields = (
            'code',
            'title',
            'general_information',
            'inventory_information',
            'sale_information',
            'purchase_information'
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

    @classmethod
    def validate_general_information(cls, value):
        for key in value:
            if not value.get(key, None):
                raise serializers.ValidationError(ProductMsg.GENERAL_INFORMATION_MISSING)
        return value

    @classmethod
    def validate_inventory_information(cls, value):
        for key in value:
            if not value.get(key, None):
                raise serializers.ValidationError(ProductMsg.INVENTORY_INFORMATION_MISSING)
        return value

    @classmethod
    def validate_sale_information(cls, value):
        for key in value:
            if not value.get(key, None):
                raise serializers.ValidationError(ProductMsg.SALE_INFORMATION_MISSING)
        return value

    def create(self, validated_data):
        price_list_information = validated_data['sale_information'].get('price_list', None)
        uom_using = validated_data['sale_information'].get('default_uom', None)
        uom_group_using = validated_data['general_information'].get('uom_group', None)
        if price_list_information:
            del validated_data['sale_information']['price_list']
        product = Product.objects.create(**validated_data)

        # gán product với price list
        if price_list_information and uom_using and uom_group_using:
            objs = []
            objs_for_mapped = []
            for item in price_list_information:
                price_list_item = Price.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=item['id']
                ).first()
                currency_using_item = Currency.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=item['currency_using']
                ).first()
                uom_group_using_item = UnitOfMeasureGroup.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=uom_group_using
                ).first()
                uom_using_item = UnitOfMeasure.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=uom_using
                ).first()
                if price_list_item and currency_using_item and uom_using_item and uom_group_using_item:
                    objs.append(ProductPriceList(
                        price_list=price_list_item,
                        product=product,
                        price=float(item['price']),
                        currency_using=currency_using_item,
                        uom_using=uom_using_item,
                        uom_group_using=uom_group_using_item
                    ))
                else:
                    raise serializers.ValidationError(PriceMsg.PRICE_LIST_OR_CURRENCY_NOT_EXIST)

                # nếu có price list source -> tạo dữ liệu copy
                price_list_mapped = Price.objects.filter(
                    price_list_mapped=item['id']
                ).first()
                if price_list_mapped:
                    objs_for_mapped.append(
                        ProductPriceList(
                            price_list=price_list_mapped,
                            product=product,
                            price=float(item['price']),
                            currency_using=currency_using_item,
                            uom_using=uom_using_item,
                            uom_group_using=uom_group_using_item
                        )
                    )
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)
            if len(objs_for_mapped) > 0:
                ProductPriceList.objects.bulk_create(objs_for_mapped)
        return product


class ProductDetailSerializer(serializers.ModelSerializer):  # noqa

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


class ProductUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)
    general_information = serializers.JSONField(required=True)
    inventory_information = serializers.JSONField(required=False)
    sale_information = serializers.JSONField(required=False)
    purchase_information = serializers.JSONField(required=False)

    class Meta:
        model = Product
        fields = (
            'title',
            'general_information',
            'inventory_information',
            'sale_information',
            'purchase_information'
        )

    @classmethod
    def validate_general_information(cls, value):
        for key in value:
            if not value.get(key, None):
                raise serializers.ValidationError(ProductMsg.GENERAL_INFORMATION_MISSING)
        return value

    @classmethod
    def validate_inventory_information(cls, value):
        for key in value:
            if not value.get(key, None):
                raise serializers.ValidationError(ProductMsg.INVENTORY_INFORMATION_MISSING)
        return value

    @classmethod
    def validate_sale_information(cls, value):
        for key in value:
            if not value.get(key, None):
                raise serializers.ValidationError(ProductMsg.SALE_INFORMATION_MISSING)
        return value
