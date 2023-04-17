from rest_framework import serializers
from apps.sale.saledata.models.product import (
    ProductType, ProductCategory, ExpenseType, UnitOfMeasureGroup, UnitOfMeasure, Product,
    ProductGeneral, ProductSale, ProductInventory
)
from apps.sale.saledata.models.price import ProductPriceList, Tax, Currency
from apps.shared import ProductMsg, PriceMsg


# Product Type
class ProductTypeListSerializer(serializers.ModelSerializer):  

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
            raise serializers.ValidationError(ProductMsg.PRODUCT_TYPE_EXIST)
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
            raise serializers.ValidationError(ProductMsg.PRODUCT_TYPE_EXIST)
        return value


# Product Category
class ProductCategoryListSerializer(serializers.ModelSerializer):  

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
            raise serializers.ValidationError(ProductMsg.PRODUCT_CATEGORY_EXIST)
        return value


class ProductCategoryDetailSerializer(serializers.ModelSerializer):  

    class Meta:
        model = ProductCategory
        fields = ('id', 'title', 'description')


class ProductCategoryUpdateSerializer(serializers.ModelSerializer):  
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
class ExpenseTypeListSerializer(serializers.ModelSerializer):  

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
        except UnitOfMeasureGroup.DoesNotExist as exc:
            raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST) from exc
        return None

    @classmethod
    def validate_ratio(cls, attrs):
        if attrs is not None and attrs > 0:
            return attrs
        raise serializers.ValidationError(ProductMsg.RATIO_MUST_BE_GREATER_THAN_ZERO)

    def create(self, validated_data):
        if validated_data['is_referenced_unit']:
            has_referenced_unit = UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                group=validated_data['group'],
                is_referenced_unit=True
            ).first()
            if has_referenced_unit:
                raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_HAD_REFERENCE)
        uom = UnitOfMeasure.objects.create(**validated_data)
        return uom


class UnitOfMeasureDetailSerializer(serializers.ModelSerializer):  
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
class ProductListSerializer(serializers.ModelSerializer):  

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'general_information',
        )


