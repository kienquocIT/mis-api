from rest_framework import serializers
from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial, Product, WareHouse
from apps.sales.inventory.models import (
    GoodsReceipt,
    GoodsReceiptWarehouse,
    GReItemProductWarehouseSerial,
    GReItemProductWarehouse,
    NoneGReItemProductWarehouse,
    NoneGReItemProductWarehouseSerial
)
from apps.sales.purchasing.models import PurchaseRequestProduct


class GoodsDetailListSerializer(serializers.ModelSerializer):
    product_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'product_data',
        )

    @classmethod
    def created_serial_data(cls, good_receipt, good_receipt_product, gr_warehouse, pr_data):
        serial_data = []
        for serial in good_receipt.pw_serial_goods_receipt.filter(
                product_warehouse__product_id=good_receipt_product.product_id,
                product_warehouse__warehouse_id=gr_warehouse.warehouse_id,
        ).order_by('vendor_serial_number', 'serial_number'):
            if not serial.purchase_request_id is None:
                if str(serial.purchase_request_id) == pr_data.get('id'):
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
        return serial_data

    @classmethod
    def get_product_data(cls, obj):
        product_data = []
        for item in obj.goods_receipt_product_goods_receipt.all():
            if item.product.general_traceability_method == 2:
                for gr_wh_gr_prd in item.goods_receipt_warehouse_gr_product.all():
                    pr_data = gr_wh_gr_prd.goods_receipt_request_product.purchase_request_data if (
                        gr_wh_gr_prd.goods_receipt_request_product) else {}
                    serial_data = cls.created_serial_data(
                        good_receipt=obj,
                        good_receipt_product=item,
                        gr_warehouse=gr_wh_gr_prd,
                        pr_data=pr_data
                    )
                    product_data.append({
                        'goods_receipt': {
                            'id': obj.id,
                            'code': obj.code,
                            'title': obj.title,
                            'date_approved': obj.date_approved,
                            'purchase_request': pr_data
                        } if obj else {},
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
                        'quantity_import': gr_wh_gr_prd.quantity_import,
                        'status': int(len(serial_data) == gr_wh_gr_prd.quantity_import)
                    })
        return product_data


class GoodsDetailDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ()

    @classmethod
    def update_serial(cls, item, all_serial, serial_id, goods_receipt_id, purchase_request_id):
        serial = all_serial.filter(id=serial_id, is_delete=False).first()
        if serial:
            if not ProductWareHouseSerial.objects.filter(
                purchase_request_id=purchase_request_id,
                serial_number=item.get('serial_number')
            ).exclude(id=serial_id).exists():
                serial.vendor_serial_number = item.get('vendor_serial_number')
                serial.serial_number = item.get('serial_number')
                serial.expire_date = item.get('expire_date')
                serial.manufacture_date = item.get('manufacture_date')
                serial.warranty_start = item.get('warranty_start')
                serial.warranty_end = item.get('warranty_end')
                serial.goods_receipt_id = goods_receipt_id
                serial.purchase_request_id = purchase_request_id
                serial.save()
                return serial
            raise serializers.ValidationError({'Serial': f"Serial {item.get('serial_number')} is existed"})
        raise serializers.ValidationError({'Serial': f"Serial id {serial_id} does not exist"})

    @classmethod
    def create_serial(cls, item, prd_wh, goods_receipt_id, bulk_info_new_serial, purchase_request_id):
        del item['serial_id']
        if item.get('vendor_serial_number') and item.get('serial_number'):
            goods_receipt_obj = GoodsReceipt.objects.filter(id=goods_receipt_id).first()
            receipted_sn_quantity = goods_receipt_obj.pw_serial_goods_receipt.filter(
                purchase_request_id=purchase_request_id,
                product_warehouse=prd_wh
            ).count() if goods_receipt_obj else 0
            gr_prd = goods_receipt_obj.goods_receipt_product_goods_receipt.filter(
                product=prd_wh.product
            ).first()
            pr_prod = PurchaseRequestProduct.objects.filter(
                product=prd_wh.product, purchase_request_id=purchase_request_id
            ).first()
            gr_wh_gr_prd = gr_prd.goods_receipt_warehouse_gr_product.filter(
                goods_receipt_request_product__purchase_request_product=pr_prod,
                warehouse=prd_wh.warehouse
            ).first() if gr_prd else None
            receipt_max_quantity = gr_wh_gr_prd.quantity_import if gr_wh_gr_prd else 0

            if not ProductWareHouseSerial.objects.filter(
                    product_warehouse__product=prd_wh.product,
                    serial_number=item.get('serial_number'),
                    purchase_request_id=purchase_request_id
            ).exists() and receipted_sn_quantity < receipt_max_quantity:
                bulk_info_new_serial.append(
                    ProductWareHouseSerial(
                        **item,
                        product_warehouse=prd_wh,
                        goods_receipt_id=goods_receipt_id,
                        company_id=prd_wh.company_id,
                        tenant_id=prd_wh.tenant_id,
                        purchase_request_id=purchase_request_id
                    )
                )
                return bulk_info_new_serial
        raise serializers.ValidationError({'Serial': "Can not create new serial."})

    @classmethod
    def sub_create(cls, serial_data, prd_wh, goods_receipt_id, purchase_request_id):
        bulk_info_new_serial = []
        for item in serial_data:
            if item.get('serial_id'):
                cls.update_serial(
                    item,
                    prd_wh.product_warehouse_serial_product_warehouse.all(),
                    item.get('serial_id'),
                    goods_receipt_id,
                    purchase_request_id
                )
            else:
                bulk_info_new_serial = cls.create_serial(
                    item,
                    prd_wh,
                    goods_receipt_id,
                    bulk_info_new_serial,
                    purchase_request_id
                )
        created_sn = ProductWareHouseSerial.objects.bulk_create(bulk_info_new_serial)
        gr_wh = GoodsReceiptWarehouse.objects.filter(
            goods_receipt_id=goods_receipt_id,
            warehouse=prd_wh.warehouse,
            goods_receipt_product__product=prd_wh.product
        ).first()
        if gr_wh:
            cls.handle_goods_receipt_wh(gr_wh=gr_wh, created_sn=created_sn, prd_wh=prd_wh)

        if len(bulk_info_new_serial) > 0:
            prd_wh.receipt_amount += len(bulk_info_new_serial)
            prd_wh.stock_amount = prd_wh.receipt_amount - prd_wh.sold_amount
            prd_wh.save(update_fields=['receipt_amount', 'stock_amount'])
            prd_wh.product.stock_amount += len(bulk_info_new_serial)
            prd_wh.product.save(update_fields=['stock_amount'])
        return True

    @classmethod
    def handle_goods_receipt_wh(cls, gr_wh, created_sn, prd_wh):
        pr_prd = gr_wh.goods_receipt_request_product.purchase_request_product if hasattr(
            gr_wh.goods_receipt_request_product, 'purchase_request_product'
        ) else None
        so_item = pr_prd.sale_order_product if pr_prd and hasattr(
            pr_prd, 'sale_order_product'
        ) else None
        gre_item_prd_wh = GReItemProductWarehouse.objects.filter(
            gre_item__so_item=so_item,
            warehouse=prd_wh.warehouse
        ).first() if so_item else None
        if gre_item_prd_wh:
            # hàng đăng kí
            bulk_info_regis = []
            for serial in created_sn:
                bulk_info_regis.append(
                    GReItemProductWarehouseSerial(
                        gre_item_prd_wh=gre_item_prd_wh,
                        sn_registered=serial,
                        goods_registration=gre_item_prd_wh.goods_registration
                    )
                )
            GReItemProductWarehouseSerial.objects.bulk_create(bulk_info_regis)
        else:
            # kiểm tra hàng vào kho chung
            none_gre_item_prd_wh = NoneGReItemProductWarehouse.objects.filter(
                product=prd_wh.product,
                warehouse=prd_wh.warehouse
            ).first()
            if none_gre_item_prd_wh:
                # hàng đăng kí
                bulk_info_none_regis = []
                for serial in created_sn:
                    bulk_info_none_regis.append(
                        NoneGReItemProductWarehouseSerial(
                            none_gre_item_prd_wh=none_gre_item_prd_wh,
                            sn_mapped=serial
                        )
                    )
                NoneGReItemProductWarehouseSerial.objects.bulk_create(bulk_info_none_regis)

    def create(self, validated_data):
        product_id = self.initial_data.get('product_id')
        warehouse_id = self.initial_data.get('warehouse_id')
        goods_receipt_id = self.initial_data.get('goods_receipt_id')
        purchase_request_id=self.initial_data.get('purchase_request_id')
        prd_wh = ProductWareHouse.objects.filter(product_id=product_id, warehouse_id=warehouse_id).first()
        if prd_wh:
            if self.initial_data.get('is_serial_update'):
                self.sub_create(self.initial_data.get('serial_data'), prd_wh, goods_receipt_id, purchase_request_id)
        else:
            product_obj = Product.objects.filter(id=product_id).first()
            warehouse_obj = WareHouse.objects.filter(id=warehouse_id).first()
            goods_receipt_obj = GoodsReceipt.objects.filter(id=goods_receipt_id).first()
            product_gr_obj = product_obj.goods_receipt_product_product.first()
            if product_obj and warehouse_obj and goods_receipt_obj and product_gr_obj:
                uom_obj = product_gr_obj.uom
                tax_obj = product_gr_obj.tax
                prd_wh = ProductWareHouse.objects.create(
                    tenant_id=goods_receipt_obj.tenant_id,
                    company_id=goods_receipt_obj.company_id,
                    product=product_obj,
                    uom=uom_obj,
                    warehouse=warehouse_obj,
                    tax=tax_obj,
                    unit_price=product_gr_obj.product_unit_price,
                    stock_amount=0,
                    receipt_amount=0,
                    sold_amount=0,
                    picked_ready=0,
                    product_data={
                        'id': product_obj.id,
                        'code': product_obj.code,
                        'title': product_obj.title
                    } if product_obj else {},
                    warehouse_data={
                        'id': warehouse_obj.id,
                        'code': warehouse_obj.code,
                        'title': warehouse_obj.title
                    } if warehouse_obj else {},
                    uom_data={
                        'id': uom_obj.id,
                        'code': uom_obj.code,
                        'title': uom_obj.title
                    } if uom_obj else {},
                    tax_data={
                        'id': tax_obj.id,
                        'code': tax_obj.code,
                        'title': tax_obj.title,
                        'rate': tax_obj.rate
                    } if tax_obj else {}
                )
                if self.initial_data.get('is_serial_update'):
                    self.sub_create(self.initial_data.get('serial_data'), prd_wh, goods_receipt_id, purchase_request_id)
            else:
                raise serializers.ValidationError({'Product Warehouse': "ProductWareHouse object does not exist"})
        return prd_wh


class GoodsDetailDataDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ('id',)


class GoodsDetailDataCreateImportSerializer(GoodsDetailDataCreateSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ()

    def create(self, validated_data):
        product_id = self.initial_data['data'].get('product_id')
        warehouse_id = self.initial_data['data'].get('warehouse_id')
        goods_receipt_id = self.initial_data['data'].get('goods_receipt_id')
        purchase_request_id = self.initial_data['data'].get('purchase_request_id')
        self.initial_data['serial_data'] = [{
            'serial_number': self.initial_data['data'].get('serial_number'),
            'vendor_serial_number': self.initial_data['data'].get('vendor_serial_number'),
            'expire_date': self.initial_data['data'].get('expire_date'),
            'manufacture_date': self.initial_data['data'].get('manufacture_date'),
            'warranty_start': self.initial_data['data'].get('warranty_start'),
            'warranty_end': self.initial_data['data'].get('warranty_end'),
            'serial_id': None
        }]
        prd_wh = ProductWareHouse.objects.filter(product_id=product_id, warehouse_id=warehouse_id).first()
        if prd_wh:
            if self.initial_data['data'].get('is_serial_update'):
                self.sub_create(self.initial_data['serial_data'], prd_wh, goods_receipt_id, purchase_request_id)
        else:
            product_obj = Product.objects.filter(id=product_id).first()
            warehouse_obj = WareHouse.objects.filter(id=warehouse_id).first()
            goods_receipt_obj = GoodsReceipt.objects.filter(id=goods_receipt_id).first()
            product_gr_obj = product_obj.goods_receipt_product_product.first()
            if product_obj and warehouse_obj and goods_receipt_obj and product_gr_obj:
                uom_obj = product_gr_obj.uom
                tax_obj = product_gr_obj.tax
                prd_wh = ProductWareHouse.objects.create(
                    tenant_id=goods_receipt_obj.tenant_id,
                    company_id=goods_receipt_obj.company_id,
                    product=product_obj,
                    uom=uom_obj,
                    warehouse=warehouse_obj,
                    tax=tax_obj,
                    unit_price=product_gr_obj.product_unit_price,
                    stock_amount=0,
                    receipt_amount=0,
                    sold_amount=0,
                    picked_ready=0,
                    product_data={
                        'id': product_obj.id,
                        'code': product_obj.code,
                        'title': product_obj.title
                    } if product_obj else {},
                    warehouse_data={
                        'id': warehouse_obj.id,
                        'code': warehouse_obj.code,
                        'title': warehouse_obj.title
                    } if warehouse_obj else {},
                    uom_data={
                        'id': uom_obj.id,
                        'code': uom_obj.code,
                        'title': uom_obj.title
                    } if uom_obj else {},
                    tax_data={
                        'id': tax_obj.id,
                        'code': tax_obj.code,
                        'title': tax_obj.title,
                        'rate': tax_obj.rate
                    } if tax_obj else {}
                )
                if self.initial_data['data'].get('is_serial_update'):
                    self.sub_create(self.initial_data['serial_data'], prd_wh, goods_receipt_id, purchase_request_id)
            else:
                raise serializers.ValidationError({'Product Warehouse': "ProductWareHouse object does not exist"})
        return prd_wh
