from datetime import datetime
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.masterdata.saledata.models.product import Product

PRODUCT_OPTION = [(0, _('Sale')), (1, _('Inventory')), (2, _('Purchase'))]


class ProductForSaleListSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    product_data = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    price_list = serializers.SerializerMethodField()
    product_choice = serializers.JSONField()
    general_information = serializers.SerializerMethodField()
    sale_information = serializers.SerializerMethodField()
    purchase_information = serializers.SerializerMethodField()
    inventory_information = serializers.SerializerMethodField()
    bom_check_data = serializers.SerializerMethodField()
    bom_data = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'code', 'title', 'description',
            'product_id', 'product_data',
            'general_information', 'sale_information', 'purchase_information',
            'price_list', 'product_choice', 'supplied_by', 'inventory_information',
            'general_traceability_method', 'bom_check_data', 'bom_data', 'standard_price',
            'lease_code', 'lease_time_previous', 'depreciation_price', 'depreciation_time',
            'origin_cost', 'date_first_delivery', 'depreciation_start_date', 'depreciation_end_date',
        )

    @classmethod
    def get_product_id(cls, obj):
        return obj.id

    @classmethod
    def get_product_data(cls, obj):
        return {'id': obj.id, 'title': obj.title, 'code': obj.code,}

    @classmethod
    def get_code(cls, obj):
        return obj.lease_source.code if obj.lease_source else obj.code

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
                'is_material': product_type.is_material, 'is_asset_tool': product_type.is_asset_tool,
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


class ProductForSaleDetailSerializer(serializers.ModelSerializer):
    cost_list = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'code', 'title', 'cost_list')

    @classmethod
    def get_cost_list(cls, obj):
        return obj.get_unit_cost_list_of_all_warehouse()
