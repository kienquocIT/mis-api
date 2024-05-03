from rest_framework import serializers
from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial, ProductWareHouseLot
from apps.sales.inventory.models import GoodsReceipt
from apps.sales.report.models import ReportInventorySub


class GoodsDetailListSerializer(serializers.ModelSerializer):
    product_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'product_data',
        )

    @classmethod
    def get_product_data(cls, obj):
        product_data = []
        for item in obj.goods_receipt_product_goods_receipt.all():
            gr_wh_gr_prd = item.goods_receipt_warehouse_gr_product.first()
            serial_data = []
            for serial in obj.product_wh_serial_goods_receipt.all().order_by('vendor_serial_number', 'serial_number'):
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
            for lot in obj.product_wh_lot_goods_receipt.all().order_by('lot_number'):
                sum_lot_quantity += lot.raw_quantity_import
                lot_data.append({
                    'id': lot.id,
                    'lot_number': lot.lot_number,
                    'raw_quantity_import': lot.raw_quantity_import,
                    'quantity_import': lot.quantity_import,
                    'expire_date': lot.expire_date,
                    'manufacture_date': lot.manufacture_date,
                })

            status = 0
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
                'quantity_import': item.quantity_import,
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

    @classmethod
    def check_lot_quantity(cls, gr_quantity_import, lot_data):
        # check quantity_import
        gr_quantity_import = float(gr_quantity_import)
        sum_quantity_import = 0
        for item in lot_data:
            sum_quantity_import += float(item.get('quantity_import'))
        if sum_quantity_import > gr_quantity_import:
            raise serializers.ValidationError({'Lot quantity': "Sum lot quantity > receipt quantity"})
        return True

    @classmethod
    def update_lot(cls, item, all_lot, lot_id, goods_receipt_id):
        lot = all_lot.filter(id=lot_id).first()
        if lot:
            if not ProductWareHouseLot.objects.filter(lot_number=item.get('lot_number')).exclude(id=lot_id).exists():
                lot.lot_number = item.get('lot_number')
                lot.expire_date = item.get('expire_date')
                lot.manufacture_date = item.get('manufacture_date')
                lot.goods_receipt_id = goods_receipt_id
                lot.save()
                return lot
            raise serializers.ValidationError({'Lot': f"Lot {item.get('lot_number')} is existed"})
        raise serializers.ValidationError({'Lot': f"Lot {lot_id} is not existed"})

    @classmethod
    def create_lot(cls, item, prd_wh, goods_receipt_id):
        del item['lot_id']
        if item.get('lot_number') and item.get('quantity_import'):
            lot_else = ProductWareHouseLot.objects.filter(lot_number=item.get('lot_number'))
            if not lot_else.exists():
                new_lot = ProductWareHouseLot.objects.create(
                    **item,
                    raw_quantity_import=item.get('quantity_import', 0),
                    product_warehouse=prd_wh,
                    goods_receipt_id=goods_receipt_id,
                    company_id=prd_wh.company_id,
                    tenant_id=prd_wh.tenant_id
                )
                return new_lot
        raise serializers.ValidationError({'Lot': "Can not create new lot."})

    @classmethod
    def for_lot(cls, lot_data, prd_wh, goods_receipt_id):
        all_lot = prd_wh.product_warehouse_lot_product_warehouse.all()
        amount_create = 0
        lot_data_updated = []
        for item in lot_data:
            lot_id = item.get('lot_id')
            if lot_id:
                lot = cls.update_lot(item, all_lot, lot_id, goods_receipt_id)
            else:
                amount_create += float(item.get('quantity_import'))
                lot = cls.create_lot(item, prd_wh, goods_receipt_id)
            lot_data_updated.append({
                'lot_id': str(lot.id),
                'lot_number': lot.lot_number,
                'lot_quantity': lot.raw_quantity_import if lot.raw_quantity_import != 0 else lot.quantity_import,
                'lot_value': 0,
                'lot_expire_date': str(lot.expire_date)
            })
        if amount_create > 0:
            prd_wh.receipt_amount += amount_create
            prd_wh.stock_amount = prd_wh.receipt_amount - prd_wh.sold_amount
            prd_wh.save(update_fields=['receipt_amount', 'stock_amount'])
            prd_wh.product.stock_amount += amount_create
            prd_wh.product.save(update_fields=['stock_amount'])
        return lot_data_updated

    @classmethod
    def update_sub_report(cls, goods_receipt_id, product_id, warehouse_id, lot_data):
        sub = ReportInventorySub.objects.filter(
            product_id=product_id, warehouse_id=warehouse_id, trans_id=goods_receipt_id
        ).first()
        if sub:
            for lot in lot_data:
                lot['lot_value'] = float(lot['lot_quantity']) * sub.cost
            sub.lot_data = lot_data
            sub.save(update_fields=['lot_data'])
            return True
        raise serializers.ValidationError({'Sub report': "Can not update."})

    def create(self, validated_data):
        product_id = self.initial_data.get('product_id')
        warehouse_id = self.initial_data.get('warehouse_id')
        goods_receipt_id = self.initial_data.get('goods_receipt_id')
        prd_wh = ProductWareHouse.objects.filter(product_id=product_id, warehouse_id=warehouse_id).first()
        if prd_wh:
            if self.initial_data.get('is_serial_update'):
                self.for_serial(self.initial_data.get('serial_data'), prd_wh, goods_receipt_id)
            else:
                self.check_lot_quantity(self.initial_data.get('gr_quantity_import'), self.initial_data.get('lot_data'))
                lot_data = self.for_lot(self.initial_data.get('lot_data'), prd_wh, goods_receipt_id)
                self.update_sub_report(goods_receipt_id, product_id, warehouse_id, lot_data)
            return prd_wh
        raise serializers.ValidationError({'Product Warehouse': "ProductWareHouse object is not exist"})


class GoodsDetailDataDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ('id',)
