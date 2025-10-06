from apps.masterdata.saledata.models import ProductWareHouseLot, ProductWareHouseSerial
from apps.sales.report.utils.inventory_log import ReportInvLog, ReportInvCommonFunc


class IRForGoodsIssueHandler:
    @classmethod
    def push_to_inventory_report(cls, instance):
        """ Chuẩn bị data để ghi vào báo cáo tồn kho và tính giá Cost """
        doc_data = []
        for item in instance.goods_issue_product.filter(issued_quantity__gt=0):
            if len(item.lot_data) > 0:
                for lot_item in item.lot_data:
                    prd_wh_lot = ProductWareHouseLot.objects.filter(id=lot_item['lot_id']).first()
                    if prd_wh_lot and lot_item.get('quantity', 0) > 0:
                        casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(
                            item.uom, lot_item.get('quantity', 0)
                        )
                        doc_data.append({
                            'product': item.product,
                            'warehouse': item.warehouse,
                            'system_date': instance.date_approved,
                            'posting_date': instance.date_approved,
                            'document_date': instance.date_approved,
                            'stock_type': -1,
                            'trans_id': str(instance.id),
                            'trans_code': instance.code,
                            'trans_title': 'Goods issue',
                            'quantity': casted_quantity,
                            'cost': 0,  # theo gia cost
                            'value': 0,  # theo gia cost
                            'lot_data': {
                                'lot_id': str(prd_wh_lot.id),
                                'lot_number': prd_wh_lot.lot_number,
                                'lot_expire_date': str(prd_wh_lot.expire_date) if prd_wh_lot.expire_date else None
                            }
                        })
            elif len(item.sn_data) > 0:
                if item.product.valuation_method == 2:
                    for serial_id in item.sn_data:
                        serial_mapped = ProductWareHouseSerial.objects.filter(id=serial_id).first()
                        if serial_mapped:
                            doc_data.append({
                                'product': item.product,
                                'warehouse': item.warehouse,
                                'system_date': instance.date_approved,
                                'posting_date': instance.date_approved,
                                'document_date': instance.date_approved,
                                'stock_type': -1,
                                'trans_id': str(instance.id),
                                'trans_code': instance.code,
                                'trans_title': 'Goods issue',
                                'quantity': 1,
                                'cost': 0,  # theo gia cost
                                'value': 0,  # theo gia cost
                                'lot_data': {},
                                'serial_data': {
                                    'serial_id': str(serial_mapped.id),
                                    'serial_number': serial_mapped.serial_number,
                                    'vendor_serial_number': serial_mapped.vendor_serial_number,
                                    'expire_date': str(
                                        serial_mapped.expire_date) if serial_mapped.expire_date else None,
                                    'manufacture_date': str(
                                        serial_mapped.manufacture_date) if serial_mapped.manufacture_date else None,
                                    'warranty_start': str(
                                        serial_mapped.warranty_start) if serial_mapped.warranty_start else None,
                                    'warranty_end': str(
                                        serial_mapped.warranty_end) if serial_mapped.warranty_end else None,
                                }
                            })
                else:
                    casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(item.uom, item.issued_quantity)
                    doc_data.append({
                        'product': item.product,
                        'warehouse': item.warehouse,
                        'system_date': instance.date_approved,
                        'posting_date': instance.date_approved,
                        'document_date': instance.date_approved,
                        'stock_type': -1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'trans_title': 'Goods issue',
                        'quantity': casted_quantity,
                        'cost': 0,  # theo gia cost
                        'value': 0,  # theo gia cost
                        'lot_data': {}
                    })
            else:
                casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(item.uom, item.issued_quantity)
                doc_data.append({
                    'product': item.product,
                    'warehouse': item.warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': -1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods issue',
                    'quantity': casted_quantity,
                    'cost': 0,  # theo gia cost
                    'value': 0,  # theo gia cost
                    'lot_data': {}
                })
        new_logs = ReportInvLog.log(instance, instance.date_approved, doc_data)
        return new_logs