class ProductCreateSerializer(serializers.ModelSerializer):  
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
        if not value.get('uom_group', None):  
            raise serializers.ValidationError(ProductMsg.UOM_MISSING)

        product_type = ProductType.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value.get('product_type', None)
        ).first()

        product_category = ProductCategory.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value.get('product_category', None)
        ).first()

        uom_group = UnitOfMeasureGroup.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value.get('uom_group', None)
        ).first()

        value = {}
        if product_type:
            value['product_type'] = {'id': str(product_type.id), 'title': product_type.title, 'code': product_type.code}
        if product_category:
            value['product_category'] = {
                'id': str(product_category.id),
                'title': product_category.title,
                'code': product_category.code
            }
        if uom_group:
            value['uom_group'] = {'id': str(uom_group.id), 'title': uom_group.title, 'code': uom_group.code}

        return value

    @classmethod
    def validate_sale_information(cls, value):
        if value != {}: 
            if not value.get('default_uom', None):
                raise serializers.ValidationError(ProductMsg.DEFAULT_UOM_MISSING)

            price_list = value.get('price_list', None)
            if price_list:
                for item in price_list:
                    for key in ['price_value', 'price_list_id', 'is_auto_update']:
                        if not item.get(key, None):
                            raise serializers.ValidationError(PriceMsg.PRICE_LIST_IS_MISSING_VALUE)
                if not value.get('currency_using', None):
                    raise serializers.ValidationError(PriceMsg.CURRENCY_NOT_EXIST)

            default_uom = UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('default_uom', None)
            ).first()
            tax_code = Tax.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('tax_code', None)
            ).first()
            currency_using = Currency.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('currency_using', None)
            ).first()

            value = {}
            if default_uom:
                value['default_uom'] = {'id': str(default_uom.id), 'title': default_uom.title, 'code': default_uom.code}
            if tax_code:
                value['tax_code'] = {'id': str(tax_code.id), 'title': tax_code.title, 'code': tax_code.code}
            if currency_using:
                value['currency_using'] = {
                    'id': str(currency_using.id),
                    'title': currency_using.title,
                    'abbreviation': currency_using.abbreviation,
                    'code': currency_using.code
                }
            value['price_list'] = price_list
            return value
        return {}

    @classmethod
    def validate_inventory_information(cls, value):
        if value != {}:  
            if not value.get('uom', None):  
                raise serializers.ValidationError(ProductMsg.UOM_MISSING)
            inventory_level_min = value.get('inventory_level_min', None)
            inventory_level_max = value.get('inventory_level_max', None)
            if inventory_level_min and inventory_level_max:
                value['inventory_level_min'] = int(inventory_level_min)
                value['inventory_level_max'] = int(inventory_level_max)
                if (value['inventory_level_min'] > 0) and (value['inventory_level_max'] > 0):
                    if value['inventory_level_min'] > value['inventory_level_max']:
                        raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)
                else:
                    raise serializers.ValidationError(ProductMsg.NEGATIVE_VALUE)
            else:
                if inventory_level_min:
                    value['inventory_level_min'] = int(inventory_level_min)
                if inventory_level_max:
                    value['inventory_level_max'] = int(inventory_level_max)

            uom = UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('uom', None)
            ).first()

            value = {}
            if uom:
                value['uom'] = {'id': str(uom.id), 'title': uom.title, 'code': uom.code}
            if inventory_level_min:
                value['inventory_level_min'] = int(inventory_level_min)
            if inventory_level_max:
                value['inventory_level_max'] = int(inventory_level_max)
            return value
        return {}

    def create(self, validated_data):
        price_list_information = validated_data['sale_information'].get('price_list', None)  
        currency_using = validated_data['sale_information'].get('currency_using', None)

        if price_list_information:
            del validated_data['sale_information']['price_list']

        product = Product.objects.create(**validated_data)

        general_information = validated_data['general_information']
        if general_information:
            product_type = general_information.get('product_type', None)
            if product_type:
                product_type = product_type['id']
            product_category = general_information.get('product_category', None)
            if product_category:
                product_category = product_category['id']
            uom_group = general_information.get('uom_group', None)
            if uom_group:
                uom_group = uom_group['id']
            ProductGeneral.objects.create(
                product=product,
                product_type_id=product_type,
                product_category_id=product_category,
                uom_group_id=uom_group,
            )

        sale_information = validated_data['sale_information']
        if sale_information:
            default_uom = sale_information.get('default_uom', None)
            if default_uom:
                default_uom = default_uom['id']
            tax_code = sale_information.get('tax_code', None)
            if tax_code:
                tax_code = tax_code['id']
            ProductSale.objects.create(
                product=product,
                default_uom_id=default_uom,
                tax_code_id=tax_code,
            )

        inventory_information = validated_data['inventory_information']
        if inventory_information:
            uom = inventory_information.get('uom', None)
            if uom:
                uom = uom['id']
            inventory_level_min = inventory_information.get('inventory_level_min', None)
            inventory_level_max = inventory_information.get('inventory_level_max', None)
            ProductInventory.objects.create(
                product=product,
                uom_id=uom,
                inventory_min=inventory_level_min,
                inventory_max=inventory_level_max
            )

        if price_list_information and currency_using:  
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
                        currency_using_id=currency_using['id'],
                        uom_using_id=validated_data['sale_information']['default_uom']['id'],
                        uom_group_using_id=validated_data['general_information']['uom_group']['id'],
                        get_price_from_source=get_price_from_source
                    )
                )  # tạo các objs price_list (luôn đưa vào general_price_list)
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)
        return product


