from rest_framework import serializers
from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models import (
    ProductMeasurements, ProductProductType, ProductVariantAttribute, ProductVariant
)
from apps.masterdata.saledata.models.price import ProductPriceList, Price, Currency
from apps.masterdata.saledata.models.product import (
    ProductComponent, ProductAttribute, UnitOfMeasure, ProductSpecificIdentificationSerialNumber, Product
)
from apps.masterdata.saledata.serializers import ProductCreateSerializer
from apps.shared import ProductMsg


PRODUCT_OPTION = [(0, _('Sale')), (1, _('Inventory')), (2, _('Purchase'))]


class ProductQuickCreateSerializer(serializers.ModelSerializer):
    product_choice = serializers.ListField(child=serializers.ChoiceField(choices=PRODUCT_OPTION))
    general_product_category = serializers.UUIDField()
    general_uom_group = serializers.UUIDField()
    sale_default_uom = serializers.UUIDField(required=False)
    sale_tax = serializers.UUIDField(required=False)

    class Meta:
        model = Product
        fields = (
            'code', 'title', 'product_choice',
            'general_product_category', 'general_uom_group', 'general_traceability_method',
            'sale_default_uom', 'sale_tax', 'description',
        )

    @classmethod
    def validate_code(cls, value):
        return ProductCreateSerializer.validate_code(value)

    @classmethod
    def validate_general_product_category(cls, value):
        return ProductCreateSerializer.validate_general_product_category(value)

    @classmethod
    def validate_general_uom_group(cls, value):
        return ProductCreateSerializer.validate_general_uom_group(value)

    @classmethod
    def validate_sale_default_uom(cls, value):
        return ProductCreateSerializer.validate_sale_default_uom(value)

    @classmethod
    def validate_sale_tax(cls, value):
        return ProductCreateSerializer.validate_sale_tax(value)

    def validate(self, validate_data):
        if 0 not in validate_data.get('product_choice', []):
            raise serializers.ValidationError({'sale': 'Sale is required'})
        if 1 in validate_data.get('product_choice', []):
            validate_data['inventory_uom'] = validate_data.get('sale_default_uom')
        if 2 in validate_data.get('product_choice', []):
            validate_data['purchase_default_uom'] = validate_data.get('sale_default_uom')
            validate_data['purchase_tax'] = validate_data.get('sale_tax')

        default_pr = Price.objects.filter_on_company(is_default=True).first()
        if not default_pr:
            raise serializers.ValidationError({'default_price_list': ProductMsg.PRICE_LIST_NOT_EXIST})
        validate_data['default_price_list'] = default_pr

        primary_crc = Currency.objects.filter_on_company(is_primary=True).first()
        if not primary_crc:
            raise serializers.ValidationError({'sale_currency_using': ProductMsg.CURRENCY_NOT_EXIST})
        validate_data['sale_currency_using'] = primary_crc
        return validate_data

    def create(self, validated_data):
        default_pr = validated_data.pop('default_price_list')

        product = Product.objects.create(**validated_data)
        ProductCommonFunction.create_product_types_mapped(
            product, self.initial_data.get('product_types_mapped_list', [])
        )
        price_list_product_data = ProductCommonFunction.create_price_list_product(product, default_pr)
        product.sale_product_price_list = price_list_product_data
        product.save(update_fields=['sale_product_price_list'])
        return product


class UnitOfMeasureOfGroupLaborListSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = ('id', 'title', 'code', 'group', 'ratio')

    @classmethod
    def get_group(cls, obj):
        return {
            'id': obj.group_id, 'title': obj.group.title, 'is_referenced_unit': obj.is_referenced_unit
        } if obj.group else {}


class ProductSpecificIdentificationSerialNumberListSerializer(serializers.ModelSerializer):
    new_description = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpecificIdentificationSerialNumber
        fields = (
            'id',
            'product_id',
            'product_warehouse_serial_id',
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end',
            # trường này lưu giá trị thực tế đích danh (PP này chỉ apply cho SP serial)
            'specific_value',
            'serial_status',
            'new_description',
        )

    @classmethod
    def get_new_description(cls, obj):
        if obj.product_warehouse_serial:
            for pw_modified in obj.product_warehouse_serial.pw_modified_pw_serial.all():
                return pw_modified.new_description
        return ''


