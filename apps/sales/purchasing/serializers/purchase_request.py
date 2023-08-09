from rest_framework import serializers
from apps.masterdata.saledata.models import Account, Contact, Product, UnitOfMeasure, Tax
from apps.sales.purchasing.models import PurchaseRequest, PurchaseRequestProduct
from apps.sales.saleorder.models import SaleOrder, SaleOrderProduct
from apps.shared import REQUEST_FOR, PURCHASE_STATUS
from apps.shared.translations.sales import PurchaseRequestMsg


class PurchaseRequestListSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    request_for = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    purchase_status = serializers.SerializerMethodField()

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

    @classmethod
    def get_request_for(cls, obj):
        return dict(REQUEST_FOR).get(obj.request_for)

    @classmethod
    def get_sale_order(cls, obj):
        if obj.sale_order:
            return {
                'id': obj.sale_order_id,
                'title': obj.sale_order.title,
            }
        return None

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'title': obj.supplier.name,
            }
        return None

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status:
            return 'Open'
        return 'Open'

    @classmethod
    def get_purchase_status(cls, obj):
        return dict(PURCHASE_STATUS).get(obj.purchase_status)


class PurchaseRequestDetailSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    request_for = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    purchase_status = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequest
        fields = (
            'id',
            'title',
            'code',
            'request_for',
            'supplier',
            'contact',
            'delivered_date',
            'system_status',
            'purchase_status',
            'note',
            'sale_order',
            'purchase_request_product_datas',
            'pretax_amount',
            'taxes',
            'total_price',
        )

    @classmethod
    def get_request_for(cls, obj):
        return dict(REQUEST_FOR).get(obj.request_for)

    @classmethod
    def get_sale_order(cls, obj):
        if obj.sale_order:
            return {
                'id': obj.sale_order_id,
                'code': obj.sale_order.code,
                'title': obj.sale_order.title,
            }
        return None

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'name': obj.supplier.name,
            }
        return None

    @classmethod
    def get_contact(cls, obj):
        if obj.supplier:
            return {
                'id': obj.contact_id,
                'name': obj.contact.fullname,
            }
        return None

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status:
            return 'Open'
        return 'Open'

    @classmethod
    def get_purchase_status(cls, obj):
        return dict(PURCHASE_STATUS).get(obj.purchase_status)


class PurchaseRequestProductSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    sale_order_product = serializers.UUIDField(allow_null=True)
    uom = serializers.UUIDField()
    tax = serializers.UUIDField()
    description = serializers.CharField(allow_blank=True)

    class Meta:
        model = PurchaseRequestProduct
        fields = (
            'sale_order_product',
            'product',
            'description',
            'uom',
            'quantity',
            'unit_price',
            'tax',
            'sub_total_price'
        )

    @classmethod
    def validate_sale_order_product(cls, value):
        if value:
            try:
                so_product = SaleOrderProduct.objects.get(
                    id=value
                )
                return str(so_product.id)
            except Product.DoesNotExist:
                raise serializers.ValidationError({'product': PurchaseRequestMsg.NOT_IN_SALE_ORDER})
        return None

    @classmethod
    def validate_product(cls, value):
        try:
            product = Product.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
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
            pr_product = PurchaseRequestProduct(
                purchase_request=purchase_request,
                sale_order_product_id=data['sale_order_product'],
                product_id=data['product']['id'],
                description=data['description'],
                uom_id=data['uom']['id'],
                tax_id=data['tax']['id'],
                quantity=data['quantity'],
                unit_price=data['unit_price'],
                sub_total_price=data['sub_total_price']
            )
            if pr_product.sale_order_product:
                pr_product.sale_order_product.remain_for_purchase_request -= pr_product.quantity
                pr_product.sale_order_product.save()
            bulk_data.append(pr_product)
        return bulk_data


class PurchaseRequestCreateSerializer(serializers.ModelSerializer):
    sale_order = serializers.UUIDField(required=False, allow_null=True)
    supplier = serializers.UUIDField(required=True)
    contact = serializers.UUIDField(required=True)
    purchase_request_product_datas = PurchaseRequestProductSerializer(many=True)
    note = serializers.CharField(allow_blank=True)

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
        if value:
            try:
                return SaleOrder.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=value
                )
            except SaleOrder.DoesNotExist:
                raise serializers.ValidationError({'sale_order': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

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


class PurchaseRequestListForPQRSerializer(serializers.ModelSerializer):
    product_list = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequest
        fields = (
            'id',
            'code',
            'title',
            'product_list'
        )

    @classmethod
    def get_product_list(cls, obj):
        product_list = []
        for item in obj.purchase_request.all().select_related('product', 'uom', 'tax'):
            product_list.append({
                'id': item.product_id,
                'title': item.product.title,
                'uom': {'id': item.uom_id, 'title': item.uom.title, 'ratio': item.uom.ratio},
                'quantity': item.quantity,
                'purchase_request_id': item.purchase_request_id,
                'purchase_request_code': item.purchase_request.code,
                'product_unit_price': item.unit_price,
                'product_subtotal_price': item.sub_total_price,
                'tax': {'id': item.tax_id, 'title': item.tax.title, 'code': item.tax.code, 'value': item.tax.rate},
                'description': item.description
            })
        return product_list


class PurchaseRequestProductListSerializer(serializers.ModelSerializer):
    purchase_request = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequestProduct
        fields = (
            'id',
            'purchase_request',
            'sale_order_product_id',
            'product',
            'uom',
            'quantity',
            'remain_for_purchase_order',
        )

    @classmethod
    def get_purchase_request(cls, obj):
        if obj.purchase_request:
            return {
                'id': obj.purchase_request_id,
                'title': obj.purchase_request.title,
                'code': obj.purchase_request.code,
            }
        return {}

    @classmethod
    def get_product(cls, obj):
        if obj.product:
            return {
                'id': obj.product_id,
                'title': obj.product.title,
                'code': obj.product.code,
            }
        return {}

    @classmethod
    def get_uom(cls, obj):
        if obj.uom:
            return {
                'id': obj.uom_id,
                'title': obj.uom.title,
                'code': obj.uom.code,
            }
        return {}
