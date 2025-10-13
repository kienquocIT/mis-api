from apps.sales.report.models import ReportStockLog
from apps.sales.report.utils.inventory_log import ReportInvLog, ReportInvCommonFunc


class IRForGoodsReturnHandler:
    @classmethod
    def check_exists(cls, doc_data, data):
        for item in doc_data:
            if all([
                data['product'] == item['product'], data['warehouse'] == item['warehouse'],
                data['system_date'] == item['system_date'], data['posting_date'] == item['posting_date'],
                data['document_date'] == item['document_date'], data['stock_type'] == item['stock_type'],
                data['trans_id'] == item['trans_id'], data['trans_code'] == item['trans_code'],
                data['trans_title'] == item['trans_title']
            ]):
                item['quantity'] += data['quantity']
                item['value'] += item['quantity'] * item['cost']
                return doc_data, True
        return doc_data, False

    @classmethod
    def for_none(cls, instance, product_detail_list, doc_data):
        for item in product_detail_list.filter(type=0):
            delivery_item = ReportStockLog.objects.filter(
                product=item.product, trans_id=str(instance.delivery_id)
            ).first()
            if delivery_item:
                casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(item.uom, item.default_return_number)
                casted_cost = (
                    delivery_item.cost * item.default_return_number / casted_quantity
                ) if casted_quantity > 0 else 0
                data = {
                    'sale_order': instance.delivery.order_delivery.sale_order,
                    'product': item.product,
                    'warehouse': item.return_to_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods return',
                    'quantity': casted_quantity,
                    'cost': casted_cost,
                    'value': casted_quantity * casted_cost,
                    'lot_data': {}
                }
                doc_data, is_append = cls.check_exists(doc_data, data)
                if not is_append:
                    doc_data.append(data)
            else:
                print('Delivery information is not found. Can not log.')
        return doc_data

    @classmethod
    def for_lot(cls, instance, product_detail_list, doc_data):
        for item in product_detail_list.filter(type=1):
            delivery_item = ReportStockLog.objects.filter(
                product=item.product, trans_id=str(instance.delivery_id)
            ).first()
            if delivery_item:
                casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(item.uom, item.lot_return_number)
                casted_cost = (
                        delivery_item.cost * item.lot_return_number / casted_quantity
                ) if casted_quantity > 0 else 0
                data = {
                    'sale_order': instance.delivery.order_delivery.sale_order,
                    'product': item.product,
                    'warehouse': item.return_to_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods return',
                    'quantity': casted_quantity,
                    'cost': casted_cost,
                    'value': casted_quantity * casted_cost,
                    'lot_data': {
                        'lot_id': str(item.lot_no_id),
                        'lot_number': item.lot_no.lot_number,
                        'lot_expire_date': str(item.lot_no.expire_date) if item.lot_no.expire_date else None
                    }
                }
                doc_data, is_append = cls.check_exists(doc_data, data)
                if not is_append:
                    doc_data.append(data)
            else:
                print('Delivery information is not found. Can not log.')
        return doc_data

    @classmethod
    def for_serial(cls, instance, product_detail_list, doc_data):
        for item in product_detail_list.filter(type=2):
            if item.product.valuation_method == 2 or item.product.product_si_serial_number.exists():
                serial_obj = item.serial_no
                delivery_item = ReportStockLog.objects.filter(
                    product=item.product, trans_id=str(instance.delivery_id), serial_number=serial_obj.serial_number
                ).first()
                if delivery_item:
                    data = {
                        'sale_order': instance.delivery.order_delivery.sale_order,
                        'product': item.product,
                        'warehouse': item.return_to_warehouse,
                        'system_date': instance.date_approved,
                        'posting_date': instance.date_approved,
                        'document_date': instance.date_approved,
                        'stock_type': 1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'trans_title': 'Goods return',
                        'quantity': 1,
                        'cost': delivery_item.cost,
                        'value': delivery_item.cost * 1,
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
                    }
                    doc_data, is_append = cls.check_exists(doc_data, data)
                    if not is_append:
                        doc_data.append(data)
                else:
                    print('Delivery information is not found. Can not log.')
            else:
                delivery_item = ReportStockLog.objects.filter(
                    product=item.product, trans_id=str(instance.delivery_id)
                ).first()
                if delivery_item:
                    data = {
                        'sale_order': instance.delivery.order_delivery.sale_order,
                        'product': item.product,
                        'warehouse': item.return_to_warehouse,
                        'system_date': instance.date_approved,
                        'posting_date': instance.date_approved,
                        'document_date': instance.date_approved,
                        'stock_type': 1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'trans_title': 'Goods return',
                        'quantity': 1,
                        'cost': delivery_item.cost,
                        'value': delivery_item.cost,
                        'lot_data': {}
                    }
                    doc_data, is_append = cls.check_exists(doc_data, data)
                    if not is_append:
                        doc_data.append(data)
                else:
                    print('Delivery information is not found. Can not log.')
        return doc_data

    @classmethod
    def for_perpetual_inventory(cls, instance):
        product_detail_list = instance.goods_return_product_detail.all()
        doc_data = []
        doc_data = cls.for_none(instance, product_detail_list, doc_data)
        doc_data = cls.for_lot(instance, product_detail_list, doc_data)
        doc_data = cls.for_serial(instance, product_detail_list, doc_data)
        return doc_data

    @classmethod
    def for_periodic_inventory(cls, instance):
        product_detail_list = instance.goods_return_product_detail.all()
        doc_data = []
        for item in product_detail_list.filter(type=0):
            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(item.uom, item.default_return_number)
            casted_cost = (
                    item.cost_for_periodic * item.default_return_number / casted_quantity
            ) if casted_quantity > 0 else 0
            doc_data.append({
                'sale_order': instance.delivery.order_delivery.sale_order,
                'product': item.product,
                'warehouse': item.return_to_warehouse,
                'system_date': instance.date_approved,
                'posting_date': instance.date_approved,
                'document_date': instance.date_approved,
                'stock_type': 1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Goods return',
                'quantity': casted_quantity,
                'cost': casted_cost,
                'value': casted_quantity * casted_cost,
                'lot_data': {}
            })
        for item in product_detail_list.filter(type=1):
            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(item.uom, item.lot_return_number)
            casted_cost = (
                    item.cost_for_periodic * item.lot_return_number / casted_quantity
            ) if casted_quantity > 0 else 0
            doc_data.append({
                'sale_order': instance.delivery.order_delivery.sale_order,
                'product': item.product,
                'warehouse': item.return_to_warehouse,
                'system_date': instance.date_approved,
                'posting_date': instance.date_approved,
                'document_date': instance.date_approved,
                'stock_type': 1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Goods return',
                'quantity': casted_quantity,
                'cost': casted_cost,
                'value': casted_quantity * casted_cost,
                'lot_data': {
                    'lot_id': str(item.lot_no_id),
                    'lot_number': item.lot_no.lot_number,
                    'lot_expire_date': str(item.lot_no.expire_date) if item.lot_no.expire_date else None
                }
            })
        for item in product_detail_list.filter(type=2):
            if item.product.valuation_method == 2 or item.product.product_si_serial_number.exists():
                serial_obj = item.serial_no
                doc_data.append({
                    'sale_order': instance.delivery.order_delivery.sale_order,
                    'product': item.product,
                    'warehouse': item.return_to_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods return',
                    'quantity': 1,
                    'cost': item.cost_for_periodic,
                    'value': item.cost_for_periodic,
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
                doc_data.append({
                    'sale_order': instance.delivery.order_delivery.sale_order,
                    'product': item.product,
                    'warehouse': item.return_to_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods return',
                    'quantity': 1,
                    'cost': item.cost_for_periodic,
                    'value': item.cost_for_periodic,
                    'lot_data': {}
                })
        return doc_data

    @classmethod
    def push_to_inventory_report(cls, instance):
        """ Chuẩn bị data để ghi vào báo cáo tồn kho và tính giá Cost """
        if instance.company.company_config.definition_inventory_valuation == 0:
            doc_data = cls.for_perpetual_inventory(instance)
        else:
            doc_data = cls.for_periodic_inventory(instance)
        ReportInvLog.log(instance, instance.date_created, doc_data)
        return True
