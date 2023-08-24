from rest_framework import serializers

from apps.sales.purchasing.models import PurchaseOrder, PurchaseOrderProduct, PurchaseOrderRequestProduct, \
    PurchaseOrderQuotation
from apps.sales.purchasing.serializers.purchase_order_sub import PurchasingCommonValidate, PurchaseOrderCommonCreate
# from apps.core.workflow.tasks import decorator_run_workflow
from apps.shared import SYSTEM_STATUS, RECEIPT_STATUS


class PurchaseQuotationSerializer(serializers.ModelSerializer):
    purchase_quotation = serializers.UUIDField()

    class Meta:
        model = PurchaseOrderQuotation
        fields = (
            'purchase_quotation',
            'is_use',
        )

    @classmethod
    def validate_purchase_quotation(cls, value):
        return PurchasingCommonValidate().validate_purchase_quotation(value=value)


class PurchaseOrderRequestProductSerializer(serializers.ModelSerializer):
    purchase_request_product = serializers.UUIDField()
    sale_order_product = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = PurchaseOrderRequestProduct
        fields = (
            'purchase_request_product',
            'sale_order_product',
            'quantity_order',
            'quantity_remain',
        )

    @classmethod
    def validate_purchase_request_product(cls, value):
        return PurchasingCommonValidate().validate_purchase_request_product(value=value)

    @classmethod
    def validate_sale_order_product(cls, value):
        return PurchasingCommonValidate().validate_sale_order_product(value=value)


class PurchaseOrderRequestProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrderRequestProduct
        fields = (
            'purchase_request_product_id',
            'sale_order_product_id',
            'quantity_order',
            'quantity_remain',
        )


class PurchaseOrderProductSerializer(serializers.ModelSerializer):
    purchase_request_product_datas = PurchaseOrderRequestProductSerializer(
        many=True,
        required=False
    )
    product = serializers.UUIDField()
    uom_order_request = serializers.UUIDField()
    uom_order_actual = serializers.UUIDField()
    tax = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = PurchaseOrderProduct
        fields = (
            'product',
            'uom_order_request',
            'uom_order_actual',
            'tax',
            'stock',
            'purchase_request_product_datas',
            # product information
            'product_title',
            'product_code',
            'product_description',
            'product_quantity_order_request',
            'product_quantity_order_actual',
            'product_unit_price',
            'product_tax_title',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
        )

    @classmethod
    def validate_product(cls, value):
        return PurchasingCommonValidate().validate_product(value=value)

    @classmethod
    def validate_uom_order_request(cls, value):
        return PurchasingCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_uom_order_actual(cls, value):
        return PurchasingCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return PurchasingCommonValidate().validate_tax(value=value)


class PurchaseOrderProductListSerializer(serializers.ModelSerializer):
    purchase_request_product_datas = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    uom_order_request = serializers.SerializerMethodField()
    uom_order_actual = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderProduct
        fields = (
            'product',
            'uom_order_request',
            'uom_order_actual',
            'tax',
            'stock',
            'purchase_request_product_datas',
            # product information
            'product_title',
            'product_code',
            'product_description',
            'product_quantity_order_request',
            'product_quantity_order_actual',
            'product_unit_price',
            'product_tax_title',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
        )

    @classmethod
    def get_purchase_request_product_datas(cls, obj):
        return PurchaseOrderRequestProductListSerializer(obj.purchase_order_request_order_product.all(), many=True).data

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
        } if obj.product else {}

    @classmethod
    def get_uom_order_request(cls, obj):
        return {
            'id': obj.uom_order_request_id,
            'title': obj.uom_order_request.title,
            'code': obj.uom_order_request.code,
        } if obj.uom_order_request else {}

    @classmethod
    def get_uom_order_actual(cls, obj):
        return {
            'id': obj.uom_order_actual_id,
            'title': obj.uom_order_actual.title,
            'code': obj.uom_order_actual.code,
        } if obj.uom_order_actual else {}

    @classmethod
    def get_tax(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
            'code': obj.tax.code,
            'rate': obj.tax.rate,
        } if obj.tax else {}