class ProductDetailSerializer(serializers.ModelSerializer):
    sale_information = serializers.SerializerMethodField()  

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
        product_price_list = ProductPriceList.objects.filter(product=obj).select_related('currency_using')
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
        if not value.get('uom_group', None):  
            raise serializers.ValidationError(ProductMsg.UOM_MISSING)

        product_type = ProductType.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value.get('product_type', None)
        ).first()

        product_category = ProductCategory.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value.get('product_category', None)
        ).first()

        uom_group = UnitOfMeasureGroup.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value.get('uom_group', None)
        ).first()

        value = {}
        if product_type:
            value['product_type'] = {'id': str(product_type.id), 'title': product_type.title, 'code': product_type.code}
        if product_category:
            value['product_category'] = {
                'id': str(product_category.id),
                'title': product_category.title,
                'code': product_category.code
            }
        if uom_group:
            value['uom_group'] = {'id': str(uom_group.id), 'title': uom_group.title, 'code': uom_group.code}

        return value

    @classmethod
    def validate_sale_information(cls, value):
        if value != {}: 
            if not value.get('default_uom', None):
                raise serializers.ValidationError(ProductMsg.DEFAULT_UOM_MISSING)

            price_list = value.get('price_list', None)
            if price_list:
                for item in price_list:
                    for key in ['price_value', 'price_list_id', 'is_auto_update']:
                        if not item.get(key, None):
                            raise serializers.ValidationError(PriceMsg.PRICE_LIST_IS_MISSING_VALUE)
                if not value.get('currency_using', None):
                    raise serializers.ValidationError(PriceMsg.CURRENCY_NOT_EXIST)

            default_uom = UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('default_uom', None)
            ).first()
            tax_code = Tax.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('tax_code', None)
            ).first()
            currency_using = Currency.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('currency_using', None)
            ).first()

            value = {}
            if default_uom:
                value['default_uom'] = {'id': str(default_uom.id), 'title': default_uom.title, 'code': default_uom.code}
            if tax_code:
                value['tax_code'] = {'id': str(tax_code.id), 'title': tax_code.title, 'code': tax_code.code}
            if currency_using:
                value['currency_using'] = {
                    'id': str(currency_using.id),
                    'title': currency_using.title,
                    'abbreviation': currency_using.abbreviation,
                    'code': currency_using.code
                }
            value['price_list'] = price_list
            return value
        return {}

    @classmethod
    def validate_inventory_information(cls, value):
        if value != {}: 
            if not value.get('uom', None):  
                raise serializers.ValidationError(ProductMsg.UOM_MISSING)
            inventory_level_min = value.get('inventory_level_min', None)
            inventory_level_max = value.get('inventory_level_max', None)
            if inventory_level_min and inventory_level_max:
                value['inventory_level_min'] = int(inventory_level_min)
                value['inventory_level_max'] = int(inventory_level_max)
                if (value['inventory_level_min'] > 0) and (value['inventory_level_max'] > 0):
                    if value['inventory_level_min'] > value['inventory_level_max']:
                        raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)
                else:
                    raise serializers.ValidationError(ProductMsg.NEGATIVE_VALUE)
            else:
                if inventory_level_min:
                    value['inventory_level_min'] = int(inventory_level_min)
                if inventory_level_max:
                    value['inventory_level_max'] = int(inventory_level_max)

            uom = UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('uom', None)
            ).first()

            value = {}
            if uom:
                value['uom'] = {'id': str(uom.id), 'title': uom.title, 'code': uom.code}
            if inventory_level_min:
                value['inventory_level_min'] = int(inventory_level_min)
            if inventory_level_max:
                value['inventory_level_max'] = int(inventory_level_max)
            return value
        return {}

    def update(self, instance, validated_data):
        price_list_information = validated_data['sale_information'].get('price_list', None)  
        currency_using = validated_data['sale_information'].get('currency_using', None)

        if price_list_information:
            del validated_data['sale_information']['price_list']

        general_information = validated_data['general_information']
        if general_information:
            product_type = general_information.get('product_type', None)
            if product_type:
                product_type = product_type['id']
            product_category = general_information.get('product_category', None)
            if product_category:
                product_category = product_category['id']
            uom_group = general_information.get('uom_group', None)
            if uom_group:
                uom_group = uom_group['id']

            product_general_old = ProductGeneral.objects.get(product=instance)
            product_general_old.product_type = product_type
            product_general_old.product_category_id = product_category
            product_general_old.uom_group_id = uom_group
            product_general_old.save()

        sale_information = validated_data['sale_information']
        if sale_information:
            default_uom = sale_information.get('default_uom', None)
            if default_uom:
                default_uom = default_uom['id']
            tax_code = sale_information.get('tax_code', None)
            if tax_code:
                tax_code = tax_code['id']

            product_sale_old = ProductSale.objects.get(product=instance)
            product_sale_old.default_uom_id = default_uom
            product_sale_old.tax_code_id = tax_code
            product_sale_old.save()

        inventory_information = validated_data['inventory_information']
        if inventory_information:
            uom = inventory_information.get('uom', None)
            if uom:
                uom = uom['id']
            inventory_level_min = inventory_information.get('inventory_level_min', None)
            inventory_level_max = inventory_information.get('inventory_level_max', None)

            product_inventory_old = ProductInventory.objects.get(product=instance)
            product_inventory_old.uom_id = uom
            product_inventory_old.inventory_min = inventory_level_min
            product_inventory_old.inventory_max = inventory_level_max
            product_inventory_old.save()

        if price_list_information and currency_using:
            for item in price_list_information:
                obj = ProductPriceList.objects.filter(
                    product=instance,
                    price_list_id=item['price_list_id'],
                    currency_using_id=currency_using['id']
                ).first()
                if obj:
                    obj.price = float(item['price_value'])
                    obj.save()
        instance.general_information = validated_data['general_information']
        instance.sale_information = validated_data['sale_information']
        instance.inventory_information = validated_data['inventory_information']
        instance.save()
        return instance


