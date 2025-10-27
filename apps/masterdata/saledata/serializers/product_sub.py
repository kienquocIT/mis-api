from datetime import datetime
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.masterdata.saledata.models.price import Price, Currency
from apps.masterdata.saledata.models.product import (
    UnitOfMeasure, ProductSpecificIdentificationSerialNumber, Product
)
from apps.masterdata.saledata.serializers.product_common import ProductCommonFunction
from apps.masterdata.saledata.serializers.product import ProductCreateSerializer
from apps.shared import ProductMsg, AttMsg, FORMATTING


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


class ProductForSaleListSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    product_data = serializers.SerializerMethodField()
    price_list = serializers.SerializerMethodField()
    product_choice = serializers.JSONField()
    general_information = serializers.SerializerMethodField()
    sale_information = serializers.SerializerMethodField()
    purchase_information = serializers.SerializerMethodField()
    inventory_information = serializers.SerializerMethodField()
    bom_check_data = serializers.SerializerMethodField()
    bom_data = serializers.SerializerMethodField()
    duration_unit = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'code', 'title', 'description',
            'product_id', 'product_data',
            'general_information', 'sale_information', 'purchase_information',
            'price_list', 'product_choice', 'supplied_by', 'inventory_information',
            'general_traceability_method', 'bom_check_data', 'bom_data', 'standard_price',
            'avatar_img', 'duration_unit',
        )

    @classmethod
    def get_product_id(cls, obj):
        return obj.id

    @classmethod
    def get_product_data(cls, obj):
        return {'id': obj.id, 'title': obj.title, 'code': obj.code,}

    @classmethod
    def check_status_price(cls, valid_time_start, valid_time_end):
        current_time = datetime.now().date()
        if (not valid_time_start.date() >= current_time) and (valid_time_end.date() >= current_time):
            return 1
        if valid_time_end.date() < current_time or valid_time_start.date() >= current_time:
            return 0
        return None

    @classmethod
    def get_price_list(cls, obj):
        return [
            {
                'id': str(price.price_list_id), 'title': price.price_list.title,
                'value': price.price, 'is_default': price.price_list.is_default,
                'price_status': cls.check_status_price(
                    price.price_list.valid_time_start, price.price_list.valid_time_end
                ), 'price_type': price.price_list.price_list_type,
                'uom': {
                    'id': str(price.uom_using_id), 'title': price.uom_using.title,
                    'code': price.uom_using.code, 'ratio': price.uom_using.ratio,
                    'rounding': price.uom_using.rounding,
                    'is_referenced_unit': price.uom_using.is_referenced_unit,
                }
            } for price in obj.product_price_product.all()
        ]

    @classmethod
    def get_general_information(cls, obj):
        return {
            'product_type': [{
                'id': str(product_type.id), 'title': product_type.title, 'code': product_type.code,
                'is_goods': product_type.is_goods, 'is_finished_goods': product_type.is_finished_goods,
                'is_material': product_type.is_material, 'is_tool': product_type.is_tool,
                'is_service': product_type.is_service,
            } for product_type in obj.general_product_types_mapped.all()],
            'product_category': {
                'id': str(obj.general_product_category_id), 'title': obj.general_product_category.title,
                'code': obj.general_product_category.code
            } if obj.general_product_category else {},
            'uom_group': {
                'id': str(obj.general_uom_group_id), 'title': obj.general_uom_group.title,
                'code': obj.general_uom_group.code
            } if obj.general_uom_group else {},
            'general_traceability_method': obj.general_traceability_method,
        }

    @classmethod
    def get_sale_information(cls, obj):
        return {
            'default_uom': {
                'id': str(obj.sale_default_uom_id), 'title': obj.sale_default_uom.title,
                'code': obj.sale_default_uom.code, 'ratio': obj.sale_default_uom.ratio,
                'rounding': obj.sale_default_uom.rounding, 'is_referenced_unit': obj.sale_default_uom.is_referenced_unit
            } if obj.sale_default_uom else {},
            'tax_code': {
                'id': str(obj.sale_tax_id), 'title': obj.sale_tax.title,
                'code': obj.sale_tax.code, 'rate': obj.sale_tax.rate
            } if obj.sale_tax else {},
            'currency_using': {
                'id': str(obj.sale_currency_using_id), 'title': obj.sale_currency_using.title,
                'code': obj.sale_currency_using.code,
            } if obj.sale_currency_using else {},
            'length': obj.length, 'width': obj.width, 'height': obj.height,
        }

    @classmethod
    def get_purchase_information(cls, obj):
        return {
            'uom': {
                'id': str(obj.purchase_default_uom_id), 'title': obj.purchase_default_uom.title,
                'code': obj.purchase_default_uom.code, 'ratio': obj.purchase_default_uom.ratio,
                'rounding': obj.purchase_default_uom.rounding,
                'is_referenced_unit': obj.purchase_default_uom.is_referenced_unit,
            } if obj.purchase_default_uom else {},
            'tax': {
                'id': str(obj.purchase_tax_id), 'title': obj.purchase_tax.title,
                'code': obj.purchase_tax.code, 'rate': obj.purchase_tax.rate,
            } if obj.purchase_tax else {}
        }

    @classmethod
    def get_inventory_information(cls, obj):
        return {
            'uom': {
                'id': str(obj.inventory_uom_id), 'title': obj.inventory_uom.title,
                'code': obj.inventory_uom.code, 'ratio': obj.inventory_uom.ratio,
                'rounding': obj.inventory_uom.rounding,
                'is_referenced_unit': obj.inventory_uom.is_referenced_unit,
            } if obj.inventory_uom else {},
        }

    @classmethod
    def get_bom_check_data(cls, obj):
        return {
            'is_bom': bool(obj.filtered_bom),
            'is_bom_opp': bool(obj.filtered_bom_opp),
            'is_so_finished': bool(obj.filtered_so_product_finished),
            'is_so_using': bool(obj.filtered_so_product_using),
        }

    @classmethod
    def get_bom_data(cls, obj):
        for bom in obj.filtered_bom_opp:
            return {
                'id': bom.id,
                'title': bom.title,
                'code': bom.code,
                'opportunity': {
                    'id': bom.opportunity_id,
                    'title': bom.opportunity.title,
                    'code': bom.opportunity.code,
                } if bom.opportunity else {}
            }
        return {}

    @classmethod
    def get_duration_unit(cls, obj):
        return {
            'id': str(obj.duration_unit_id), 'title': obj.duration_unit.title,
            'code': obj.duration_unit.code, 'ratio': obj.duration_unit.ratio,
            'rounding': obj.duration_unit.rounding, 'is_referenced_unit': obj.duration_unit.is_referenced_unit
        } if obj.duration_unit else {}


