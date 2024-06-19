from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import WareHouse
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.inventory.models import GoodsReturn, GoodsReturnAttachmentFile, GoodsReturnProductDetail
from apps.sales.saleorder.models import SaleOrder
from apps.shared import SaleMsg, SYSTEM_STATUS, AbstractDetailSerializerModel


class GoodsReturnListSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    delivery = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    raw_system_status = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReturn
        fields = (
            'id',
            'title',
            'code',
            'sale_order',
            'note',
            'delivery',
            'system_status',
            'raw_system_status',
            'date_created'
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'code': obj.sale_order.code,
            'title': obj.sale_order.title,
            'sale_person': {
                'id': obj.sale_order.employee_inherit_id,
                'code': obj.sale_order.employee_inherit.code,
                'fullname': obj.sale_order.employee_inherit.get_full_name(2),
            } if obj.sale_order.employee_inherit else {},
            'customer': {
                'id': obj.sale_order.customer_id,
                'code': obj.sale_order.customer.code,
                'name': obj.sale_order.customer.name,
            } if obj.sale_order.employee_inherit else {}
        } if obj.sale_order else {}

    @classmethod
    def get_delivery(cls, obj):
        return {
            'id': obj.delivery_id,
            'code': obj.delivery.code
        } if obj.delivery_id else {}

    @classmethod
    def get_system_status(cls, obj):
        return _(str(dict(SYSTEM_STATUS).get(obj.system_status)))

    @classmethod
    def get_raw_system_status(cls, obj):
        return obj.system_status


def create_files_mapped(gr_obj, file_id_list):
    try:
        bulk_data_file = []
        for index, file_id in enumerate(file_id_list):
            bulk_data_file.append(GoodsReturnAttachmentFile(
                goods_return=gr_obj,
                attachment_id=file_id,
                order=index
            ))
        GoodsReturnAttachmentFile.objects.filter(goods_return=gr_obj).delete()
        GoodsReturnAttachmentFile.objects.bulk_create(bulk_data_file)
        return True
    except Exception as err:
        raise serializers.ValidationError({'files': SaleMsg.SAVE_FILES_ERROR + f' {err}'})


def create_item_mapped(goods_return):
    bulk_info = []
    for item in goods_return.product_detail_list:
        div = goods_return.company.company_config.definition_inventory_valuation
        if not item.get('cost_for_periodic') and div == 1:
            raise serializers.ValidationError({"cost": 'Cost for periodic in not NULL.'})
        data_type = item.get('type')
        default_return_number = 0
        default_redelivery_number = 0
        lot_return_number = 0
        lot_redelivery_number = 0
        is_return = False
        is_redelivery = False
        if data_type == 0:
            default_return_number = float(item.get('is_return', 0))
            default_redelivery_number = float(item.get('is_redelivery', 0))
            lot_return_number = 0
            lot_redelivery_number = 0
            is_return = False
            is_redelivery = False
        elif data_type == 1:
            default_return_number = 0
            default_redelivery_number = 0
            lot_return_number = float(item.get('is_return', 0))
            lot_redelivery_number = float(item.get('is_redelivery', 0))
            is_return = False
            is_redelivery = False
        elif data_type == 2:
            default_return_number = 0
            default_redelivery_number = 0
            lot_return_number = 0
            lot_redelivery_number = 0
            is_return = item.get('is_return', False)
            is_redelivery = item.get('is_redelivery', False)

        if all([
            item.get('return_to_warehouse_id'),
            item.get('delivery_item_id'),
            item.get('product_id'),
            item.get('uom_id')
        ]):
            bulk_info.append(
                GoodsReturnProductDetail.objects.create(
                    goods_return=goods_return,
                    type=data_type,
                    product_id=item.get('product_id'),
                    uom_id=item.get('uom_id'),
                    return_to_warehouse_id=item.get('return_to_warehouse_id'),
                    delivery_item_id=item.get('delivery_item_id'),
                    # none
                    default_return_number=default_return_number,
                    default_redelivery_number=default_redelivery_number,
                    # lot
                    lot_no_id=item.get('lot_id'),
                    lot_return_number=lot_return_number,
                    lot_redelivery_number=lot_redelivery_number,
                    # sn
                    serial_no_id=item.get('serial_id'),
                    is_return=is_return,
                    is_redelivery=is_redelivery
                )
            )
        else:
            raise serializers.ValidationError({"error": 'Row is missing data.'})
    GoodsReturnProductDetail.objects.filter(goods_return=goods_return).delete()
    GoodsReturnProductDetail.objects.bulk_create(bulk_info)
    return True


class GoodsReturnCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = GoodsReturn
        fields = (
            'title',
            'code',
            'sale_order',
            'note',
            'delivery',
            'system_status',
            'product_detail_list',
            'data_line_detail_table'
        )

    @decorator_run_workflow
    def create(self, validated_data):
        goods_return = GoodsReturn.objects.create(**validated_data)

        create_item_mapped(goods_return)
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(goods_return, attachment.strip().split(','))

        return goods_return


class GoodsReturnDetailSerializer(AbstractDetailSerializerModel):
    sale_order = serializers.SerializerMethodField()
    delivery = serializers.SerializerMethodField()
    data_line_detail_table = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReturn
        fields = (
            'id',
            'title',
            'code',
            'sale_order',
            'note',
            'delivery',
            'system_status',
            'date_created',
            'product_detail_list',
            'data_line_detail_table',
            'attachment'
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'code': obj.sale_order.code,
            'title': obj.sale_order.title,
            'customer_name': obj.sale_order.customer.name if obj.sale_order.customer else ''
        } if obj.sale_order else {}

    @classmethod
    def get_delivery(cls, obj):
        return {
            'id': obj.delivery_id,
            'code': obj.delivery.code
        } if obj.delivery_id else {}

    @classmethod
    def get_data_line_detail_table(cls, obj):
        for row in obj.data_line_detail_table:
            warehouse = WareHouse.objects.filter(id=row['return_to_warehouse_id']).first()
            if warehouse:
                row['return_to_warehouse'] = {
                    'id': str(warehouse.id),
                    'code': warehouse.code,
                    'title': warehouse.title
                }
        return obj.data_line_detail_table

    @classmethod
    def get_attachment(cls, obj):
        att_objs = GoodsReturnAttachmentFile.objects.select_related('attachment').filter(goods_return=obj)
        return [item.attachment.get_detail() for item in att_objs]


class GoodsReturnUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsReturn
        fields = (
            'title',
            'code',
            'sale_order',
            'note',
            'delivery',
            'system_status',
            'product_detail_list',
            'data_line_detail_table'
        )

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        create_item_mapped(instance)
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(instance, attachment.strip().split(','))
        return instance


class SaleOrderListSerializerForGoodsReturn(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'sale_person',
            'date_created',
            'system_status',
            'delivery_status',
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_sale_person(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'is_active': obj.employee_inherit.is_active,
        } if obj.employee_inherit else {}


class DeliveryListSerializerForGoodsReturn(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = OrderDeliverySub
        fields = (
            'id',
            'title',
            'code',
            'sale_order_data',
            'delivery_quantity',
            'state',
            'is_active',
            'times',
            'details',
            'date'
        )

    @classmethod
    def get_details(cls, obj):
        return [{
            'id': item.id,
            'product_data': {
                'id': item.product_id,
                'code': item.product.code,
                'title': item.product.title,
            } if item.product else {},
            'uom_data': item.uom_data,
            'total_order': item.delivery_quantity,
            'delivered_quantity': item.picked_quantity,
            'product_unit_price': item.product_unit_price,
            'product_subtotal_price': item.product_subtotal_price,
            'product_general_traceability_method': item.product.general_traceability_method,
            'returned_quantity_default': item.returned_quantity_default,
            'sn_data': [{
                'id': serial.id,
                'product': serial.delivery_product.product_data,
                'uom': serial.delivery_product.uom_data,
                'product_unit_price': serial.delivery_product.product_unit_price,
                'product_subtotal_price': serial.delivery_product.product_subtotal_price,
                'serial_id': serial.product_warehouse_serial_id,
                'vendor_serial_number': serial.product_warehouse_serial.vendor_serial_number,
                'serial_number': serial.product_warehouse_serial.serial_number,
                'is_returned': serial.is_returned
            } for serial in item.delivery_serial_delivery_product.all()],
            'lot_data': [{
                'id': lot.id,
                'product': lot.delivery_product.product_data,
                'uom': lot.delivery_product.uom_data,
                'product_unit_price': lot.delivery_product.product_unit_price,
                'lot_id': lot.product_warehouse_lot_id,
                'lot_number': lot.product_warehouse_lot.lot_number,
                'quantity_delivery': lot.quantity_delivery,
                'returned_quantity': lot.returned_quantity
            } for lot in item.delivery_lot_delivery_product.all()]
        } for item in obj.delivery_product_delivery_sub.all().select_related('product')]

    @classmethod
    def get_date(cls, obj):
        return obj.order_delivery.date_created
