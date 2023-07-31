from rest_framework import serializers

from apps.masterdata.saledata.models import Account, Contact, Product, UnitOfMeasure, Tax
from apps.sales.purchasing.models import PurchaseRequest, PurchaseRequestProduct
from apps.sales.saleorder.models import SaleOrder
from apps.shared.translations.sales import PurchaseRequestMsg


class PurchaseRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = (
            'id',
            'code',
            'title',
            'request_for',
            'sale_order',
            'supplier',
            'delivered_date',
            'system_status',
            'purchase_status',
        )


class PurchaseRequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = '__all__'


class PurchaseRequestProductSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    uom = serializers.UUIDField()
    tax = serializers.UUIDField()

    class Meta:
        model = PurchaseRequestProduct
        fields = (
            'product',
            'description',
            'uom',
            'quantity',
            'unit_price',
            'tax',
            'sub_total_price'
        )

    @classmethod
    def validate_product(cls, value):
        try:
            product = Product.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            if 2 not in product.product_choice:
                raise serializers.ValidationError({'product': PurchaseRequestMsg.NOT_PURCHASE})
            return {
                'id': str(product.id),
                'title': product.title,
            }
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_tax(cls, value):
        try:
            tax = Tax.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(tax.id),
                'title': tax.title,
            }
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_uom(cls, value):
        try:
            uom = UnitOfMeasure.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(uom.id),
                'title': uom.title,
            }
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_unit_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'unit_price': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_sub_total_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'sub_total_price': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_quantity(cls, value):
        if value < 0:
            raise serializers.ValidationError({'quantity': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def create_product_datas(cls, purchase_request, product_datas):
        bulk_data = []
        for data in product_datas:
            bulk_data.append(
                PurchaseRequestProduct(
                    purchase_request=purchase_request,
                    product_id=data['product']['id'],
                    description=data['description'],
                    uom_id=data['uom']['id'],
                    tax_id=data['tax']['id'],
                    quantity=data['quantity'],
                    unit_price=data['unit_price'],
                    sub_total_price=data['sub_total_price']
                )
            )
        return bulk_data


class PurchaseRequestCreateSerializer(serializers.ModelSerializer):
    sale_order = serializers.UUIDField(required=False)
    supplier = serializers.UUIDField(required=True)
    contact = serializers.UUIDField(required=True)
    purchase_request_product_datas = PurchaseRequestProductSerializer(many=True)

    class Meta:
        model = PurchaseRequest
        fields = (
            'title',
            'supplier',
            'contact',
            'request_for',
            'sale_order',
            'delivered_date',
            'purchase_status',
            'note',
            'purchase_request_product_datas',
            'pretax_amount',
            'taxes',
            'total_price',
        )

    @classmethod
    def validate_supplier(cls, value):
        try:
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'supplier': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_contact(cls, value):
        try:
            return Contact.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_sale_order(cls, value):
        try:
            return SaleOrder.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except SaleOrder.DoesNotExist:
            raise serializers.ValidationError({'sale_order': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_pretax_amount(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_taxes(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_total_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    def create(self, validated_data):
        purchase_request = PurchaseRequest.objects.create(**validated_data)
        if len(validated_data['purchase_request_product_datas']) > 0:
            bulk_data = PurchaseRequestProductSerializer.create_product_datas(
                purchase_request,
                validated_data['purchase_request_product_datas']
            )
            PurchaseRequestProduct.objects.bulk_create(bulk_data)
        return purchase_request
