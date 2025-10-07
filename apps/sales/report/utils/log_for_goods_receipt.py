from apps.masterdata.saledata.models import ProductWareHouseLot, ProductWareHouseSerial
from apps.masterdata.saledata.models.product_warehouse import ProductSpecificIdentificationSerial
from apps.sales.report.utils.inventory_log import ReportInvLog, ReportInvCommonFunc


class HasPurchaseRequestHandler:
    @classmethod
    def combine_data_none(cls, prd_wh, gr_item, sale_order, instance, doc_data):
        casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(gr_item.uom, prd_wh.quantity_import)
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
        return doc_data

    @classmethod
    def combine_data_lot(cls, prd_wh, gr_item, sale_order, instance, doc_data):
        all_lot = IRForGoodsReceiptHandler.get_all_lot(instance)
        for item in prd_wh.goods_receipt_lot_gr_warehouse.all():
            lot_mapped = all_lot.filter(lot_number=item.lot_number).first()
            if lot_mapped:
                casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(gr_item.uom, item.quantity_import)
                casted_cost = (
                        gr_item.product_unit_price * item.quantity_import / casted_quantity
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
                        'lot_number': item.lot_number,
                        'lot_expire_date': str(item.expire_date) if item.expire_date else None
                    }
                })
        return doc_data

    @classmethod
    def combine_data_serial(cls, prd_wh, gr_item, sale_order, instance, doc_data):
        all_serial = IRForGoodsReceiptHandler.get_all_serial(instance)
        if gr_item.product.valuation_method == 2:
            for item in prd_wh.goods_receipt_serial_gr_warehouse.all():
                serial_mapped = all_serial.filter(serial_number=item.serial_number).first()
                if serial_mapped:
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
                        'quantity': 1,
                        'cost': gr_item.product_unit_price,
                        'value': gr_item.product_unit_price * 1,
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

                    # cập nhập hoặc tạo giá đich danh khi nhập
                    ProductSpecificIdentificationSerial.create_or_update_si_product_serial(
                        product=gr_item.product,
                        serial_obj=serial_mapped,
                        specific_value=gr_item.product_unit_price
                    )
        else:
            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(gr_item.uom, prd_wh.quantity_import)
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
        return doc_data

    @classmethod
    def combine_doc_data(cls, instance):
        doc_data = []
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
                for prd_wh in pr_item.goods_receipt_warehouse_request_product.all():
                    if gr_item.product.general_traceability_method == 0:
                        doc_data = cls.combine_data_none(prd_wh, gr_item, sale_order, instance, doc_data)
                    elif gr_item.product.general_traceability_method == 1:
                        doc_data = cls.combine_data_lot(prd_wh, gr_item, sale_order, instance, doc_data)
                    elif gr_item.product.general_traceability_method == 2:
                        doc_data = cls.combine_data_serial(prd_wh, gr_item, sale_order, instance, doc_data)
        return doc_data