class ProductCreateInPriceListSerializer(serializers.ModelSerializer):  
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)
    general_information = serializers.JSONField(required=True)
    sale_information = serializers.JSONField(required=False)

    class Meta:
        model = Product
        fields = (
            'code',
            'title',
            'general_information',
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

    @classmethod
    def validate_general_information(cls, value):
        if not value.get('uom_group', None):
            raise serializers.ValidationError(ProductMsg.UOM_MISSING)

        product_type = ProductType.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value.get('product_type', None)
        ).first()

        product_category = ProductCategory.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value.get('product_category', None)
        ).first()

        uom_group = UnitOfMeasureGroup.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value.get('uom_group', None)
        ).first()

        value = {}
        if product_type:
            value['product_type'] = {'id': str(product_type.id), 'title': product_type.title, 'code': product_type.code}
        if product_category:
            value['product_category'] = {
                'id': str(product_category.id),
                'title': product_category.title,
                'code': product_category.code
            }
        if uom_group:
            value['uom_group'] = {'id': str(uom_group.id), 'title': uom_group.title, 'code': uom_group.code}

        return value

    @classmethod
    def validate_sale_information(cls, value):
        if value != {}: 
            if not value.get('default_uom', None):
                raise serializers.ValidationError(ProductMsg.DEFAULT_UOM_MISSING)

            price_list = value.get('price_list', None)
            if price_list:
                for item in price_list:
                    for key in ['price_value', 'price_list_id', 'is_auto_update', 'currency_using']:
                        if not item.get(key, None):
                            raise serializers.ValidationError(PriceMsg.PRICE_LIST_IS_MISSING_VALUE)

            default_uom = UnitOfMeasure.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('default_uom', None)
            ).first()
            tax_code = Tax.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('tax_code', None)
            ).first()
            currency_using = Currency.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.get('currency_using', None)
            ).first()

            value = {}
            if default_uom:
                value['default_uom'] = {'id': str(default_uom.id), 'title': default_uom.title, 'code': default_uom.code}
            if tax_code:
                value['tax_code'] = {'id': str(tax_code.id), 'title': tax_code.title, 'code': tax_code.code}
            if currency_using:
                value['currency_using'] = {
                    'id': str(currency_using.id),
                    'title': currency_using.title,
                    'abbreviation': currency_using.abbreviation,
                    'code': currency_using.code
                }
            value['price_list'] = price_list
            return value
        return {}

    def create(self, validated_data):
        price_list_information = validated_data['sale_information'].get('price_list', None)

        if price_list_information:
            del validated_data['sale_information']['price_list']

        product = Product.objects.create(**validated_data)

        general_information = validated_data['general_information']
        if general_information:
            product_type = general_information.get('product_type', None)
            if product_type:
                product_type = product_type['id']
            product_category = general_information.get('product_category', None)
            if product_category:
                product_category = product_category['id']
            uom_group = general_information.get('uom_group', None)
            if uom_group:
                uom_group = uom_group['id']
            ProductGeneral.objects.create(
                product=product,
                product_type_id=product_type,
                product_category_id=product_category,
                uom_group_id=uom_group,
            )

        sale_information = validated_data['sale_information']
        if sale_information:
            default_uom = sale_information.get('default_uom', None)
            if default_uom:
                default_uom = default_uom['id']
            tax_code = sale_information.get('tax_code', None)
            if tax_code:
                tax_code = tax_code['id']
            ProductSale.objects.create(
                product=product,
                default_uom_id=default_uom,
                tax_code_id=tax_code,
            )

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
                        currency_using_id=item.get('currency_using', None),
                        uom_using_id=validated_data['sale_information']['default_uom'],
                        uom_group_using_id=validated_data['general_information']['uom_group'],
                        get_price_from_source=get_price_from_source
                    )
                )
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)
        return product
