from rest_framework import serializers
from apps.sales.purchasing.models import (
    PurchaseQuotationRequest, PurchaseQuotationRequestProduct, PurchaseQuotationRequestPurchaseRequest,
)
from apps.shared.translations.sales import PurchaseRequestMsg


class PurchaseQuotationRequestListSerializer(serializers.ModelSerializer):
    purchase_requests = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseQuotationRequest
        fields = (
            'id',
            'code',
            'title',
            'purchase_requests',
            'delivered_date',
            'response_status',
        )

    @classmethod
    def get_purchase_requests(cls, obj):
        purchase_request_list = []
        for item in obj.purchase_request_mapped.all():
            purchase_request_list.append({
                'id': item.id,
                'code': item.code,
                'title': item.title
            })
        return purchase_request_list


class PurchaseQuotationRequestDetailSerializer(serializers.ModelSerializer):
    purchase_requests = serializers.SerializerMethodField()
    products_mapped = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseQuotationRequest
        fields = (
            'id',
            'code',
            'title',
            'purchase_requests',
            'delivered_date',
            'note',
            'pretax_price',
            'taxes_price',
            'total_price',
            'products_mapped',
            'purchase_quotation_request_type'
        )

    @classmethod
    def get_purchase_requests(cls, obj):
        purchase_request_list = []
        for item in obj.purchase_request_mapped.all():
            purchase_request_list.append({'id': str(item.id), 'code': item.code, 'title': item.title})
        return purchase_request_list

    @classmethod
    def get_products_mapped(cls, obj):
        product_mapped_list = []
        index = 1
        for item in obj.purchase_quotation_request.all().select_related('product', 'uom', 'tax'):
            product_mapped_list.append({
                'index': index,
                'product': {
                    'id': item.product_id,
                    'code': item.product.code,
                    'title': item.product.title,
                    'uom': {
                        'id': item.uom_id, 'code': item.uom.code, 'title': item.uom.title
                    } if item.uom else {},
                    'uom_group': {
                        'id': item.uom.group_id, 'code': item.uom.group.code, 'title': item.uom.group.title
                    } if item.uom.group else {},
                    'tax': {
                        'id': item.tax_id, 'code': item.tax.code, 'title': item.tax.title, 'rate': item.tax.rate
                    } if item.tax else {}
                } if item.product else {},
                'description': item.description,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'subtotal_price': item.subtotal_price
            })
            index += 1
        return product_mapped_list


def create_pr_map_pqr(pqr, pr_list):
    bulk_info = []
    for item in pr_list:
        bulk_info.append(
            PurchaseQuotationRequestPurchaseRequest(
                purchase_quotation_request=pqr,
                purchase_request_id=item
            )
        )
    PurchaseQuotationRequestPurchaseRequest.objects.bulk_create(bulk_info)
    return True


def create_pqr_map_products(purchase_quotation_request_obj, product_list):
    bulk_info = []
    for item in product_list:
        bulk_info.append(
            PurchaseQuotationRequestProduct(
                purchase_quotation_request=purchase_quotation_request_obj,
                product_id=item.get('product_id', None),
                description=item.get('product_description', None),
                uom_id=item.get('product_uom_id', None),
                quantity=item.get('product_quantity', None),
                unit_price=item.get('product_unit_price', None),
                tax_id=item.get('product_taxes', None),
                subtotal_price=item.get('product_subtotal_price', None),
            )
        )
    PurchaseQuotationRequestProduct.objects.bulk_create(bulk_info)
    return True


class PurchaseQuotationRequestCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseQuotationRequest
        fields = (
            'title',
            'delivered_date',
            'note',
            'pretax_price',
            'taxes_price',
            'total_price',
            'purchase_quotation_request_type'
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
        purchase_request_list = self.initial_data.get('purchase_request_list', [])
        if len(purchase_request_list) <= 0 and not validate_data.get('purchase_quotation_request_type', None):
            raise serializers.ValidationError({'purchase_request': PurchaseRequestMsg.PR_NOT_NULL})
        products_selected = self.initial_data.get('products_selected', [])
        if len(products_selected) <= 0:
            raise serializers.ValidationError({'purchase_request': PurchaseRequestMsg.PRODUCT_NOT_NULL})
        return validate_data

    def create(self, validated_data):
        if PurchaseQuotationRequest.objects.filter_current(fill__tenant=True, fill__company=True).count() == 0:
            new_code = 'PQR.CODE.0001'
        else:
            latest_code = PurchaseQuotationRequest.objects.filter_current(
                fill__tenant=True, fill__company=True
            ).latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1
            new_code = 'PQR.CODE.000' + str(new_code)

        purchase_quotation_request = PurchaseQuotationRequest.objects.create(**validated_data, code=new_code)

        create_pr_map_pqr(purchase_quotation_request, self.initial_data.get('purchase_request_list', []))
        create_pqr_map_products(purchase_quotation_request, self.initial_data.get('products_selected', []))
        return purchase_quotation_request


class PurchaseQuotationRequestListForPQSerializer(serializers.ModelSerializer):
    product_list = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseQuotationRequest
        fields = (
            'id',
            'code',
            'title',
            'product_list'
        )

    @classmethod
    def get_product_list(cls, obj):
        product_list = []
        for item in obj.purchase_quotation_request.all().select_related('product', 'uom', 'tax'):
            product_list.append({
                'id': item.product_id,
                'title': item.product.title,
                'uom': {
                    'id': item.uom_id,
                    'title': item.uom.title,
                    'ratio': item.uom.ratio,
                    'group_id': item.uom.group_id
                },
                'quantity': item.quantity,
                'product_unit_price': item.unit_price,
                'product_subtotal_price': item.subtotal_price,
                'tax': {'id': item.tax_id, 'title': item.tax.title, 'code': item.tax.code, 'value': item.tax.rate},
                'description': item.description
            })
        return product_list
