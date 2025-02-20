from apps.masterdata.saledata.models import ProductWareHouseLot
from apps.sales.report.utils import ReportInvLog, ReportInvCommonFunc


class IRForGoodsReceiptHandler:
    @classmethod
    def get_all_lots(cls, instance):
        all_lots_in_gr = list({lot.lot_number for lot in instance.goods_receipt_lot_goods_receipt.all()})
        all_lots = ProductWareHouseLot.objects.filter(lot_number__in=all_lots_in_gr)
        return all_lots

    @classmethod
    def gr_has_pr_combine_log_data(cls, pr_item, gr_item, doc_data, sale_order, all_lots, instance):
        for prd_wh in pr_item.goods_receipt_warehouse_request_product.all():
            if gr_item.product.general_traceability_method != 1:
                casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(
                    gr_item.uom, prd_wh.quantity_import
                )
                casted_cost = (
                        gr_item.product_unit_price * prd_wh.quantity_import / casted_quantity
                ) if casted_quantity > 0 else 0
                doc_data.append({
                    'sale_order': sale_order,
                    'product': gr_item.product,
                    'warehouse': prd_wh.warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods receipt',
                    'quantity': casted_quantity,
                    'cost': casted_cost,
                    'value': casted_cost * casted_quantity,
                    'lot_data': {}
                })
            else:
                for lot in prd_wh.goods_receipt_lot_gr_warehouse.all():
                    lot_mapped = all_lots.filter(lot_number=lot.lot_number).first()
                    if lot_mapped:
                        casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(
                            gr_item.uom, lot.quantity_import
                        )
                        casted_cost = (
                                gr_item.product_unit_price * lot.quantity_import / casted_quantity
                        ) if casted_quantity > 0 else 0
                        doc_data.append({
                            'sale_order': sale_order,
                            'product': gr_item.product,
                            'warehouse': prd_wh.warehouse,
                            'system_date': instance.date_approved,
                            'posting_date': instance.date_approved,
                            'document_date': instance.date_approved,
                            'stock_type': 1,
                            'trans_id': str(instance.id),
                            'trans_code': instance.code,
                            'trans_title': 'Goods receipt',
                            'quantity': casted_quantity,
                            'cost': casted_cost,
                            'value': casted_cost * casted_quantity,
                            'lot_data': {
                                'lot_id': str(lot_mapped.id),
                                'lot_number': lot.lot_number,
                                'lot_expire_date': str(lot.expire_date) if lot.expire_date else None
                            }
                        })
        return doc_data

    @classmethod
    def gr_has_no_pr(cls, instance, doc_data, all_lots):
        goods_receipt_warehouses = instance.goods_receipt_warehouse_goods_receipt.all()
        for gr_item in instance.goods_receipt_product_goods_receipt.all():
            if gr_item.product.general_traceability_method != 1:  # None + Sn
                for gr_prd_wh in goods_receipt_warehouses.filter(goods_receipt_product__product=gr_item.product):
                    casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(
                        gr_item.uom, gr_prd_wh.quantity_import
                    )
                    casted_cost = (
                        gr_item.product_unit_price * gr_prd_wh.quantity_import / casted_quantity
                    ) if casted_quantity > 0 else 0
                    doc_data.append({
                        'product': gr_item.product,
                        'warehouse': gr_prd_wh.warehouse,
                        'system_date': instance.date_approved,
                        'posting_date': instance.date_approved,
                        'document_date': instance.date_approved,
                        'stock_type': 1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'trans_title': 'Goods receipt (IA)'
                        if instance.goods_receipt_type == 1 else 'Goods receipt',
                        'quantity': casted_quantity,
                        'cost': casted_cost,
                        'value': casted_cost * casted_quantity,
                        'lot_data': {}
                    })
            else:  # lot
                for gr_prd_wh in goods_receipt_warehouses.filter(goods_receipt_product__product=gr_item.product):
                    for lot in gr_prd_wh.goods_receipt_lot_gr_warehouse.all():
                        lot_mapped = all_lots.filter(lot_number=lot.lot_number).first()
                        if lot_mapped:
                            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(
                                gr_item.uom,
                                lot.quantity_import
                            )
                            casted_cost = (
                                gr_item.product_unit_price * lot.quantity_import / casted_quantity
                            ) if casted_quantity > 0 else 0
                            doc_data.append({
                                'product': gr_item.product,
                                'warehouse': gr_prd_wh.warehouse,
                                'system_date': instance.date_approved,
                                'posting_date': instance.date_approved,
                                'document_date': instance.date_approved,
                                'stock_type': 1,
                                'trans_id': str(instance.id),
                                'trans_code': instance.code,
                                'trans_title': 'Goods receipt (IA)'
                                if instance.goods_receipt_type == 1 else 'Goods receipt',
                                'quantity': casted_quantity,
                                'cost': casted_cost,
                                'value': casted_cost * casted_quantity,
                                'lot_data': {
                                    'lot_id': str(lot_mapped.id),
                                    'lot_number': lot.lot_number,
                                    'lot_expire_date': str(lot.expire_date) if lot.expire_date else None
                                }
                            })
        return doc_data

    @classmethod
    def gr_has_pr(cls, instance, doc_data, all_lots):
        for gr_item in instance.goods_receipt_product_goods_receipt.all():
            for pr_item in gr_item.goods_receipt_request_product_gr_product.all():
                sale_order = None
                if instance.goods_receipt_type == 0:
                    if pr_item.purchase_request_product:
                        if pr_item.purchase_request_product.purchase_request:
                            sale_order = pr_item.purchase_request_product.purchase_request.sale_order
                if instance.goods_receipt_type == 2:
                    if pr_item.production_report:
                        if pr_item.production_report.work_order:
                            sale_order = pr_item.production_report.work_order.sale_order
                doc_data = cls.gr_has_pr_combine_log_data(
                    pr_item, gr_item, doc_data, sale_order, all_lots, instance
                )
        return doc_data

    @classmethod
    def push_to_inventory_report(cls, instance):
        """ Chuẩn bị data để ghi vào báo cáo tồn kho và tính giá Cost """
        all_lots = cls.get_all_lots(instance)
        doc_data = []
        if instance.goods_receipt_type in [0, 1]:  # GR by PO/IA
            if instance.goods_receipt_pr_goods_receipt.count() == 0:
                doc_data = cls.gr_has_no_pr(instance, doc_data, all_lots)
            else:
                doc_data = cls.gr_has_pr(instance, doc_data, all_lots)
        if instance.goods_receipt_type == 2:  # GR by Production
            if instance.production_order:
                doc_data = cls.gr_has_no_pr(instance, doc_data, all_lots)
            if instance.work_order:
                doc_data = cls.gr_has_pr(instance, doc_data, all_lots)
        ReportInvLog.log(instance, instance.date_approved, doc_data)
        return True