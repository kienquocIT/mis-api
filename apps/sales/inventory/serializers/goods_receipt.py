from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models.product_warehouse import ProductWareHouseSerial, ProductWareHouseLot
from apps.sales.inventory.models import GoodsReceipt, GoodsReceiptProduct, GoodsReceiptRequestProduct, \
    GoodsReceiptWarehouse, GoodsReceiptLot, GoodsReceiptSerial, InventoryAdjustmentItem
from apps.sales.inventory.serializers.goods_receipt_sub import GoodsReceiptCommonValidate, GoodsReceiptCommonCreate


class GoodsReceiptSerialSerializer(serializers.ModelSerializer):
    serial_number = serializers.CharField(max_length=100, required=False, allow_blank=False)

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
    lot = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = GoodsReceiptLot
        fields = (
            'lot',
            'lot_number',
            'quantity_import',
            'expire_date',
            'manufacture_date',
        )

    @classmethod
    def validate_lot(cls, value):
        return GoodsReceiptCommonValidate.validate_lot(value=value)


class GoodsReceiptLotListSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsReceiptLot
        fields = (
            'lot_id',
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
            'is_additional',
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
            'is_additional',
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
    purchase_order_request_product = serializers.UUIDField()
    purchase_request_product = serializers.UUIDField(required=False, allow_null=True)
    warehouse_data = GoodsReceiptWarehouseSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptRequestProduct
        fields = (
            'purchase_order_request_product',
            'purchase_request_product',
            'quantity_import',
            'warehouse_data',
            'is_stock',
        )

    @classmethod
    def validate_purchase_order_request_product(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_order_request_product(value=value)

    @classmethod
    def validate_purchase_request_product(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_request_product(value=value)


class GoodsReceiptRequestProductListSerializer(serializers.ModelSerializer):
    purchase_request_product = serializers.SerializerMethodField()
    warehouse_data = serializers.SerializerMethodField()
    purchase_order_request_product = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceiptRequestProduct
        fields = (
            'purchase_request_product',
            'quantity_import',
            'warehouse_data',
            'purchase_order_request_product',
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

    @classmethod
    def get_purchase_order_request_product(cls, obj):
        return obj.purchase_order_request_product_id


class GoodsReceiptProductSerializer(serializers.ModelSerializer):
    purchase_order_product = serializers.UUIDField(required=False)
    product = serializers.UUIDField(required=False)
    uom = serializers.UUIDField(required=False)
    tax = serializers.UUIDField(required=False)
    warehouse = serializers.UUIDField(required=False)
    product_unit_price = serializers.FloatField()
    quantity_import = serializers.FloatField()
    purchase_request_products_data = GoodsReceiptRequestProductSerializer(many=True, required=False)
    warehouse_data = GoodsReceiptWarehouseSerializer(many=True, required=False)
    ia_item = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = GoodsReceiptProduct
        fields = (
            'purchase_order_product',
            'product',
            'uom',
            'tax',
            'warehouse',
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
            'is_additional',
            'ia_item'
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

    @classmethod
    def validate_warehouse(cls, value):
        return GoodsReceiptCommonValidate.validate_warehouse(value=value)

    @classmethod
    def validate_quantity_import(cls, value):
        return GoodsReceiptCommonValidate.validate_quantity_import(value=value)

    @classmethod
    def validate_product_unit_price(cls, value):
        return GoodsReceiptCommonValidate().validate_price(value=value)

    @classmethod
    def validate_ia_item(cls, value):
        try:
            if value is None:
                return None
            return InventoryAdjustmentItem.objects.get(id=value)
        except InventoryAdjustmentItem.DoesNotExist:
            raise serializers.ValidationError({'unit_of_measure': 'IA item not exist'})

    @classmethod
    def check_lot_serial_exist(cls, warehouse_data, product_obj):
        serial_number_list = []
        for wh_data in warehouse_data:
            lot_number_list = []
            for lot in wh_data.get('lot_data', []):
                lot_obj = lot.get('lot', None)
                if not lot_obj:
                    lot_number_list.append(lot.get('lot_number', None))
            # check lot
            cls.check_lot_exist(
                product_obj=product_obj, warehouse_obj=wh_data.get('warehouse', None), lot_number_list=lot_number_list
            )
            for serial in wh_data.get('serial_data', []):
                serial_number_list.append(serial.get('serial_number', None))
        # check serial
        cls.check_serial_exist(product_obj=product_obj, serial_number_list=serial_number_list)
        return True

    @classmethod
    def check_lot_exist(cls, product_obj, warehouse_obj, lot_number_list):
        # check unique in data submit (in same warehouse)
        if len(lot_number_list) != len(set(lot_number_list)):
            raise serializers.ValidationError({'lot_number': 'Lot number must be different.'})
        # check unique in db
        if product_obj and warehouse_obj:
            for product_wh_lot in ProductWareHouseLot.objects.filter(
                    tenant_id=product_obj.tenant_id,
                    company_id=product_obj.company_id,
                    lot_number__in=lot_number_list
            ):
                if product_wh_lot.product_warehouse:
                    pwh = product_wh_lot.product_warehouse
                    if pwh.product_id == product_obj.id and pwh.warehouse_id == warehouse_obj.id:
                        raise serializers.ValidationError({'lot_number': 'Lot number is exist.'})
                    if pwh.product_id != product_obj.id:
                        raise serializers.ValidationError({'lot_number': 'Lot number is exist.'})
        return True

    @classmethod
    def check_serial_exist(cls, product_obj, serial_number_list):
        # check unique in data submit
        if len(serial_number_list) != len(set(serial_number_list)):
            raise serializers.ValidationError({'serial_number': 'Serial number must be different.'})
        # check unique in db
        if ProductWareHouseSerial.objects.filter(
                tenant_id=product_obj.tenant_id,
                company_id=product_obj.company_id,
                product_warehouse__product=product_obj,
                serial_number__in=serial_number_list
        ).exists():
            raise serializers.ValidationError({'serial_number': 'Serial number is exist.'})
        return True

    def validate(self, validate_data):
        if 'product' in validate_data:
            if 'warehouse_data' in validate_data:
                warehouse_data = validate_data['warehouse_data']
                self.check_lot_serial_exist(warehouse_data=warehouse_data, product_obj=validate_data['product'])
            if 'purchase_request_products_data' in validate_data:
                for pr_product in validate_data['purchase_request_products_data']:
                    if 'warehouse_data' in pr_product:
                        warehouse_data = pr_product['warehouse_data']
                        self.check_lot_serial_exist(warehouse_data=warehouse_data, product_obj=validate_data['product'])
        return validate_data


class GoodsReceiptProductListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
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
            'warehouse',
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
            'is_additional',
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'description': obj.product.description,
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
            } if obj.uom.group else {},
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
    def get_warehouse(cls, obj):
        return {
            'id': obj.warehouse_id,
            'title': obj.warehouse.title,
            'code': obj.warehouse.code,
        } if obj.warehouse else {}

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


class GoodsReceiptDetailSerializer(serializers.ModelSerializer):
    purchase_requests = serializers.SerializerMethodField()
    goods_receipt_product = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'id',
            'title',
            'code',
            'goods_receipt_type',
            'purchase_order_data',
            'inventory_adjustment_data',
            'supplier_data',
            'purchase_requests',
            'remarks',
            'date_received',
            # line detail
            'goods_receipt_product',
            # system
            'system_status',
            'workflow_runtime_id',
            'is_active',
            'employee_inherit',
        )

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
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'phone': obj.employee_inherit.phone,
            'is_active': obj.employee_inherit.is_active,
        } if obj.employee_inherit else {}


class GoodsReceiptCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    purchase_order = serializers.UUIDField(required=False, allow_null=True)
    inventory_adjustment = serializers.UUIDField(required=False, allow_null=True)
    supplier = serializers.UUIDField(required=False, allow_null=True)
    purchase_requests = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    goods_receipt_product = GoodsReceiptProductSerializer(many=True, required=False)
    date_received = serializers.DateTimeField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'goods_receipt_type',
            'title',
            'purchase_order',
            'purchase_order_data',
            'inventory_adjustment',
            'inventory_adjustment_data',
            'supplier',
            'supplier_data',
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

    @decorator_run_workflow
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
    purchase_order = serializers.UUIDField(required=False, allow_null=True)
    inventory_adjustment = serializers.UUIDField(required=False, allow_null=True)
    supplier = serializers.UUIDField(required=False, allow_null=True)
    purchase_requests = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    goods_receipt_product = GoodsReceiptProductSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceipt
        fields = (
            'goods_receipt_type',
            'title',
            'purchase_order',
            'inventory_adjustment',
            'supplier',
            'supplier_data',
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

    @decorator_run_workflow
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
