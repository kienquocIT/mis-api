from apps.masterdata.saledata.models import ProductWareHouseLot
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
