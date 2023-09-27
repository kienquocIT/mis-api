from rest_framework import serializers

# from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.inventory.models import GoodsReceipt, GoodsReceiptProduct, GoodsReceiptRequestProduct, \
    GoodsReceiptWarehouse, GoodsReceiptLot, GoodsReceiptSerial
from apps.sales.inventory.serializers.goods_receipt_sub import GoodsReceiptCommonValidate, GoodsReceiptCommonCreate
from apps.shared import SYSTEM_STATUS, GOODS_RECEIPT_TYPE


class GoodsReceiptSerialSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptSerial
        fields = (
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end',
        )


class GoodsReceiptSerialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptSerial
        fields = (
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end',
        )


class GoodsReceiptLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptLot
        fields = (
            'lot_number',
            'quantity_import',
            'expire_date',
            'manufacture_date',
        )


class GoodsReceiptLotListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptLot
        fields = (
            'lot_number',
            'quantity_import',
            'expire_date',
            'manufacture_date',
        )


class GoodsReceiptWarehouseSerializer(serializers.ModelSerializer):
    warehouse = serializers.UUIDField()
    lot_data = GoodsReceiptLotSerializer(many=True, required=False)
    serial_data = GoodsReceiptSerialSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptWarehouse
        fields = (
            'warehouse',
            'quantity_import',
            'lot_data',
            'serial_data',
        )

    @classmethod
    def validate_warehouse(cls, value):
        return GoodsReceiptCommonValidate.validate_warehouse(value=value)


class GoodsReceiptWarehouseListSerializer(serializers.ModelSerializer):
    warehouse = serializers.SerializerMethodField()
    lot_data = serializers.SerializerMethodField()
    serial_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceiptWarehouse
        fields = (
            'warehouse',
            'quantity_import',
            'lot_data',
            'serial_data',
        )

    @classmethod
    def get_warehouse(cls, obj):
        return {
            'id': obj.warehouse_id,
            'title': obj.warehouse.title,
            'code': obj.warehouse.code,
        } if obj.warehouse else {}

    @classmethod
    def get_lot_data(cls, obj):
        return GoodsReceiptLotListSerializer(obj.goods_receipt_lot_gr_warehouse.all(), many=True).data

    @classmethod
    def get_serial_data(cls, obj):
        return GoodsReceiptSerialListSerializer(obj.goods_receipt_serial_gr_warehouse.all(), many=True).data