# PURCHASE ORDER BEGIN
class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()
    receipt_status = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'code',
            'supplier',
            'delivered_date',
            'receipt_status',
            'system_status',
        )

    @classmethod
    def get_supplier(cls, obj):
        return {
            'id': obj.supplier_id,
            'title': obj.supplier.name,
            'code': obj.supplier.code,
        } if obj.supplier else {}

    @classmethod
    def get_receipt_status(cls, obj):
        if obj.receipt_status or obj.receipt_status == 0:
            return dict(RECEIPT_STATUS).get(obj.receipt_status)
        return None

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    purchase_requests_data = serializers.SerializerMethodField()
    purchase_quotations_data = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    purchase_order_products_data = serializers.SerializerMethodField()
    receipt_status = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'purchase_requests_data',
            'purchase_quotations_data',
            'supplier',
            'contact',
            'delivered_date',
            'status_delivered',
            'receipt_status',
            # purchase order tabs
            'purchase_order_products_data',
            # total amount
            'total_product_pretax_amount',
            'total_product_tax',
            'total_product',
            'total_product_revenue_before_tax',
            # system
            'system_status',
        )

    @classmethod
    def get_purchase_requests_data(cls, obj):
        return [{
            'id': purchase_request.id,
            'title': purchase_request.title,
            'code': purchase_request.code,
        } for purchase_request in obj.purchase_requests.all()]

    @classmethod
    def get_purchase_quotations_data(cls, obj):
        return [{
            'id': purchase_order_quotation.id,
            'purchase_quotation': {
                'id': purchase_order_quotation.purchase_quotation_id,
                'title': purchase_order_quotation.purchase_quotation.title,
                'code': purchase_order_quotation.purchase_quotation.code,
                'supplier': {
                    'id': purchase_order_quotation.purchase_quotation.supplier_mapped_id,
                    'name': purchase_order_quotation.purchase_quotation.supplier_mapped.name,
                    'code': purchase_order_quotation.purchase_quotation.supplier_mapped.code,
                } if purchase_order_quotation.purchase_quotation.supplier_mapped else {}
            } if purchase_order_quotation.purchase_quotation else {},
            'is_use': purchase_order_quotation.is_use,
        } for purchase_order_quotation in obj.purchase_order_quotation_order.all()]

    @classmethod
    def get_supplier(cls, obj):
        return {
            'id': obj.supplier_id,
            'name': obj.supplier.name,
            'code': obj.supplier.code,
        } if obj.supplier else {}

    @classmethod
    def get_contact(cls, obj):
        return {
            'id': obj.contact_id,
            'fullname': obj.contact.fullname,
            'code': obj.contact.code,
        } if obj.contact else {}

    @classmethod
    def get_purchase_order_products_data(cls, obj):
        return PurchaseOrderProductListSerializer(obj.purchase_order_product_order.all(), many=True).data

    @classmethod
    def get_receipt_status(cls, obj):
        if obj.receipt_status or obj.receipt_status == 0:
            return dict(RECEIPT_STATUS).get(obj.receipt_status)
        return None

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    purchase_requests_data = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    purchase_quotations_data = PurchaseQuotationSerializer(
        many=True,
        required=False
    )
    supplier = serializers.UUIDField(required=False)
    contact = serializers.UUIDField(required=False)
    # purchase order tabs
    purchase_order_products_data = PurchaseOrderProductSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = PurchaseOrder
        fields = (
            'title',
            'purchase_requests_data',
            'purchase_quotations_data',
            'supplier',
            'contact',
            'delivered_date',
            'status_delivered',
            # purchase order tabs
            'purchase_order_products_data',
            # total amount
            'total_product_pretax_amount',
            'total_product_tax',
            'total_product',
            'total_product_revenue_before_tax',
            # system
            'system_status',
        )

    @classmethod
    def validate_purchase_requests_data(cls, value):
        return PurchasingCommonValidate().validate_purchase_requests_data(value=value)

    @classmethod
    def validate_supplier(cls, value):
        return PurchasingCommonValidate().validate_supplier(value=value)

    @classmethod
    def validate_contact(cls, value):
        return PurchasingCommonValidate().validate_contact(value=value)

    # @decorator_run_workflow
    def create(self, validated_data):
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        PurchaseOrderCommonCreate().create_purchase_order_sub_models(
            validated_data=validated_data,
            instance=purchase_order
        )
        return purchase_order


class PurchaseOrderUpdateSerializer(serializers.ModelSerializer):
    purchase_requests_data = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    purchase_quotations_data = PurchaseQuotationSerializer(
        many=True,
        required=False
    )
    supplier = serializers.UUIDField(required=False)
    contact = serializers.UUIDField(required=False)
    # purchase order tabs
    purchase_order_products_data = PurchaseOrderProductSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = PurchaseOrder
        fields = (
            'title',
            'purchase_requests_data',
            'purchase_quotations_data',
            'supplier',
            'contact',
            'delivered_date',
            'status_delivered',
            # purchase order tabs
            'purchase_order_products_data',
            # total amount
            'total_product_pretax_amount',
            'total_product_tax',
            'total_product',
            'total_product_revenue_before_tax',
            # system
            'system_status',
        )

    @classmethod
    def validate_purchase_requests_data(cls, value):
        return PurchasingCommonValidate().validate_purchase_requests_data(value=value)

    @classmethod
    def validate_supplier(cls, value):
        return PurchasingCommonValidate().validate_supplier(value=value)

    @classmethod
    def validate_contact(cls, value):
        return PurchasingCommonValidate().validate_contact(value=value)

    def update(self, instance, validated_data):
        # update purchase order
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        PurchaseOrderCommonCreate().create_purchase_order_sub_models(
            validated_data=validated_data,
            instance=instance,
            is_update=True,
        )
        return instance