class ProductCommonFunction:
    @staticmethod
    def validate_dimension(value, field_name, error_msg):
        if value:
            try:
                value = float(value)
                if value <= 0:
                    raise serializers.ValidationError({field_name: error_msg})
            except ValueError:
                raise serializers.ValidationError({field_name: error_msg})
        else:
            value = None
        return value

    @staticmethod
    def create_price_list_product(product, price_list_obj):
        child_price_list = Price.get_children(price_list_obj)
        bulk_info = []
        price_list_product_data = []
        for child_obj, _ in child_price_list:
            price_list_product_obj = ProductPriceList(
                product=product,
                price_list=child_obj,
                price=0,
                currency_using=product.sale_currency_using,
                uom_using=product.sale_default_uom,
                uom_group_using=product.general_uom_group,
                get_price_from_source=str(child_obj.id) != str(price_list_obj.id),
            )
            bulk_info.append(price_list_product_obj)
            price_list_product_data.append({
                'price_list_id': str(price_list_product_obj.price_list_id),
                'price_value': price_list_product_obj.price,
                'is_auto_update': price_list_product_obj.get_price_from_source
            })
        ProductPriceList.objects.bulk_create(bulk_info)
        return price_list_product_data

    @staticmethod
    def create_price_list(product, data_price, validated_data):
        default_pr = Price.objects.filter_current(fill__tenant=True, fill__company=True, is_default=True).first()
        currency_using = product.sale_currency_using
        if not currency_using:
            primary_crc = Currency.objects.filter_current(
                fill__tenant=True, fill__company=True, is_primary=True
            ).first()
            if not primary_crc:
                raise serializers.ValidationError({'sale_currency_using': ProductMsg.CURRENCY_NOT_EXIST})
            currency_using = primary_crc
        if default_pr:
            if len(data_price) == 0:
                ProductCommonFunction.create_price_list_product(product, default_pr)
            else:
                objs = []
                for item in data_price:
                    objs.append(ProductPriceList(
                        product=product,
                        price_list_id=item.get('price_list_id', None),
                        price=float(item.get('price_list_value', 0)),
                        currency_using=currency_using,
                        uom_using=validated_data.get('sale_default_uom'),
                        uom_group_using=validated_data.get('general_uom_group'),
                        get_price_from_source=item.get('is_auto_update', None) == 'true'
                    ))
                    if str(default_pr.id) == item.get('price_list_id', None):
                        product.sale_price = float(item.get('price_list_value', 0))
                        product.save()
                ProductPriceList.objects.bulk_create(objs)
            return True
        return False

    @staticmethod
    def create_measure(product, data_measure):
        volume_id = data_measure['volume']['id'] if len(data_measure['volume']) > 0 else None
        weight_id = data_measure['weight']['id'] if len(data_measure['weight']) > 0 else None
        if volume_id and 'value' in data_measure['volume']:
            ProductMeasurements.objects.create(
                product=product,
                measure_id=volume_id,
                value=data_measure['volume']['value']
            )
        if weight_id and 'value' in data_measure['weight']:
            ProductMeasurements.objects.create(
                product=product,
                measure_id=weight_id,
                value=data_measure['weight']['value']
            )
        return True

    @staticmethod
    def sub_validate_volume_obj(initial_data, validate_data):
        volume_obj = None
        if initial_data.get('volume_id', None):
            volume_obj = BaseItemUnit.objects.filter(id=initial_data['volume_id'])
        if volume_obj and validate_data.get('volume', None):
            volume_obj = volume_obj.first()
            return {
                'id': str(volume_obj.id),
                'title': volume_obj.title,
                'measure': volume_obj.measure,
                'value': validate_data['volume']
            }
        return {}

    @staticmethod
    def sub_validate_weight_obj(initial_data, validate_data):
        weight_obj = None
        if initial_data.get('weight_id', None):
            weight_obj = BaseItemUnit.objects.filter(id=initial_data['weight_id'])
        if weight_obj and validate_data.get('weight', None):
            weight_obj = weight_obj.first()
            return {
                'id': str(weight_obj.id),
                'title': weight_obj.title,
                'measure': weight_obj.measure,
                'value': validate_data['weight']
            }
        return {}

    @staticmethod
    def setup_price_list_data_in_sale(initial_data):
        sale_price_list = initial_data.get('sale_price_list', [])
        for item in sale_price_list:
            price_list_id = item.get('price_list_id', None)
            price_list_value = float(item.get('price_list_value', 0))
            if not Price.objects.filter(id=price_list_id).exists() or price_list_value < 0:
                raise serializers.ValidationError({'sale_product_price_list': ProductMsg.PRICE_LIST_NOT_EXIST})
        return sale_price_list

    @staticmethod
    def create_product_types_mapped(product_obj, product_types_mapped_list):
        bulk_info = []
        for item in product_types_mapped_list:
            bulk_info.append(ProductProductType(product=product_obj, product_type_id=item))
        ProductProductType.objects.filter(product=product_obj).delete()
        ProductProductType.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def create_component_mapped(product_obj, component_list_data):
        bulk_info = []
        for item in component_list_data:
            bulk_info.append(ProductComponent(product=product_obj, **item))
        ProductComponent.objects.filter(product=product_obj).delete()
        ProductComponent.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def create_attribute_mapped(product_obj, attribute_list_data):
        bulk_info = []
        for order, item in enumerate(attribute_list_data):
            bulk_info.append(ProductAttribute(product=product_obj, order=order, attribute_id=item))
        ProductAttribute.objects.filter(product=product_obj).delete()
        ProductAttribute.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def create_product_variant_attribute(product_obj, product_variant_attribute_list):
        bulk_info = []
        for item in product_variant_attribute_list:
            bulk_info.append(ProductVariantAttribute(product=product_obj, **item))
        ProductVariantAttribute.objects.filter(product=product_obj).delete()
        ProductVariantAttribute.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def create_product_variant_item(product_obj, product_variant_item_list):
        bulk_info = []
        for item in product_variant_item_list:
            bulk_info.append(ProductVariant(product=product_obj, **item))
        ProductVariant.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def update_product_variant_item(product_obj, product_variant_item_update_list):
        bulk_info = []
        for item in product_variant_item_update_list:
            if item.get('variant_value_id', None):
                variant_value_id = item.pop('variant_value_id')
                ProductVariant.objects.filter(id=variant_value_id).update(**item)
            else:
                bulk_info.append(ProductVariant(product=product_obj, **item))
        ProductVariant.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def get_cumulative_factor(price_list):
        factor = 1.0
        current = price_list
        visited_price_list = set()
        # Traverse up the hierarchy until price_list_mapped is None (the root)
        # make sure price_list_mapped doesn't point back, example: A -> B -> A
        while current.price_list_mapped and current.id not in visited_price_list:
            visited_price_list.add(current.id)
            factor *= current.factor
            current = current.price_list_mapped

        return factor
