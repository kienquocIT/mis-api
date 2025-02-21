from apps.masterdata.saledata.models import ProductWareHouseLot
from apps.sales.report.utils import ReportInvCommonFunc, ReportInvLog


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
                    'system_date': instance.date_done,
                    'posting_date': instance.date_done,
                    'document_date': instance.date_done,
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
        casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(uom_obj, len(sn_data))
        doc_data.append({
            'sale_order': sale_order_obj,
            'lease_order': lease_order_obj,
            'product': product_obj,
            'warehouse': warehouse_obj,
            'system_date': instance.date_done,
            'posting_date': instance.date_done,
            'document_date': instance.date_done,
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
        for deli_product in instance.delivery_product_delivery_sub.all():
            if deli_product.product:
                product_obj = deli_product.product
                for pw_data in deli_product.delivery_pw_delivery_product.all():
                    sale_order_obj = pw_data.sale_order
                    lease_order_obj = pw_data.lease_order
                    warehouse_obj = pw_data.warehouse
                    uom_obj = pw_data.uom
                    quantity = pw_data.quantity_delivery
                    lot_data = pw_data.lot_data
                    sn_data = pw_data.serial_data
                    if warehouse_obj and uom_obj and quantity > 0:
                        if product_obj.general_traceability_method == 0:  # None
                            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(uom_obj, quantity)
                            doc_data.append({
                                'sale_order': sale_order_obj,
                                'lease_order': lease_order_obj,
                                'product': product_obj,
                                'warehouse': warehouse_obj,
                                'system_date': instance.date_done,
                                'posting_date': instance.date_done,
                                'document_date': instance.date_done,
                                'stock_type': -1,
                                'trans_id': str(instance.id),
                                'trans_code': instance.code,
                                'trans_title': 'Delivery (sale)' if sale_order_obj else 'Delivery (lease)',
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
                                sale_order_obj,
                                lease_order_obj
                            )
        ReportInvLog.log(instance, instance.date_done, doc_data)
        print('Write to Inventory Report successfully!')
        return True