class NoPurchaseRequestHandler:
    @classmethod
    def combine_data_none(cls, goods_receipt_warehouses, gr_item, instance, doc_data):
        for gr_prd_wh in goods_receipt_warehouses.filter(goods_receipt_product__product=gr_item.product):
            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(gr_item.uom, gr_prd_wh.quantity_import)
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
        return doc_data

    @classmethod
    def combine_data_lot(cls, goods_receipt_warehouses, gr_item, instance, doc_data):
        all_lot = IRForGoodsReceiptHandler.get_all_lot(instance)
        for gr_prd_wh in goods_receipt_warehouses.filter(goods_receipt_product__product=gr_item.product):
            for lot in gr_prd_wh.goods_receipt_lot_gr_warehouse.all():
                lot_mapped = all_lot.filter(lot_number=lot.lot_number).first()
                if lot_mapped:
                    casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(gr_item.uom, lot.quantity_import)
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
    def combine_data_serial(cls, goods_receipt_warehouses, gr_item, instance, doc_data):
        all_serial = IRForGoodsReceiptHandler.get_all_serial(instance)
        if gr_item.product.valuation_method == 2:
            for gr_prd_wh in goods_receipt_warehouses.filter(goods_receipt_product__product=gr_item.product):
                for item in gr_prd_wh.goods_receipt_serial_gr_warehouse.all():
                    serial_mapped = all_serial.filter(serial_number=item.serial_number).first()
                    if serial_mapped:
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
                            'quantity': 1,
                            'cost': gr_item.product_unit_price,
                            'value': gr_item.product_unit_price * 1,
                            'lot_data': {},
                            'serial_data': {
                                'serial_id': str(serial_mapped.id),
                                'serial_number': serial_mapped.serial_number,
                                'vendor_serial_number': serial_mapped.vendor_serial_number,
                                'expire_date': str(
                                    serial_mapped.expire_date
                                ) if serial_mapped.expire_date else None,
                                'manufacture_date': str(
                                    serial_mapped.manufacture_date
                                ) if serial_mapped.manufacture_date else None,
                                'warranty_start': str(
                                    serial_mapped.warranty_start
                                ) if serial_mapped.expire_dwarranty_startate else None,
                                'warranty_end': str(
                                    serial_mapped.warranty_end
                                ) if serial_mapped.warranty_end else None,
                            }
                        })

                        # cập nhập hoặc tạo giá đich danh khi nhập
                        ProductSpecificIdentificationSerial.create_or_update_si_product_serial(
                            product=gr_item.product,
                            serial_obj=serial_mapped,
                            specific_value=gr_item.product_unit_price
                        )
        else:
            for gr_prd_wh in goods_receipt_warehouses.filter(goods_receipt_product__product=gr_item.product):
                casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(gr_item.uom, gr_prd_wh.quantity_import)
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
        return doc_data

    @classmethod
    def combine_doc_data(cls, instance):
        doc_data = []
        goods_receipt_warehouses = instance.goods_receipt_warehouse_goods_receipt.all()
        for gr_item in instance.goods_receipt_product_goods_receipt.all():
            if gr_item.product.general_traceability_method == 0:  # none
                doc_data = cls.combine_data_none(goods_receipt_warehouses, gr_item, instance, doc_data)
            elif gr_item.product.general_traceability_method == 1:  # lot
                doc_data = cls.combine_data_lot(goods_receipt_warehouses, gr_item, instance, doc_data)
            elif gr_item.product.general_traceability_method == 2:  # serial
                doc_data = cls.combine_data_serial(goods_receipt_warehouses, gr_item, instance, doc_data)
        return doc_data


class IRForGoodsReceiptHandler:
    @classmethod
    def get_all_lot(cls, instance):
        all_lot_in_gr = list({item.lot_number for item in instance.goods_receipt_lot_goods_receipt.all()})
        all_lot = ProductWareHouseLot.objects.filter(lot_number__in=all_lot_in_gr)
        return all_lot

    @classmethod
    def get_all_serial(cls, instance):
        all_serial_in_gr = list({item.serial_number for item in instance.goods_receipt_serial_goods_receipt.all()})
        all_serial = ProductWareHouseSerial.objects.filter(serial_number__in=all_serial_in_gr)
        return all_serial

    @classmethod
    def push_to_inventory_report(cls, instance):
        """ Chuẩn bị data để ghi vào báo cáo tồn kho và tính giá Cost """
        if instance.goods_receipt_type in [0, 1, 3]:  # GR by PO/IA
            if instance.goods_receipt_pr_goods_receipt.count() == 0:
                doc_data = NoPurchaseRequestHandler.combine_doc_data(instance)
                ReportInvLog.log(instance, instance.date_approved, doc_data)
            else:
                doc_data = HasPurchaseRequestHandler.combine_doc_data(instance)
                ReportInvLog.log(instance, instance.date_approved, doc_data)
        if instance.goods_receipt_type == 2:  # GR by Production
            if instance.production_order:
                doc_data = NoPurchaseRequestHandler.combine_doc_data(instance)
                ReportInvLog.log(instance, instance.date_approved, doc_data)
            if instance.work_order:
                doc_data = HasPurchaseRequestHandler.combine_doc_data(instance)
                ReportInvLog.log(instance, instance.date_approved, doc_data)
        return True
