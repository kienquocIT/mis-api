from rest_framework import serializers

from apps.sales.purchasing.models import PurchaseOrder, PurchaseOrderProduct, PurchaseOrderRequestProduct
from apps.sales.purchasing.serializers.purchase_order_sub import PurchasingCommonValidate, PurchaseOrderCommonCreate
# from apps.core.workflow.tasks import decorator_run_workflow
from apps.shared import SYSTEM_STATUS


class PurchaseQuotationSerializer(serializers.ModelSerializer):
    purchase_quotation = serializers.UUIDField()

    class Meta:
        model = PurchaseOrderRequestProduct
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


class PurchaseOrderProductSerializer(serializers.ModelSerializer):
    purchase_request_product_datas = PurchaseOrderRequestProductSerializer(
        many=True,
        required=False
    )
    product = serializers.UUIDField()
    uom_request = serializers.UUIDField()
    uom_order = serializers.UUIDField()
    tax = serializers.UUIDField()

    class Meta:
        model = PurchaseOrderProduct
        fields = (
            'product',
            'uom_request',
            'uom_order',
            'tax',
            'stock',
            'purchase_request_product_datas',
            # product information
            'product_title',
            'product_code',
            'product_description',
            'product_uom_request_title',
            'product_uom_order_title',
            'product_quantity_request',
            'product_quantity_order',
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
    def validate_uom_request(cls, value):
        return PurchasingCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_uom_order(cls, value):
        return PurchasingCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return PurchasingCommonValidate().validate_tax(value=value)


# PURCHASE ORDER BEGIN
class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()
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
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'title': obj.supplier.name,
                'code': obj.supplier.code,
            }
        return {}

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'code',
            'supplier',
            'contact',
            'purchase_requests',
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
    def get_supplier(cls, obj):
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'title': obj.supplier.name,
                'code': obj.supplier.code,
            }
        return {}

    @classmethod
    def get_contact(cls, obj):
        if obj.contact:
            return {
                'id': obj.contact_id,
                'title': obj.contact.fullname,
                'code': obj.contact.code,
            }
        return {}

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
