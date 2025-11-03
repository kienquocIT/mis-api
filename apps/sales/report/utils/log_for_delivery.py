from apps.masterdata.saledata.models import ProductWareHouseLot, ProductWareHouseSerial
from apps.sales.report.utils.inventory_log import ReportInvCommonFunc, ReportInvLog


class IRForDeliveryHandler:
    @classmethod
    def for_lot(
            cls, instance, lot_data, doc_data, product_obj, warehouse_obj, uom_obj, sale_order_obj, lease_order_obj
    ):
        for lot in lot_data:
            lot_obj = ProductWareHouseLot.objects.filter(id=lot.get('product_warehouse_lot_id')).first()
            if lot_obj and lot.get('quantity_delivery'):
                casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(uom_obj, lot.get('quantity_delivery'))
                doc_data.append({
                    'sale_order': sale_order_obj,
                    'lease_order': lease_order_obj,
                    'product': product_obj,
                    'warehouse': warehouse_obj,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': -1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Delivery (sale)' if sale_order_obj else 'Delivery (lease)',
                    'quantity': casted_quantity,
                    'cost': 0,  # theo gia cost
                    'value': 0,  # theo gia cost
                    'lot_data': {
                        'lot_id': str(lot_obj.id),
                        'lot_number': lot_obj.lot_number,
                        'lot_expire_date': str(lot_obj.expire_date) if lot_obj.expire_date else None
                    }
                })
        return doc_data

    @classmethod
    def for_sn(
            cls, instance, sn_data, doc_data, product_obj, warehouse_obj, uom_obj, sale_order_obj, lease_order_obj
    ):
        if product_obj.valuation_method == 2:
            for serial in sn_data:
                serial_obj = ProductWareHouseSerial.objects.filter(id=serial.get('product_warehouse_serial_id')).first()
                if serial_obj:
                    doc_data.append({
                        'sale_order': sale_order_obj,
                        'lease_order': lease_order_obj,
                        'product': product_obj,
                        'warehouse': warehouse_obj,
                        'system_date': instance.date_approved,
                        'posting_date': instance.date_approved,
                        'document_date': instance.date_approved,
                        'stock_type': -1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'trans_title': 'Delivery (sale)' if sale_order_obj else 'Delivery (lease)',
                        'quantity': 1,
                        'cost': 0,  # theo gia cost
                        'value': 0,  # theo gia cost
                        'lot_data': {},
                        'serial_data': {
                            'serial_id': str(serial_obj.id),
                            'serial_number': serial_obj.serial_number,
                            'vendor_serial_number': serial_obj.vendor_serial_number,
                            'expire_date': str(
                                serial_obj.expire_date
                            ) if serial_obj.expire_date else None,
                            'manufacture_date': str(
                                serial_obj.manufacture_date
                            ) if serial_obj.manufacture_date else None,
                            'warranty_start': str(
                                serial_obj.warranty_start
                            ) if serial_obj.warranty_start else None,
                            'warranty_end': str(
                                serial_obj.warranty_end
                            ) if serial_obj.warranty_end else None,
                        }
                    })
        else:
            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(uom_obj, len(sn_data))
            doc_data.append({
                'sale_order': sale_order_obj,
                'lease_order': lease_order_obj,
                'product': product_obj,
                'warehouse': warehouse_obj,
                'system_date': instance.date_approved,
                'posting_date': instance.date_approved,
                'document_date': instance.date_approved,
                'stock_type': -1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Delivery (sale)' if sale_order_obj else 'Delivery (lease)',
                'quantity': casted_quantity,
                'cost': 0,  # theo gia cost
                'value': 0,  # theo gia cost
                'lot_data': {}
            })
        return doc_data

    @classmethod
    def push_to_inventory_report(cls, instance):
        """ Chuẩn bị data để ghi vào báo cáo tồn kho và tính giá Cost """
        doc_data = []
        sale_order_obj = instance.order_delivery.sale_order if instance.order_delivery else None
        for deli_product in instance.delivery_product_delivery_sub.all():
            if deli_product.product and sale_order_obj:
                product_obj = deli_product.product
                for pw_data in deli_product.delivery_pw_delivery_product.filter(quantity_delivery__gt=0):
                    warehouse_obj = pw_data.warehouse
                    uom_obj = pw_data.uom
                    quantity = pw_data.quantity_delivery
                    lot_data = pw_data.lot_data
                    sn_data = pw_data.serial_data
                    if product_obj.general_traceability_method == 0:  # None
                        casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(uom_obj, quantity)
                        doc_data.append({
                            'sale_order': sale_order_obj,
                            'lease_order': None,
                            'product': product_obj,
                            'warehouse': warehouse_obj,
                            'system_date': instance.date_approved,
                            'posting_date': instance.date_approved,
                            'document_date': instance.date_approved,
                            'stock_type': -1,
                            'trans_id': str(instance.id),
                            'trans_code': instance.code,
                            'trans_title': 'Delivery (sale)',
                            'quantity': casted_quantity,
                            'cost': 0,  # theo gia cost
                            'value': 0,  # theo gia cost
                            'lot_data': {}
                        })
                    if product_obj.general_traceability_method == 1 and len(lot_data) > 0:  # Lot
                        cls.for_lot(
                            instance,
                            lot_data,
                            doc_data,
                            product_obj,
                            warehouse_obj,
                            uom_obj,
                            sale_order_obj,
                            None
                        )
                    if product_obj.general_traceability_method == 2 and len(sn_data) > 0:  # Sn
                        cls.for_sn(
                            instance,
                            sn_data,
                            doc_data,
                            product_obj,
                            warehouse_obj,
                            uom_obj,
                            sale_order_obj,
                            None
                        )
        ReportInvLog.log(instance, instance.date_approved, doc_data)
        return True

    @classmethod
    def push_to_inventory_report_lease(cls, instance):
        """ Chuẩn bị data để ghi vào báo cáo tồn kho và tính giá Cost """
        doc_data = []
        lease_order_obj = instance.order_delivery.lease_order if instance.order_delivery else None
        for deli_product in instance.delivery_product_delivery_sub.all():
            if deli_product.offset_data and lease_order_obj:
                for deli_offset in deli_product.delivery_po_delivery_product.filter(offset__isnull=False):
                    product_obj = deli_offset.offset
                    for pw_data in deli_offset.delivery_pw_delivery_offset.filter(quantity_delivery__gt=0):
                        warehouse_obj = pw_data.warehouse
                        uom_obj = pw_data.uom
                        quantity = pw_data.quantity_delivery
                        lot_data = pw_data.lot_data
                        sn_data = pw_data.serial_data
                        if product_obj.general_traceability_method == 0:  # None
                            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(uom_obj, quantity)
                            doc_data.append({
                                'sale_order': None,
                                'lease_order': lease_order_obj,
                                'product': product_obj,
                                'warehouse': warehouse_obj,
                                'system_date': instance.date_approved,
                                'posting_date': instance.date_approved,
                                'document_date': instance.date_approved,
                                'stock_type': -1,
                                'trans_id': str(instance.id),
                                'trans_code': instance.code,
                                'trans_title': 'Delivery (lease)',
                                'quantity': casted_quantity,
                                'cost': 0,  # theo gia cost
                                'value': 0,  # theo gia cost
                                'lot_data': {}
                            })
                        if product_obj.general_traceability_method == 1 and len(lot_data) > 0:  # Lot
                            cls.for_lot(
                                instance,
                                lot_data,
                                doc_data,
                                product_obj,
                                warehouse_obj,
                                uom_obj,
                                None,
                                lease_order_obj
                            )
                        if product_obj.general_traceability_method == 2 and len(sn_data) > 0:  # Sn
                            cls.for_sn(
                                instance,
                                sn_data,
                                doc_data,
                                product_obj,
                                warehouse_obj,
                                uom_obj,
                                None,
                                lease_order_obj
                            )
        ReportInvLog.log(instance, instance.date_approved, doc_data)
        return True
