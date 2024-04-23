from rest_framework import serializers

from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial, ProductWareHouseLot
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
                'category': item.product.general_product_category,
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
                'warranty_end': serial.warranty_end,
                'is_delete': serial.is_delete
            } for serial in obj.product_wh_serial_goods_receipt.all().order_by('serial_number')],
            'lot_list': [{
                'id': lot.id,
                'lot_number': lot.lot_number,
                'quantity_import': lot.quantity_import,
                'expire_date': lot.expire_date,
                'manufacture_date': lot.manufacture_date,
            } for lot in obj.product_wh_lot_goods_receipt.all().order_by('lot_number')],
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
        prd_wh = ProductWareHouse.objects.filter(product_id=product_id, warehouse_id=warehouse_id).first()
        if prd_wh:
            if self.initial_data.get('is_serial_update'):
                all_serial = prd_wh.product_warehouse_serial_product_warehouse.all()
                for item in self.initial_data.get('serial_data'):
                    serial_id = item.get('serial_id')
                    if serial_id:
                        serial = all_serial.filter(id=serial_id, is_delete=False).first()
                        if serial:
                            if not ProductWareHouseSerial.objects.filter(
                                serial_number=item.get('serial_number')
                            ).exclude(id=serial_id).exists():
                                serial.vendor_serial_number = item.get('vendor_serial_number')
                                serial.serial_number = item.get('serial_number')
                                serial.expire_date = item.get('expire_date')
                                serial.manufacture_date = item.get('manufacture_date')
                                serial.warranty_start = item.get('warranty_start')
                                serial.warranty_end = item.get('warranty_end')
                                serial.goods_receipt_id = goods_receipt_id
                                serial.save()
                            else:
                                raise serializers.ValidationError(
                                    {'Serial': f"'Serial {item.get('serial_number')} is existed"}
                                )
                    else:
                        del item['serial_id']
                        if item.get('vendor_serial_number') and item.get('serial_number'):
                            if not ProductWareHouseSerial.objects.filter(serial_number=item.get('serial_number')).exists():
                                ProductWareHouseSerial.objects.create(
                                    **item,
                                    product_warehouse=prd_wh,
                                    goods_receipt_id=goods_receipt_id,
                                    company_id=prd_wh.company_id,
                                    tenant_id=prd_wh.tenant_id
                                )
                            else:
                                raise serializers.ValidationError(
                                    {'Serial': f"'Serial {item.get('serial_number')} is existed"}
                                )
            else:
                # check quantity_import
                gr_quantity_import = float(self.initial_data.get('gr_quantity_import'))
                sum_quantity_import = 0
                for item in self.initial_data.get('lot_data'):
                    sum_quantity_import += float(item.get('quantity_import'))
                if sum_quantity_import > gr_quantity_import:
                    raise serializers.ValidationError({'Lot quantity': f"'Sum lot quantity > receipt quantity"})

                all_lot = prd_wh.product_warehouse_lot_product_warehouse.all()
                for item in self.initial_data.get('lot_data'):
                    lot_id = item.get('lot_id')
                    if lot_id:
                        lot = all_lot.filter(id=lot_id).first()
                        if lot:
                            if not ProductWareHouseLot.objects.filter(
                                lot_number=item.get('lot_number')
                            ).exclude(id=lot_id).exists():
                                lot.lot_number = item.get('lot_number')
                                lot.expire_date = item.get('expire_date')
                                lot.manufacture_date = item.get('manufacture_date')
                                lot.goods_receipt_id = goods_receipt_id
                                lot.save()
                            else:
                                raise serializers.ValidationError(
                                    {'Lot': f"'Lot {item.get('lot_number')} is existed"}
                                )
                    else:
                        del item['lot_id']
                        if item.get('lot_number') and item.get('quantity_import'):
                            if not ProductWareHouseLot.objects.filter(lot_number=item.get('lot_number')).exists():
                                ProductWareHouseLot.objects.create(
                                    **item,
                                    product_warehouse=prd_wh,
                                    goods_receipt_id=goods_receipt_id,
                                    company_id=prd_wh.company_id,
                                    tenant_id=prd_wh.tenant_id
                                )
                            else:
                                raise serializers.ValidationError(
                                    {'Lot': f"'Lot {item.get('lot_number')} is existed"}
                                )
        return prd_wh


class GoodsDetailDataDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ('id',)
