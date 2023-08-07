from rest_framework import serializers
from apps.sales.purchasing.models import (
    PurchaseQuotation, PurchaseQuotationProduct
)
from apps.shared.translations.sales import PurchaseRequestMsg


class PurchaseQuotationListSerializer(serializers.ModelSerializer):
    supplier_mapped = serializers.SerializerMethodField()
    purchase_quotation_request_mapped = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseQuotation
        fields = (
            'id',
            'code',
            'title',
            'supplier_mapped',
            'purchase_quotation_request_mapped',
            'expiration_date',
        )

    @classmethod
    def get_purchase_quotation_request_mapped(cls, obj):
        if obj.purchase_quotation_request_mapped:
            return {
                'id': obj.purchase_quotation_request_mapped.id,
                'code': obj.purchase_quotation_request_mapped.code,
                'title': obj.purchase_quotation_request_mapped.title
            }
        return {}

    @classmethod
    def get_supplier_mapped(cls, obj):
        if obj.supplier_mapped:
            return {
                'id': obj.supplier_mapped_id,
                'code': obj.supplier_mapped.code,
                'name': obj.supplier_mapped.name
            }
        return {}


class PurchaseQuotationDetailSerializer(serializers.ModelSerializer):
    supplier_mapped = serializers.SerializerMethodField()
    contact_mapped = serializers.SerializerMethodField()
    purchase_quotation_request_mapped = serializers.SerializerMethodField()
    products_mapped = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseQuotation
        fields = (
            'id',
            'code',
            'title',
            'supplier_mapped',
            'contact_mapped',
            'purchase_quotation_request_mapped',
            'expiration_date',
            'lead_time_from',
            'lead_time_to',
            'lead_time_type',
            'note',
            'products_mapped',
            'pretax_price',
            'taxes_price',
            'total_price'
        )

    @classmethod
    def get_supplier_mapped(cls, obj):
        if obj.supplier_mapped:
            return {
                'id': obj.supplier_mapped_id,
                'code': obj.supplier_mapped.code,
                'name': obj.supplier_mapped.name
            }
        return {}

    @classmethod
    def get_contact_mapped(cls, obj):
        if obj.contact_mapped:
            return {
                'id': obj.contact_mapped_id,
                'code': obj.contact_mapped.code,
                'fullname': obj.contact_mapped.fullname
            }
        return {}

    @classmethod
    def get_purchase_quotation_request_mapped(cls, obj):
        if obj.purchase_quotation_request_mapped:
            return {
                'id': obj.purchase_quotation_request_mapped_id,
                'code': obj.purchase_quotation_request_mapped.code,
                'title': obj.purchase_quotation_request_mapped.title
            }
        return {}

    @classmethod
    def get_products_mapped(cls, obj):
        product_mapped_list = []
        index = 1
        for item in obj.purchase_quotation.all().select_related('product', 'uom', 'tax'):
            product_mapped_list.append(
                {
                    'index': index,
                    'product': {
                        'id': item.product_id,
                        'code': item.product.code,
                        'title': item.product.title,
                        'uom': {'id': item.uom_id, 'code': item.uom.code, 'title': item.uom.title} if item.uom else {},
                        'tax': {'id': item.tax_id, 'code': item.tax.code, 'title': item.tax.title} if item.tax else {}
                    },
                    'description': item.description,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'subtotal_price': item.subtotal_price
                }
            )
            index += 1
        return product_mapped_list


def create_pq_map_products(purchase_quotation_obj, product_list):
    bulk_info = []
    for item in product_list:
        bulk_info.append(
            PurchaseQuotationProduct(
                purchase_quotation=purchase_quotation_obj,
                product_id=item.get('product_id', None),
                description=item.get('product_description', None),
                uom_id=item.get('product_uom_id', None),
                quantity=item.get('product_quantity', None),
                unit_price=item.get('product_unit_price', None),
                tax_id=item.get('product_taxes', None),
                subtotal_price=item.get('product_subtotal_price', None),
            )
        )
    PurchaseQuotationProduct.objects.bulk_create(bulk_info)
    return True


class PurchaseQuotationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseQuotation
        fields = (
            'title',
            'expiration_date',
            'note',
            'pretax_price',
            'taxes_price',
            'total_price',
            'lead_time_from',
            'lead_time_to',
            'lead_time_type',
            'supplier_mapped',
            'contact_mapped',
            'purchase_quotation_request_mapped'
        )

    @classmethod
    def validate_pretax_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_price': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_taxes_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'taxes_price': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_total_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'total_price': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    def validate(self, validate_data):
        products_selected = self.initial_data.get('products_selected', [])
        if len(products_selected) <= 0:
            raise serializers.ValidationError({'purchase_request': PurchaseRequestMsg.PRODUCT_NOT_NULL})
        return validate_data

    def create(self, validated_data):
        if PurchaseQuotation.objects.filter_current(fill__tenant=True, fill__company=True).count() == 0:
            new_code = 'PQ.CODE.0001'
        else:
            latest_code = PurchaseQuotation.objects.filter_current(
                fill__tenant=True, fill__company=True
            ).latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1
            new_code = 'PQ.CODE.000' + str(new_code)

        purchase_quotation = PurchaseQuotation.objects.create(**validated_data, code=new_code)
        create_pq_map_products(purchase_quotation, self.initial_data.get('products_selected', []))
        return purchase_quotation