class GoodsReceiptRequestProductSerializer(serializers.ModelSerializer):
    purchase_request_product = serializers.UUIDField()
    warehouse_data = GoodsReceiptWarehouseSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptRequestProduct
        fields = (
            'purchase_request_product',
            'quantity_import',
            'warehouse_data',
        )

    @classmethod
    def validate_purchase_request_product(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_request_product(value=value)


class GoodsReceiptRequestProductListSerializer(serializers.ModelSerializer):
    purchase_request_product = serializers.SerializerMethodField()
    warehouse_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceiptRequestProduct
        fields = (
            'purchase_request_product',
            'quantity_import',
            'warehouse_data',
        )

    @classmethod
    def get_purchase_request_product(cls, obj):
        return {
            'id': obj.purchase_request_product_id,
            'purchase_request': {
                'id': obj.purchase_request_product.purchase_request_id,
                'title': obj.purchase_request_product.purchase_request.title,
                'code': obj.purchase_request_product.purchase_request.code,
            } if obj.purchase_request_product.purchase_request else {},
            'uom': {
                'id': obj.purchase_request_product.uom_id,
                'title': obj.purchase_request_product.uom.title,
                'code': obj.purchase_request_product.uom.code,
            } if obj.purchase_request_product.uom else {},
        } if obj.purchase_request_product else {}

    @classmethod
    def get_warehouse_data(cls, obj):
        return GoodsReceiptWarehouseListSerializer(obj.goods_receipt_warehouse_request_product.all(), many=True).data


class GoodsReceiptProductSerializer(serializers.ModelSerializer):
    purchase_order_product = serializers.UUIDField(required=False)
    product = serializers.UUIDField(required=False)
    uom = serializers.UUIDField(required=False)
    tax = serializers.UUIDField(required=False)
    purchase_request_products_data = GoodsReceiptRequestProductSerializer(many=True, required=False)
    warehouse_data = GoodsReceiptWarehouseSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptProduct
        fields = (
            'purchase_order_product',
            'product',
            'uom',
            'tax',
            'quantity_import',
            'product_title',
            'product_code',
            'product_description',
            'product_unit_price',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
            'purchase_request_products_data',
            'warehouse_data'
        )

    @classmethod
    def validate_purchase_order_product(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_order_product(value=value)

    @classmethod
    def validate_product(cls, value):
        return GoodsReceiptCommonValidate.validate_product(value=value)

    @classmethod
    def validate_uom(cls, value):
        return GoodsReceiptCommonValidate.validate_uom(value=value)

    @classmethod
    def validate_tax(cls, value):
        return GoodsReceiptCommonValidate.validate_tax(value=value)


class GoodsReceiptProductListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    purchase_request_products_data = serializers.SerializerMethodField()
    warehouse_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceiptProduct
        fields = (
            'id',
            'purchase_order_product_id',
            'product',
            'uom',
            'tax',
            'quantity_import',
            'product_title',
            'product_code',
            'product_description',
            'product_unit_price',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
            'purchase_request_products_data',
            'warehouse_data',
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'general_traceability_method': obj.product.general_traceability_method,
        } if obj.product else {}

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': obj.uom_id,
            'title': obj.uom.title,
            'code': obj.uom.code,
            'uom_group': {
                'id': obj.uom.group_id,
                'title': obj.uom.group.title,
                'code': obj.uom.group.code,
                'uom_reference': {
                    'id': obj.uom.group.uom_reference_id,
                    'title': obj.uom.group.uom_reference.title,
                    'code': obj.uom.group.uom_reference.code,
                    'ratio': obj.uom.group.uom_reference.ratio,
                    'rounding': obj.uom.group.uom_reference.rounding,
                } if obj.uom.group.uom_reference else {},
            },
            'ratio': obj.uom.ratio,
            'rounding': obj.uom.rounding,
            'is_referenced_unit': obj.uom.is_referenced_unit,
        } if obj.uom else {}

    @classmethod
    def get_tax(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
            'code': obj.tax.code,
            'rate': obj.tax.rate,
        } if obj.tax else {}

    @classmethod
    def get_purchase_request_products_data(cls, obj):
        return GoodsReceiptRequestProductListSerializer(
            obj.goods_receipt_request_product_gr_product.all(),
            many=True
        ).data

    @classmethod
    def get_warehouse_data(cls, obj):
        return GoodsReceiptWarehouseListSerializer(obj.goods_receipt_warehouse_gr_product.all(), many=True).data


# GOODS RECEIPT BEGIN
class GoodsReceiptListSerializer(serializers.ModelSerializer):
    purchase_order = serializers.SerializerMethodField()
    inventory_adjustment = serializers.SerializerMethodField()
    goods_receipt_type = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'id',
            'title',
            'code',
            'goods_receipt_type',
            'purchase_order',
            'inventory_adjustment',
            'date_received',
            'system_status',
        )

    @classmethod
    def get_goods_receipt_type(cls, obj):
        if obj.goods_receipt_type or obj.goods_receipt_type == 0:
            return dict(GOODS_RECEIPT_TYPE).get(obj.goods_receipt_type)
        return None

    @classmethod
    def get_purchase_order(cls, obj):
        return {
            'id': obj.purchase_order_id,
            'title': obj.purchase_order.title,
            'code': obj.purchase_order.code,
        } if obj.purchase_order else {}

    @classmethod
    def get_inventory_adjustment(cls, obj):
        return {
            'id': obj.inventory_adjustment_id,
            'title': obj.inventory_adjustment.title,
            'code': obj.inventory_adjustment.code,
        } if obj.inventory_adjustment else {}

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


