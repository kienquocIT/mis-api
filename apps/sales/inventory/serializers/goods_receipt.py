from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models.product_warehouse import ProductWareHouseSerial, ProductWareHouseLot
from apps.sales.inventory.models import GoodsReceipt, GoodsReceiptProduct, GoodsReceiptRequestProduct, \
    GoodsReceiptWarehouse, GoodsReceiptLot, GoodsReceiptSerial, GoodsReceiptAttachment
from apps.sales.inventory.serializers.goods_receipt_sub import GoodsReceiptCommonValidate, GoodsReceiptCommonCreate
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel, HRMsg
from apps.shared.translations.base import AttachmentMsg


class GoodsReceiptSerialSerializer(serializers.ModelSerializer):
    serial_number = serializers.CharField(max_length=100, required=False, allow_blank=False)
    expire_date = serializers.CharField(required=False, allow_null=True)
    manufacture_date = serializers.CharField(required=False, allow_null=True)
    warranty_start = serializers.CharField(required=False, allow_null=True)
    warranty_end = serializers.CharField(required=False, allow_null=True)

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
    lot_id = serializers.UUIDField(required=False, allow_null=True)
    expire_date = serializers.CharField(required=False, allow_null=True)
    manufacture_date = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = GoodsReceiptLot
        fields = (
            'lot_id',
            'lot_number',
            'quantity_import',
            'expire_date',
            'manufacture_date',
        )

    @classmethod
    def validate_lot_id(cls, value):
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
    warehouse_id = serializers.UUIDField()
    lot_data = GoodsReceiptLotSerializer(many=True, required=False)
    serial_data = GoodsReceiptSerialSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptWarehouse
        fields = (
            'warehouse_id',
            'warehouse_data',
            'quantity_import',
            'lot_data',
            'serial_data',
            'is_additional',
        )

    @classmethod
    def validate_warehouse_id(cls, value):
        return GoodsReceiptCommonValidate.validate_warehouse_id(value=value)


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
    purchase_order_request_product_id = serializers.UUIDField(required=False, allow_null=True)
    purchase_request_product_id = serializers.UUIDField(required=False, allow_null=True)
    production_report_id = serializers.UUIDField(required=False, allow_null=True)
    gr_warehouse_data = GoodsReceiptWarehouseSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptRequestProduct
        fields = (
            'purchase_order_request_product_id',
            'purchase_request_product_id',
            'purchase_request_data',
            'production_report_id',
            'production_report_data',
            'uom_data',
            'quantity_order',
            'quantity_import',
            'is_stock',
            'gr_warehouse_data',
        )

    @classmethod
    def validate_purchase_order_request_product_id(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_order_request_product_id(value=value)

    @classmethod
    def validate_purchase_request_product_id(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_request_product_id(value=value)

    @classmethod
    def validate_production_report_id(cls, value):
        return GoodsReceiptCommonValidate.validate_production_report_id(value=value)


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
    purchase_order_product_id = serializers.UUIDField(required=False, allow_null=True)
    production_order_id = serializers.UUIDField(required=False, allow_null=True)
    ia_item_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField()
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    tax_id = serializers.UUIDField(required=False, allow_null=True)
    product_unit_price = serializers.FloatField()
    quantity_import = serializers.FloatField()
    pr_products_data = GoodsReceiptRequestProductSerializer(many=True, required=False)
    gr_warehouse_data = GoodsReceiptWarehouseSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptProduct
        fields = (
            'purchase_order_product_id',
            'ia_item_id',
            'production_order_id',
            'product_id',
            'product_data',
            'uom_id',
            'uom_data',
            'tax_id',
            'tax_data',
            'product_quantity_order_actual',
            'quantity_import',
            'product_title',
            'product_code',
            'product_description',
            'product_unit_price',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
            'pr_products_data',
            'gr_warehouse_data',
            'is_additional',
        )

    @classmethod
    def validate_purchase_order_product_id(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_order_product_id(value=value)

    @classmethod
    def validate_ia_item_id(cls, value):
        return GoodsReceiptCommonValidate.validate_ia_item_id(value=value)

    @classmethod
    def validate_production_order_id(cls, value):
        return GoodsReceiptCommonValidate.validate_production_order_id(value=value)

    @classmethod
    def validate_product_id(cls, value):
        return GoodsReceiptCommonValidate.validate_product_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return GoodsReceiptCommonValidate.validate_uom_id(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return GoodsReceiptCommonValidate.validate_tax_id(value=value)

    @classmethod
    def validate_quantity_import(cls, value):
        return GoodsReceiptCommonValidate.validate_quantity_import(value=value)

    @classmethod
    def validate_product_unit_price(cls, value):
        return GoodsReceiptCommonValidate().validate_price(value=value)

    @classmethod
    def check_lot_serial_exist(cls, gr_warehouse_data, product_id):
        serial_number_list = []
        for gr_wh_data in gr_warehouse_data:
            lot_number_list = []
            for lot in gr_wh_data.get('lot_data', []):
                lot_id = lot.get('lot_id', None)
                if not lot_id:
                    lot_number_list.append(lot.get('lot_number', None))
            # check lot
            cls.check_lot_exist(
                product_id=product_id,
                warehouse_id=gr_wh_data.get('warehouse_id', None),
                lot_number_list=lot_number_list
            )
            for serial in gr_wh_data.get('serial_data', []):
                serial_number_list.append(serial.get('serial_number', None))
        # check serial
        cls.check_serial_exist(product_id=product_id, serial_number_list=serial_number_list)
        return True

    @classmethod
    def check_lot_exist(cls, product_id, warehouse_id, lot_number_list):
        # check unique in data submit (in same warehouse)
        if len(lot_number_list) != len(set(lot_number_list)):
            raise serializers.ValidationError({'lot_number': 'Lot number must be different.'})
        # check unique in db
        if product_id and warehouse_id:
            for product_wh_lot in ProductWareHouseLot.objects.filter(
                    lot_number__in=lot_number_list
            ):
                if product_wh_lot.product_warehouse:
                    pwh = product_wh_lot.product_warehouse
                    if pwh.product_id == product_id and pwh.warehouse_id == warehouse_id:
                        raise serializers.ValidationError({'lot_number': 'Lot number is exist.'})
                    if pwh.product_id != product_id:
                        raise serializers.ValidationError({'lot_number': 'Lot number is exist.'})
        return True

    @classmethod
    def check_serial_exist(cls, product_id, serial_number_list):
        # check unique in data submit
        if len(serial_number_list) != len(set(serial_number_list)):
            raise serializers.ValidationError({'serial_number': 'Serial number must be different.'})
        # check unique in db
        if ProductWareHouseSerial.objects.filter(
                product_warehouse__product_id=product_id,
                serial_number__in=serial_number_list
        ).exists():
            raise serializers.ValidationError({'serial_number': 'Serial number is exist.'})
        return True

    def validate(self, validate_data):
        self.check_lot_serial_exist(
            gr_warehouse_data=validate_data.get('gr_warehouse_data', []),
            product_id=validate_data.get('product_id', None)
        )
        for pr_product in validate_data.get('pr_products_data', []):
            if 'gr_warehouse_data' in pr_product:
                self.check_lot_serial_exist(
                    gr_warehouse_data=pr_product.get('gr_warehouse_data', []),
                    product_id=validate_data.get('product_id', None)
                )
        return validate_data


class GoodsReceiptProductListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    pr_products_data = serializers.SerializerMethodField()
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
            'pr_products_data',
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
    def get_pr_products_data(cls, obj):
        return GoodsReceiptRequestProductListSerializer(
            obj.goods_receipt_request_product_gr_product.all(),
            many=True
        ).data

    @classmethod
    def get_warehouse_data(cls, obj):
        return GoodsReceiptWarehouseListSerializer(obj.goods_receipt_warehouse_gr_product.all(), many=True).data


# GOODS RECEIPT BEGIN
def handle_attach_file(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.filter(id="dd16a86c-4aef-46ec-9302-19f30b101cf5").first()
        if relate_app:
            state = GoodsReceiptAttachment.resolve_change(
                result=attachment_result, doc_id=instance.id, doc_app=relate_app,
            )
            if state:
                return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


class GoodsReceiptListSerializer(AbstractListSerializerModel):

    class Meta:
        model = GoodsReceipt
        fields = (
            'id',
            'title',
            'code',
            'goods_receipt_type',
            'purchase_order_data',
            'inventory_adjustment_data',
            'production_order_data',
            'date_received',
            'system_status',
        )


class GoodsReceiptDetailSerializer(AbstractDetailSerializerModel):
    purchase_requests = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'id',
            'title',
            'code',
            'goods_receipt_type',
            'purchase_order_data',
            'inventory_adjustment_data',
            'production_order_data',
            'supplier_data',
            'purchase_requests',
            'production_reports_data',
            'remarks',
            'date_received',
            # line detail
            'gr_products_data',
            # system
            'system_status',
            'workflow_runtime_id',
            'is_active',
            'employee_inherit',
            # attachment
            'attachment',
        )

    @classmethod
    def get_purchase_requests(cls, obj):
        return [
            {'id': purchase_request.id, 'title': purchase_request.title, 'code': purchase_request.code}
            for purchase_request in obj.purchase_requests.all()
        ]

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

    @classmethod
    def get_attachment(cls, obj):
        return [file_obj.get_detail() for file_obj in obj.attachment_m2m.all()]


class GoodsReceiptCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField()
    purchase_order_id = serializers.UUIDField(required=False, allow_null=True)
    inventory_adjustment_id = serializers.UUIDField(required=False, allow_null=True)
    production_order_id = serializers.UUIDField(required=False, allow_null=True)
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    purchase_requests = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    gr_products_data = GoodsReceiptProductSerializer(many=True, required=False)
    date_received = serializers.DateTimeField()
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = GoodsReceipt
        fields = (
            'goods_receipt_type',
            'title',
            'purchase_order_id',
            'purchase_order_data',
            'inventory_adjustment_id',
            'inventory_adjustment_data',
            'production_order_id',
            'production_order_data',
            'supplier_id',
            'supplier_data',
            'purchase_requests',
            'production_reports_data',
            'remarks',
            'date_received',
            # tab product
            'gr_products_data',
            # attachment
            'attachment',
        )

    @classmethod
    def validate_purchase_order_id(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_order_id(value=value)

    @classmethod
    def validate_inventory_adjustment_id(cls, value):
        return GoodsReceiptCommonValidate.validate_inventory_adjustment_id(value=value)

    @classmethod
    def validate_production_order_id(cls, value):
        return GoodsReceiptCommonValidate.validate_production_order_id(value=value)

    @classmethod
    def validate_supplier_id(cls, value):
        return GoodsReceiptCommonValidate.validate_supplier_id(value=value)

    @classmethod
    def validate_purchase_requests(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_requests(value=value)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = GoodsReceiptAttachment.valid_change(
                current_ids=value, employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        purchase_requests = validated_data.pop('purchase_requests', [])
        goods_receipt = GoodsReceipt.objects.create(**validated_data)
        # create sub models
        GoodsReceiptCommonCreate.create_goods_receipt_sub_models(
            purchase_requests=purchase_requests,
            goods_receipt_product=goods_receipt.gr_products_data,
            instance=goods_receipt,
            is_update=False
        )
        handle_attach_file(goods_receipt, attachment)
        return goods_receipt


class GoodsReceiptUpdateSerializer(AbstractCreateSerializerModel):
    purchase_order_id = serializers.UUIDField(required=False, allow_null=True)
    inventory_adjustment_id = serializers.UUIDField(required=False, allow_null=True)
    production_order_id = serializers.UUIDField(required=False, allow_null=True)
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    purchase_requests = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    gr_products_data = GoodsReceiptProductSerializer(many=True, required=False)
    date_received = serializers.DateTimeField(required=False, allow_null=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = GoodsReceipt
        fields = (
            'goods_receipt_type',
            'title',
            'purchase_order_id',
            'purchase_order_data',
            'inventory_adjustment_id',
            'inventory_adjustment_data',
            'production_order_id',
            'production_order_data',
            'supplier_id',
            'supplier_data',
            'purchase_requests',
            'production_reports_data',
            'remarks',
            'date_received',
            # tab product
            'gr_products_data',
            # attachment
            'attachment',
        )

    @classmethod
    def validate_purchase_order_id(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_order_id(value=value)

    @classmethod
    def validate_inventory_adjustment_id(cls, value):
        return GoodsReceiptCommonValidate.validate_inventory_adjustment_id(value=value)

    @classmethod
    def validate_production_order_id(cls, value):
        return GoodsReceiptCommonValidate.validate_production_order_id(value=value)

    @classmethod
    def validate_supplier_id(cls, value):
        return GoodsReceiptCommonValidate.validate_supplier_id(value=value)

    @classmethod
    def validate_purchase_requests(cls, value):
        return GoodsReceiptCommonValidate.validate_purchase_requests(value=value)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = GoodsReceiptAttachment.valid_change(
                current_ids=value, employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        purchase_requests = validated_data.pop('purchase_requests', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # create sub models
        GoodsReceiptCommonCreate.create_goods_receipt_sub_models(
            purchase_requests=purchase_requests,
            goods_receipt_product=instance.gr_products_data,
            instance=instance,
            is_update=True
        )
        handle_attach_file(instance, attachment)
        return instance
