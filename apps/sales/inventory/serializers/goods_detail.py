from rest_framework import serializers
from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial, ProductWareHouseLot
from apps.masterdata.saledata.models.product_warehouse import ProductWareHouseLotTransaction
from apps.sales.inventory.models import GoodsReceipt
from apps.sales.report.models import ReportInventorySub, ReportInventory


class GoodsDetailListSerializer(serializers.ModelSerializer):
    product_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'product_data',
        )

    @classmethod
    def get_product_data(cls, obj):
        lots_import = obj.goods_receipt_lot_goods_receipt.all()
        product_data = []
        for item in obj.goods_receipt_product_goods_receipt.all():
            for gr_wh_gr_prd in item.goods_receipt_warehouse_gr_product.all():
                serial_data = []
                for serial in obj.product_wh_serial_goods_receipt.filter(
                    product_warehouse__product_id=item.product_id,
                    product_warehouse__warehouse_id=gr_wh_gr_prd.warehouse_id
                ).order_by('vendor_serial_number', 'serial_number'):
                    serial_data.append({
                        'id': serial.id,
                        'vendor_serial_number': serial.vendor_serial_number,
                        'serial_number': serial.serial_number,
                        'expire_date': serial.expire_date,
                        'manufacture_date': serial.manufacture_date,
                        'warranty_start': serial.warranty_start,
                        'warranty_end': serial.warranty_end,
                        'is_delete': serial.is_delete
                    })
                sum_serial_quantity = len(serial_data)

                lot_data = []
                sum_lot_quantity = 0
                for lot_trans in obj.pw_lot_transact_goods_receipt.filter(
                    pw_lot__product_warehouse__product_id=item.product_id,
                    pw_lot__product_warehouse__warehouse_id=gr_wh_gr_prd.warehouse_id
                ).order_by('pw_lot__lot_number'):
                    lot = lot_trans.pw_lot
                    lot_quantity_import = lots_import.filter(lot_number=lot.lot_number).first()
                    if lot_quantity_import:
                        sum_lot_quantity += lot_quantity_import.quantity_import
                        lot_data.append({
                            'id': lot.id,
                            'lot_number': lot.lot_number,
                            'quantity_import': lot.quantity_import,
                            'expire_date': lot.expire_date,
                            'manufacture_date': lot.manufacture_date,
                        })

                status = 0
                if item.product.general_traceability_method == 0:
                    status = 1
                if item.product.general_traceability_method == 1 and sum_lot_quantity == item.quantity_import:
                    status = 1
                if item.product.general_traceability_method == 2 and sum_serial_quantity == item.quantity_import:
                    status = 1

                product_data.append({
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
                        'category': item.product.general_product_category_id,
                        'type': item.product.general_traceability_method
                    } if item.product else {},
                    'warehouse': {
                        'id': gr_wh_gr_prd.warehouse_id,
                        'code': gr_wh_gr_prd.warehouse.code,
                        'title': gr_wh_gr_prd.warehouse.title
                    } if gr_wh_gr_prd else {},
                    'serial_list': serial_data,
                    'lot_list': lot_data,
                    'quantity_import': gr_wh_gr_prd.quantity_import,
                    'status': status
                })
        return product_data


class GoodsDetailDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ()

    @classmethod
    def update_serial(cls, item, all_serial, serial_id, goods_receipt_id):
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
                return serial
            raise serializers.ValidationError({'Serial': f"Serial {item.get('serial_number')} is existed"})
        raise serializers.ValidationError({'Serial': f"Serial id {serial_id} is not existed"})

    @classmethod
    def create_serial(cls, item, prd_wh, goods_receipt_id):
        del item['serial_id']
        if item.get('vendor_serial_number') and item.get('serial_number'):
            if not ProductWareHouseSerial.objects.filter(
                    serial_number=item.get('serial_number')
            ).exists():
                new_serial = ProductWareHouseSerial.objects.create(
                    **item,
                    product_warehouse=prd_wh,
                    goods_receipt_id=goods_receipt_id,
                    company_id=prd_wh.company_id,
                    tenant_id=prd_wh.tenant_id
                )
                return new_serial
        raise serializers.ValidationError({'Serial': "Can not create new serial."})

    @classmethod
    def for_serial(cls, serial_data, prd_wh, goods_receipt_id):
        all_serial = prd_wh.product_warehouse_serial_product_warehouse.all()
        amount_create = 0
        for item in serial_data:
            serial_id = item.get('serial_id')
            if serial_id:
                cls.update_serial(item, all_serial, serial_id, goods_receipt_id)
            else:
                amount_create += 1
                cls.create_serial(item, prd_wh, goods_receipt_id)
        if amount_create > 0:
            prd_wh.receipt_amount += amount_create
            prd_wh.stock_amount = prd_wh.receipt_amount - prd_wh.sold_amount
            prd_wh.save(update_fields=['receipt_amount', 'stock_amount'])
            prd_wh.product.stock_amount += amount_create
            prd_wh.product.save(update_fields=['stock_amount'])
        return True

    def create(self, validated_data):
        product_id = self.initial_data.get('product_id')
        warehouse_id = self.initial_data.get('warehouse_id')
        goods_receipt_id = self.initial_data.get('goods_receipt_id')
        prd_wh = ProductWareHouse.objects.filter(product_id=product_id, warehouse_id=warehouse_id).first()
        if prd_wh:
            if self.initial_data.get('is_serial_update'):
                self.for_serial(self.initial_data.get('serial_data'), prd_wh, goods_receipt_id)
            return prd_wh
        raise serializers.ValidationError({'Product Warehouse': "ProductWareHouse object is not exist"})


class GoodsDetailDataDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ('id',)