class GoodsReceiptDetailSerializer(serializers.ModelSerializer):
    purchase_order = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    purchase_requests = serializers.SerializerMethodField()
    goods_receipt_product = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'id',
            'title',
            'code',
            'goods_receipt_type',
            'purchase_order',
            'supplier',
            'purchase_requests',
            'remarks',
            'date_received',
            # line detail
            'goods_receipt_product',
            # system
            'system_status',
            'workflow_runtime_id',
            'is_active',
        )

    @classmethod
    def get_purchase_order(cls, obj):
        return {
            'id': obj.purchase_order_id,
            'title': obj.purchase_order.title,
            'code': obj.purchase_order.code,
        } if obj.purchase_order else {}

    @classmethod
    def get_supplier(cls, obj):
        return {
            'id': obj.supplier_id,
            'name': obj.supplier.name,
            'code': obj.supplier.code,
        } if obj.supplier else {}

    @classmethod
    def get_purchase_requests(cls, obj):
        return [
            {'id': purchase_request.id, 'title': purchase_request.title, 'code': purchase_request.code}
            for purchase_request in obj.purchase_requests.all()
        ]

    @classmethod
    def get_goods_receipt_product(cls, obj):
        return GoodsReceiptProductListSerializer(
            obj.goods_receipt_product_goods_receipt.all(),
            many=True
        ).data

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


class GoodsReceiptCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    purchase_order = serializers.UUIDField(required=False, allow_null=True)
    inventory_adjustment = serializers.UUIDField(required=False, allow_null=True)
    supplier = serializers.UUIDField(required=False, allow_null=True)
    purchase_requests = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    goods_receipt_product = GoodsReceiptProductSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceipt
        fields = (
            'title',
            'purchase_order',
            'inventory_adjustment',
            'supplier',
            'purchase_requests',
            'remarks',
            'date_received',
            # line detail
            'goods_receipt_product',
            # system
            'system_status',
        )

    @classmethod
    def validate_purchase_order(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_order(value=value)

    @classmethod
    def validate_inventory_adjustment(cls, value):
        return GoodsReceiptCommonValidate.validate_inventory_adjustment(value=value)

    @classmethod
    def validate_supplier(cls, value):
        return GoodsReceiptCommonValidate.validate_supplier(value=value)

    @classmethod
    def validate_purchase_requests(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_requests(value=value)

    # @decorator_run_workflow
    def create(self, validated_data):
        purchase_requests = []
        goods_receipt_product = []
        if 'purchase_requests' in validated_data:
            purchase_requests = validated_data['purchase_requests']
            del validated_data['purchase_requests']
        if 'goods_receipt_product' in validated_data:
            goods_receipt_product = validated_data['goods_receipt_product']
            del validated_data['goods_receipt_product']
        goods_receipt = GoodsReceipt.objects.create(**validated_data)
        # create sub models
        GoodsReceiptCommonCreate.create_goods_receipt_sub_models(
            purchase_requests=purchase_requests,
            goods_receipt_product=goods_receipt_product,
            instance=goods_receipt,
            is_update=False
        )
        return goods_receipt


class GoodsReceiptUpdateSerializer(serializers.ModelSerializer):
    purchase_order = serializers.UUIDField(required=False)
    inventory_adjustment = serializers.UUIDField(required=False)
    supplier = serializers.UUIDField(required=False)
    purchase_requests = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    goods_receipt_product = GoodsReceiptProductSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceipt
        fields = (
            'title',
            'purchase_order',
            'inventory_adjustment',
            'supplier',
            'purchase_requests',
            'remarks',
            'date_received',
            # line detail
            'goods_receipt_product',
            # system
            'system_status',
        )

    @classmethod
    def validate_purchase_order(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_order(value=value)

    @classmethod
    def validate_inventory_adjustment(cls, value):
        return GoodsReceiptCommonValidate.validate_inventory_adjustment(value=value)

    @classmethod
    def validate_supplier(cls, value):
        return GoodsReceiptCommonValidate.validate_supplier(value=value)

    @classmethod
    def validate_purchase_requests(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_requests(value=value)

    def update(self, instance, validated_data):
        purchase_requests = []
        goods_receipt_product = []
        if 'purchase_requests' in validated_data:
            purchase_requests = validated_data['purchase_requests']
            del validated_data['purchase_requests']
        if 'goods_receipt_product' in validated_data:
            goods_receipt_product = validated_data['goods_receipt_product']
            del validated_data['goods_receipt_product']
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # create sub models
        GoodsReceiptCommonCreate.create_goods_receipt_sub_models(
            purchase_requests=purchase_requests,
            goods_receipt_product=goods_receipt_product,
            instance=instance,
            is_update=True
        )
        return instance
