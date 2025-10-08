from apps.masterdata.saledata.models import ProductWareHouseLot, ProductWareHouseSerial
from apps.masterdata.saledata.models.product import ProductSpecificIdentificationSerialNumber
from apps.sales.report.utils.inventory_log import ReportInvLog, ReportInvCommonFunc


class IRForGoodsTransferHandler:
    @classmethod
    def push_to_inventory_report(cls, instance):
        """ Chuẩn bị data để ghi vào báo cáo tồn kho và tính giá Cost """
        doc_data_out = []
        doc_data_in = []
        for item in instance.goods_transfer.all():
            if item.product.general_traceability_method == 0:
                casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(item.uom, item.quantity)
                casted_cost = (item.unit_cost * item.quantity / casted_quantity) if casted_quantity > 0 else 0
                doc_data_out.append({
                    'sale_order': item.sale_order,
                    'product': item.product,
                    'warehouse': item.warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': -1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods transfer (out)',
                    'quantity': casted_quantity,
                    'cost': 0,  # theo gia cost
                    'value': 0,  # theo gia cost
                    'lot_data': {}
                })
                doc_data_in.append({
                    'sale_order': item.sale_order,
                    'product': item.product,
                    'warehouse': item.end_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods transfer (in)',
                    'quantity': casted_quantity,
                    'cost': casted_cost,
                    'value': casted_cost * casted_quantity,
                    'lot_data': {}
                })
            if item.product.general_traceability_method == 1:
                for lot_item in item.lot_data:
                    prd_wh_lot = ProductWareHouseLot.objects.filter(id=lot_item['lot_id']).first()
                    if prd_wh_lot:
                        lot_data = {
                            'lot_id': str(prd_wh_lot.id),
                            'lot_number': prd_wh_lot.lot_number,
                            'lot_expire_date': str(prd_wh_lot.expire_date) if prd_wh_lot.expire_date else None
                        }
                        casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(item.uom, lot_item['quantity'])
                        casted_cost = (
                                item.unit_cost * lot_item['quantity'] / casted_quantity
                        ) if lot_item['quantity'] > 0 else 0
                        doc_data_out.append({
                            'sale_order': item.sale_order,
                            'product': item.product,
                            'warehouse': item.warehouse,
                            'system_date': instance.date_approved,
                            'posting_date': instance.date_approved,
                            'document_date': instance.date_approved,
                            'stock_type': -1,
                            'trans_id': str(instance.id),
                            'trans_code': instance.code,
                            'trans_title': 'Goods transfer (out)',
                            'quantity': casted_quantity,
                            'cost': 0,  # theo gia cost
                            'value': 0,  # theo gia cost
                            'lot_data': lot_data
                        })
                        doc_data_in.append({
                            'sale_order': item.sale_order,
                            'product': item.product,
                            'warehouse': item.end_warehouse,
                            'system_date': instance.date_approved,
                            'posting_date': instance.date_approved,
                            'document_date': instance.date_approved,
                            'stock_type': 1,
                            'trans_id': str(instance.id),
                            'trans_code': instance.code,
                            'trans_title': 'Goods transfer (in)',
                            'quantity': casted_quantity,
                            'cost': casted_cost,
                            'value': casted_cost * casted_quantity,
                            'lot_data': lot_data
                        })
            if item.product.general_traceability_method == 2:
                if item.product.valuation_method == 2:
                    for serial_id in item.sn_data:
                        serial_obj = ProductWareHouseSerial.objects.filter(id=serial_id).first()
                        if serial_obj:
                            specific_value = ProductSpecificIdentificationSerialNumber.get_specific_value(
                                product=item.product,
                                serial_number=serial_obj.serial_number
                            )
                            doc_data_out.append({
                                'sale_order': item.sale_order,
                                'product': item.product,
                                'warehouse': item.warehouse,
                                'system_date': instance.date_approved,
                                'posting_date': instance.date_approved,
                                'document_date': instance.date_approved,
                                'stock_type': -1,
                                'trans_id': str(instance.id),
                                'trans_code': instance.code,
                                'trans_title': 'Goods transfer (out)',
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
                            doc_data_in.append({
                                'sale_order': item.sale_order,
                                'product': item.product,
                                'warehouse': item.end_warehouse,
                                'system_date': instance.date_approved,
                                'posting_date': instance.date_approved,
                                'document_date': instance.date_approved,
                                'stock_type': 1,
                                'trans_id': str(instance.id),
                                'trans_code': instance.code,
                                'trans_title': 'Goods transfer (in)',
                                'quantity': 1,
                                'cost': specific_value,
                                'value': specific_value * 1,
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
                    casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(item.uom, item.quantity)
                    casted_cost = (item.unit_cost * item.quantity / casted_quantity) if casted_quantity > 0 else 0
                    doc_data_out.append({
                        'sale_order': item.sale_order,
                        'product': item.product,
                        'warehouse': item.warehouse,
                        'system_date': instance.date_approved,
                        'posting_date': instance.date_approved,
                        'document_date': instance.date_approved,
                        'stock_type': -1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'trans_title': 'Goods transfer (out)',
                        'quantity': casted_quantity,
                        'cost': 0,  # theo gia cost
                        'value': 0,  # theo gia cost
                        'lot_data': {}
                    })
                    doc_data_in.append({
                        'sale_order': item.sale_order,
                        'product': item.product,
                        'warehouse': item.end_warehouse,
                        'system_date': instance.date_approved,
                        'posting_date': instance.date_approved,
                        'document_date': instance.date_approved,
                        'stock_type': 1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'trans_title': 'Goods transfer (in)',
                        'quantity': casted_quantity,
                        'cost': casted_cost,
                        'value': casted_cost * casted_quantity,
                        'lot_data': {}
                    })
        ReportInvLog.log(instance, instance.date_approved, doc_data_out)
        ReportInvLog.log(instance, instance.date_approved, doc_data_in)
        return True
