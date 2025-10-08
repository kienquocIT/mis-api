from rest_framework import serializers
from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial, Product, WareHouse
from apps.sales.inventory.models import (
    GoodsReceipt,
    GReItemProductWarehouseSerial,
    NoneGReItemProductWarehouse,
    NoneGReItemProductWarehouseSerial, GoodsDetail
)
from apps.sales.purchasing.models import PurchaseRequest


class GoodsDetailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsDetail
        fields = (
            'id',
            'product',
            'product_data',
            'warehouse',
            'warehouse_data',
            'uom',
            'uom_data',
            'goods_receipt',
            'goods_receipt_data',
            'purchase_request',
            'purchase_request_data',
            'lot',
            'lot_data',
            'imported_sn_quantity',
            'receipt_quantity',
            'status',
        )


class GoodsDetailSerialDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouseSerial
        fields = (
            'id',
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end',
            'serial_status',
            'purchase_request_id',
            'goods_receipt_id',
            'date_created',
        )


class GoodsDetailDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ()

    def validate(self, validate_data):
        product_id = self.initial_data.get('product_id')
        warehouse_id = self.initial_data.get('warehouse_id')
        goods_receipt_id = self.initial_data.get('goods_receipt_id')
        purchase_request_id = self.initial_data.get('purchase_request_id')
        if not product_id:
            raise serializers.ValidationError({'product_obj': "Product does not found."})
        validate_data['product_obj'] = Product.objects.filter(id=product_id).first()
        if not warehouse_id:
            raise serializers.ValidationError({'warehouse_obj': "Warehouse does not found."})
        validate_data['warehouse_obj'] = WareHouse.objects.filter(id=warehouse_id).first()
        if not goods_receipt_id:
            raise serializers.ValidationError({'goods_receipt_obj': "Goods Receipt does not found."})
        validate_data['goods_receipt_obj'] = GoodsReceipt.objects.filter(id=goods_receipt_id).first()
        if purchase_request_id:
            validate_data['purchase_request_obj'] = PurchaseRequest.objects.filter(id=purchase_request_id).first()
        else:
            validate_data['purchase_request_obj'] = None
        validate_data['serial_data'] = self.initial_data.get('serial_data', [])

        prd_wh_obj = ProductWareHouse.objects.filter(
            product=validate_data['product_obj'],
            warehouse=validate_data['warehouse_obj']
        ).first()
        if not prd_wh_obj:
            product_gr_obj = validate_data['goods_receipt_obj'].goods_receipt_product_goods_receipt.filter(
                product=validate_data['product_obj']
            ).first()
            if product_gr_obj:
                uom_obj = product_gr_obj.uom
                tax_obj = product_gr_obj.tax
                prd_wh_obj = ProductWareHouse.objects.create(
                    tenant=validate_data['goods_receipt_obj'].tenant,
                    company=validate_data['goods_receipt_obj'].company,
                    product=validate_data['product_obj'],
                    uom=uom_obj,
                    warehouse=validate_data['warehouse_obj'],
                    tax=tax_obj,
                    unit_price=product_gr_obj.product_unit_price,
                    stock_amount=0,
                    receipt_amount=0,
                    sold_amount=0,
                    picked_ready=0,
                    product_data={
                        'id': str(validate_data['product_obj'].id),
                        'code': validate_data['product_obj'].code,
                        'title': validate_data['product_obj'].title
                    } if validate_data['product_obj'] else {},
                    warehouse_data={
                        'id': str(validate_data['warehouse_obj'].id),
                        'code': validate_data['warehouse_obj'].code,
                        'title': validate_data['warehouse_obj'].title
                    } if validate_data['warehouse_obj'] else {},
                    uom_data={
                        'id': str(uom_obj.id),
                        'code': uom_obj.code,
                        'title': uom_obj.title
                    } if uom_obj else {},
                    tax_data={
                        'id': str(tax_obj.id),
                        'code': tax_obj.code,
                        'title': tax_obj.title,
                        'rate': tax_obj.rate
                    } if tax_obj else {}
                )
            else:
                raise serializers.ValidationError({
                    'product_gr_obj': f"Can not find Prd: {validate_data['product_obj'].title} in "
                                      f"GR: {validate_data['product_obj'].title}."
                })
        validate_data['prd_wh_obj'] = prd_wh_obj
        goods_detail_obj = GoodsDetail.objects.filter(
            product=prd_wh_obj.product,
            warehouse=prd_wh_obj.warehouse,
            goods_receipt=validate_data.get('goods_receipt_obj'),
            purchase_request=validate_data.get('purchase_request_obj')
        ).first()
        if not goods_detail_obj:
            raise serializers.ValidationError({'goods_detail_obj': "Can not find Goods detail object."})
        # if goods_detail_obj.status:
        #     raise serializers.ValidationError({'goods_detail_obj': "This Goods detail has completed already."})
        validate_data['goods_detail_obj'] = goods_detail_obj
        return validate_data

    @classmethod
    def update_serial(cls, serial_item):
        serial_obj = ProductWareHouseSerial.objects.filter(id=serial_item.get('serial_id')).first()
        if serial_obj:
            if serial_obj.serial_status == 0:
                serial_obj.vendor_serial_number = serial_item.get('vendor_serial_number')
                serial_obj.serial_number = serial_item.get('serial_number')
                serial_obj.expire_date = serial_item.get('expire_date')
                serial_obj.manufacture_date = serial_item.get('manufacture_date')
                serial_obj.warranty_start = serial_item.get('warranty_start')
                serial_obj.warranty_end = serial_item.get('warranty_end')
                serial_obj.save(update_fields=[
                    'vendor_serial_number',
                    'serial_number',
                    'expire_date',
                    'manufacture_date',
                    'warranty_start',
                    'warranty_end',
                ])
                return serial_obj
            raise serializers.ValidationError({'serial_obj': f"Serial {serial_obj.serial_number} is deleted."})
        raise serializers.ValidationError({'error': f"Serial id {serial_item.get('serial_id')} does not exist."})

    @classmethod
    def combine_new_serial(cls, serial_item, validated_data):
        prd_wh_obj = validated_data.get('prd_wh_obj')
        goods_detail_obj = validated_data.get('goods_detail_obj')
        if serial_item.get('serial_number'):
            goods_receipt_obj = validated_data.get('goods_receipt_obj')
            purchase_request_obj = validated_data.get('purchase_request_obj')
            serial_obj = ProductWareHouseSerial.objects.filter(serial_number=serial_item.get('serial_number')).first()
            if not serial_obj:
                if goods_detail_obj.imported_sn_quantity < goods_detail_obj.receipt_quantity:
                    return ProductWareHouseSerial(
                        **serial_item,
                        product_warehouse=prd_wh_obj,
                        goods_receipt=goods_receipt_obj,
                        purchase_request=purchase_request_obj,
                        tenant=goods_receipt_obj.tenant,
                        company=goods_receipt_obj.company,
                    )
                raise serializers.ValidationError({
                    'error': f"You have imported max receipt quantity already ({goods_detail_obj.receipt_quantity})."
                })
            raise serializers.ValidationError({'serial_obj': "This serial already exists."})
        raise serializers.ValidationError({'serial_number': "Serial number is missing."})

    @classmethod
    def sub_create_or_update(cls, validated_data):
        prd_wh_obj = validated_data.get('prd_wh_obj')
        goods_detail_obj = validated_data.get('goods_detail_obj')
        bulk_info_new_serial = []
        for serial_item in validated_data.get('serial_data', []):
            if serial_item.get('serial_id'):
                cls.update_serial(serial_item)
            else:
                serial_item.pop('serial_id')
                serial_new_obj = cls.combine_new_serial(serial_item, validated_data)
                bulk_info_new_serial.append(serial_new_obj)
        if len(bulk_info_new_serial) > 0:
            created_sn = ProductWareHouseSerial.objects.bulk_create(bulk_info_new_serial)
            prd_wh_obj.receipt_amount += len(bulk_info_new_serial)
            prd_wh_obj.stock_amount = prd_wh_obj.receipt_amount - prd_wh_obj.sold_amount
            prd_wh_obj.save(update_fields=['receipt_amount', 'stock_amount'])
            prd_wh_obj.product.stock_amount += len(bulk_info_new_serial)
            prd_wh_obj.product.save(update_fields=['stock_amount'])
            goods_detail_obj.imported_sn_quantity += len(bulk_info_new_serial)
            if goods_detail_obj.imported_sn_quantity == goods_detail_obj.receipt_quantity:
                goods_detail_obj.status = True
            goods_detail_obj.save(update_fields=['imported_sn_quantity', 'status'])
            # kiểm tra đăng kí hàng
            cls.handle_registration(validated_data, created_sn)
        return True

    @classmethod
    def handle_registration(cls, validated_data, created_sn):
        prd_wh_obj = validated_data.get('prd_wh_obj')
        goods_receipt_obj = validated_data.get('goods_receipt_obj')
        gr_wh_obj = goods_receipt_obj.goods_receipt_warehouse_goods_receipt.filter(
            warehouse=prd_wh_obj.warehouse,
            goods_receipt_product__product=prd_wh_obj.product
        ).first()
        pr_prd_obj = gr_wh_obj.goods_receipt_request_product.purchase_request_product if hasattr(
            gr_wh_obj.goods_receipt_request_product, 'purchase_request_product'
        ) else None
        so_item_obj = pr_prd_obj.sale_order_product if pr_prd_obj and hasattr(
            pr_prd_obj, 'sale_order_product'
        ) else None
        gre_item_prd_wh_obj = prd_wh_obj.warehouse.gre_item_prd_wh_warehouse.filter(
            gre_item__so_item=so_item_obj,
        ).first() if so_item_obj else None

        if gre_item_prd_wh_obj: # hàng có đăng kí
            bulk_info_regis = []
            for serial in created_sn:
                bulk_info_regis.append(GReItemProductWarehouseSerial(
                    gre_item_prd_wh=gre_item_prd_wh_obj,
                    goods_registration=gre_item_prd_wh_obj.goods_registration,
                    sn_registered=serial
                ))
            GReItemProductWarehouseSerial.objects.bulk_create(bulk_info_regis)
        else: # hàng vào kho chung
            none_gre_item_prd_wh_obj = NoneGReItemProductWarehouse.objects.filter(
                product=prd_wh_obj.product,
                warehouse=prd_wh_obj.warehouse
            ).first()
            if none_gre_item_prd_wh_obj:
                bulk_info_none_regis = []
                for serial in created_sn:
                    bulk_info_none_regis.append(NoneGReItemProductWarehouseSerial(
                        none_gre_item_prd_wh=none_gre_item_prd_wh_obj,
                        sn_mapped=serial
                    ))
                NoneGReItemProductWarehouseSerial.objects.bulk_create(bulk_info_none_regis)
        return True

    def create(self, validated_data):
        self.sub_create_or_update(validated_data)
        return validated_data.get('prd_wh_obj')


class GoodsDetailDataDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ('id',)


class GoodsDetailCreateSerializerImportDB(GoodsDetailDataCreateSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ()

    def validate(self, validate_data):
        initial_data = self.initial_data.get('data')
        if initial_data:
            product_id = initial_data.get('product_id')
            warehouse_id = initial_data.get('warehouse_id')
            goods_receipt_id = initial_data.get('goods_receipt_id')
            purchase_request_id = initial_data.get('purchase_request_id')
            if not product_id:
                raise serializers.ValidationError({'product_obj': "Product does not found."})
            validate_data['product_obj'] = Product.objects.filter(id=product_id).first()
            if not warehouse_id:
                raise serializers.ValidationError({'warehouse_obj': "Warehouse does not found."})
            validate_data['warehouse_obj'] = WareHouse.objects.filter(id=warehouse_id).first()
            if not goods_receipt_id:
                raise serializers.ValidationError({'goods_receipt_obj': "Goods Receipt does not found."})
            validate_data['goods_receipt_obj'] = GoodsReceipt.objects.filter(id=goods_receipt_id).first()
            if purchase_request_id:
                validate_data['purchase_request_obj'] = PurchaseRequest.objects.filter(id=purchase_request_id).first()
            else:
                validate_data['purchase_request_obj'] = None
            validate_data['serial_data'] = [{
                'serial_number': initial_data.get('serial_number'),
                'vendor_serial_number': initial_data.get('vendor_serial_number'),
                'expire_date': initial_data.get('expire_date'),
                'manufacture_date': initial_data.get('manufacture_date'),
                'warranty_start': initial_data.get('warranty_start'),
                'warranty_end': initial_data.get('warranty_end'),
                'serial_id': None
            }]

            prd_wh_obj = ProductWareHouse.objects.filter(
                product=validate_data['product_obj'],
                warehouse=validate_data['warehouse_obj']
            ).first()
            if not prd_wh_obj:
                product_gr_obj = validate_data['goods_receipt_obj'].goods_receipt_product_goods_receipt.filter(
                    product=validate_data['product_obj']
                ).first()
                if product_gr_obj:
                    uom_obj = product_gr_obj.uom
                    tax_obj = product_gr_obj.tax
                    prd_wh_obj = ProductWareHouse.objects.create(
                        tenant=validate_data['goods_receipt_obj'].tenant,
                        company=validate_data['goods_receipt_obj'].company,
                        product=validate_data['product_obj'],
                        uom=uom_obj,
                        warehouse=validate_data['warehouse_obj'],
                        tax=tax_obj,
                        unit_price=product_gr_obj.product_unit_price,
                        stock_amount=0,
                        receipt_amount=0,
                        sold_amount=0,
                        picked_ready=0,
                        product_data={
                            'id': str(validate_data['product_obj'].id),
                            'code': validate_data['product_obj'].code,
                            'title': validate_data['product_obj'].title
                        } if validate_data['product_obj'] else {},
                        warehouse_data={
                            'id': str(validate_data['warehouse_obj'].id),
                            'code': validate_data['warehouse_obj'].code,
                            'title': validate_data['warehouse_obj'].title
                        } if validate_data['warehouse_obj'] else {},
                        uom_data={
                            'id': str(uom_obj.id),
                            'code': uom_obj.code,
                            'title': uom_obj.title
                        } if uom_obj else {},
                        tax_data={
                            'id': str(tax_obj.id),
                            'code': tax_obj.code,
                            'title': tax_obj.title,
                            'rate': tax_obj.rate
                        } if tax_obj else {}
                    )
                else:
                    raise serializers.ValidationError({
                        'product_gr_obj': f"Can not find Prd: {validate_data['product_obj'].title} in "
                                          f"GR: {validate_data['product_obj'].title}."
                    })
            validate_data['prd_wh_obj'] = prd_wh_obj
            goods_detail_obj = GoodsDetail.objects.filter(
                product=prd_wh_obj.product,
                warehouse=prd_wh_obj.warehouse,
                goods_receipt=validate_data.get('goods_receipt_obj'),
                purchase_request=validate_data.get('purchase_request_obj')
            ).first()
            if not goods_detail_obj:
                raise serializers.ValidationError({'goods_detail_obj': "Can not find Goods detail object."})
            # if goods_detail_obj.status:
            #     raise serializers.ValidationError({'goods_detail_obj': "This Goods detail has completed already."})
            validate_data['goods_detail_obj'] = goods_detail_obj
            return validate_data
        raise serializers.ValidationError({'validate_data': "Import data is invalid."})


class GoodsDetailDetailSerializerImportDB(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = ('id',)
