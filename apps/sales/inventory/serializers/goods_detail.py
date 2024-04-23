from rest_framework import serializers

from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial
from apps.sales.inventory.models import GoodsReceipt


class GoodsDetailListSerializer(serializers.ModelSerializer):
    product_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'product_data',
        )

    @classmethod
    def get_product_data(cls, obj):
        return [{
            'goods_receipt': {
                'id': obj.id,
                'code': obj.code,
                'title': obj.title,
                'date_approved': obj.date_approved
            },
            'person_in_charge': {
                'id': obj.employee_inherit_id,
                'code': obj.employee_inherit.code,
                'full_name': obj.employee_inherit.get_full_name(2)
            } if obj.employee_inherit else {},
            'product': {
                'id': item.product_id,
                'code': item.product.code,
                'title': item.product.title,
                'type': item.product.general_traceability_method
            } if item.product else {},
            'warehouse': {
                'id': item.goods_receipt_warehouse_gr_product.first().warehouse_id,
                'code': item.goods_receipt_warehouse_gr_product.first().warehouse.code,
                'title': item.goods_receipt_warehouse_gr_product.first().warehouse.title
            } if item.goods_receipt_warehouse_gr_product.first() else {},
            'serial_list': [{
                'id': serial.id,
                'vendor_serial_number': serial.vendor_serial_number,
                'serial_number': serial.serial_number,
                'expire_date': serial.expire_date,
                'manufacture_date': serial.manufacture_date,
                'warranty_start': serial.warranty_start,
                'warranty_end': serial.warranty_end
            } for serial in item.goods_receipt_warehouse_gr_product.first().goods_receipt_serial_gr_warehouse.all(
            ).order_by('serial_number')],
            'lot_list': [{
                'id': lot.id,
                'lot_number': lot.lot_number,
                'quantity_import': lot.quantity_import,
                'expire_date': lot.expire_date,
                'manufacture_date': lot.manufacture_date,
            } for lot in item.goods_receipt_warehouse_gr_product.first().goods_receipt_lot_gr_warehouse.all(
            ).order_by('lot_number')],
            'quantity_import': item.quantity_import
        } for item in obj.goods_receipt_product_goods_receipt.all()]


class GoodsDetailDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ()

    def create(self, validated_data):
        product_id = self.initial_data.get('product_id')
        warehouse_id = self.initial_data.get('warehouse_id')
        goods_receipt_id = self.initial_data.get('goods_receipt_id')
        prd_wh = ProductWareHouse.objects.filter(
            product_id=product_id,
            warehouse_id=warehouse_id,
            goods_receipt_id=goods_receipt_id
        ).first()
        if prd_wh:
            all_serial = prd_wh.product_warehouse_serial_product_warehouse.all()
            for item in self.initial_data.get('serial_data'):
                serial_id = item.get('serial_id')
                if serial_id:
                    serial = all_serial.filter(id=serial_id).first()
                    if serial:
                        serial.vendor_serial_number = item.get('vendor_serial_number')
                        serial.serial_number = item.get('serial_number')
                        serial.expire_date = item.get('expire_date')
                        serial.manufacture_date = item.get('manufacture_date')
                        serial.warranty_start = item.get('warranty_start')
                        serial.warranty_end = item.get('warranty_end')
                        serial.save()
                    else:
                        raise serializers.ValidationError({"Serial": 'Serial is not exist.'})
                else:
                    ProductWareHouseSerial.objects.create(product_warehouse=prd_wh, **item)
        return prd_wh


class GoodsDetailDataDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ('id',)