class ProductForSaleDetailSerializer(serializers.ModelSerializer):
    cost_list = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'code', 'title', 'cost_list')

    @classmethod
    def get_cost_list(cls, obj):
        return obj.get_cost_info_of_all_warehouse()


class ProductUploadAvatarSerializer(serializers.ModelSerializer):
    @classmethod
    def validate_avatar_img(cls, attrs):
        if attrs and hasattr(attrs, 'size'):
            if isinstance(attrs.size, int) and attrs.size < settings.FILE_AVATAR_MAX_SIZE:
                return attrs
            file_size_limit = AttMsg.FILE_SIZE_SHOULD_BE_LESS_THAN_X.format(
                FORMATTING.size_to_text(settings.FILE_AVATAR_MAX_SIZE)
            )
            raise serializers.ValidationError({'avatar_img': file_size_limit})
        raise serializers.ValidationError({'avatar_img': AttMsg.FILE_NO_DETECT_SIZE})

    def update(self, instance, validated_data):
        if instance.avatar_img:
            instance.avatar_img.storage.delete(instance.avatar_img.name)
        # trick or fixed issue: https://docs.djangoproject.com/en/4.2/ref/forms/fields/#django.forms.ImageField
        # https://stackoverflow.com/a/77483484/13048590
        instance.avatar_img = validated_data['avatar_img']
        instance.save(update_fields=['avatar_img'])
        return instance

    class Meta:
        model = Product
        fields = ('avatar_img',)
