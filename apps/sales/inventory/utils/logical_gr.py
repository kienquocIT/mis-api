from django.utils import timezone

from apps.core.diagram.models import DiagramSuffix
from apps.shared import DisperseModel


class GRHandler:
    @classmethod
    def push_diagram(cls, instance):
        data_push = {}
        list_reference = []
        if instance.purchase_order:
            list_reference.append(instance.purchase_order.code)
        for gr_pr_product in instance.goods_receipt_request_product_goods_receipt.all():
            if gr_pr_product.purchase_request_product and gr_pr_product.goods_receipt_product:
                if gr_pr_product.purchase_request_product.purchase_request:
                    if gr_pr_product.purchase_request_product.purchase_request.sale_order:
                        so_id = gr_pr_product.purchase_request_product.purchase_request.sale_order_id
                        quantity = gr_pr_product.quantity_import
                        total = gr_pr_product.goods_receipt_product.product_unit_price * quantity
                        if str(so_id) not in data_push:
                            data_push.update({
                                str(gr_pr_product.purchase_request_product.purchase_request.sale_order_id): {
                                    'quantity': quantity,
                                    'total': total,
                                }
                            })
                        else:
                            data_push[str(so_id)]['quantity'] += quantity
                            data_push[str(so_id)]['total'] += total
        for purchase_request in instance.purchase_requests.all():
            if purchase_request.sale_order:
                list_reference.reverse()
                reference = ", ".join(list_reference)
                DiagramSuffix.push_diagram_suffix(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    app_code_main=purchase_request.sale_order.__class__.get_model_code(),
                    doc_id_main=purchase_request.sale_order.id,
                    app_code=instance.__class__.get_model_code(),
                    doc_id=instance.id,
                    doc_data={
                        'id': str(instance.id),
                        'title': instance.title,
                        'code': instance.code,
                        'system_status': instance.system_status,
                        'date_created': str(instance.date_created),
                        # custom
                        'quantity': data_push.get(str(purchase_request.sale_order_id), {}).get('quantity', 0),
                        'total': data_push.get(str(purchase_request.sale_order_id), {}).get('total', 0),
                        'reference': reference,
                    }
                )
        return True


class GRFromPMHandler:
    @classmethod
    def create_new(cls, pm_obj, issue_data, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj):
        model_cls = DisperseModel(app_model='inventory.goodsreceipt').get_model()
        if pm_obj and model_cls and hasattr(model_cls, 'objects'):
            gr_products_data1 = GRFromPMHandler.setup_product(
                pm_obj, issue_data, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
            )
            if gr_products_data1:
                goods_receipt_obj = GRFromPMHandler.run_create(
                    pm_obj=pm_obj,
                    gr_products_data=gr_products_data1,
                    model_cls=model_cls,
                    system_status=3,
                )
                return goods_receipt_obj
            gr_products_data2 = GRFromPMHandler.setup_component(pm_obj=pm_obj)
            if gr_products_data2:
                goods_receipt_obj = GRFromPMHandler.run_create(
                    pm_obj=pm_obj,
                    gr_products_data=gr_products_data2,
                    model_cls=model_cls,
                    system_status=0,
                )
                return goods_receipt_obj
        return None

    @classmethod
    def setup_product(cls, pm_obj, issue_data, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj):
        new_logs = issue_data.get('new_logs', [])
        re_product_obj = pm_obj.representative_product_modified
        if re_product_obj:
            if pm_obj.product_modified and new_logs:
                uom_obj = None
                product_modified_value = 0
                value_plus = 0
                value_minus = 0
                for log in new_logs:
                    if log.product_id != pm_obj.product_modified_id:
                        if log.product_id == re_product_obj.id:
                            uom_obj = re_product_obj.inventory_uom
                            product_modified_value = log.value
                            for pm_product_obj in pm_obj.removed_components.all():
                                value_minus += pm_product_obj.fair_value * pm_product_obj.component_quantity
                        if log.product_id != re_product_obj.id:
                            value_plus += log.value
                return [{
                    'order': 1,
                    'product_id': str(re_product_obj.id),
                    'product_data': {
                        'id': str(re_product_obj.id),
                        'title': re_product_obj.title,
                        'code': re_product_obj.code,
                        'general_traceability_method': re_product_obj.general_traceability_method,
                        'description': re_product_obj.description,
                        'product_choice': re_product_obj.product_choice,
                    },
                    'uom_id': str(uom_obj.id) if uom_obj else None,
                    'uom_data': {
                        'id': str(uom_obj.id),
                        'title': uom_obj.title,
                        'code': uom_obj.code,
                        'uom_group': {
                            'id': str(uom_obj.group_id),
                            'title': uom_obj.group.title,
                            'code': uom_obj.group.code,
                            'uom_reference': {
                                'id': str(uom_obj.group.uom_reference_id),
                                'title': uom_obj.group.uom_reference.title,
                                'code': uom_obj.group.uom_reference.code,
                                'ratio': uom_obj.group.uom_reference.ratio,
                                'rounding': uom_obj.group.uom_reference.rounding,
                            } if uom_obj.group.uom_reference else {},
                        } if uom_obj.group else {},
                        'ratio': uom_obj.ratio,
                        'rounding': uom_obj.rounding,
                        'is_referenced_unit': uom_obj.is_referenced_unit,
                    } if uom_obj else {},
                    'product_unit_price': product_modified_value - value_minus + value_plus,
                    'product_quantity_order_actual': 1,
                    'quantity_import': 1,
                    'gr_warehouse_data': pm_obj.setup_representative_product_product_wh(
                        pm_obj, re_prd_prd_wh_obj, re_prd_prd_wh_lot_obj, re_prd_prd_wh_serial_obj
                    ),
                }]
        else:
            if pm_obj.product_modified and new_logs:
                uom_obj = None
                product_modified_value = 0
                value_plus = 0
                value_minus = 0
                for log in new_logs:
                    if log.product_id == pm_obj.product_modified_id:
                        uom_obj = pm_obj.product_modified.inventory_uom
                        product_modified_value = log.value
                        for pm_product_obj in pm_obj.removed_components.all():
                            value_minus += pm_product_obj.fair_value * pm_product_obj.component_quantity
                    if log.product_id != pm_obj.product_modified_id:
                        value_plus += log.value
                return [{
                    'order': 1,
                    'product_id': str(pm_obj.product_modified_id),
                    'product_data': {
                        'id': str(pm_obj.product_modified_id),
                        'title': pm_obj.product_modified.title,
                        'code': pm_obj.product_modified.code,
                        'general_traceability_method': pm_obj.product_modified.general_traceability_method,
                        'description': pm_obj.product_modified.description,
                        'product_choice': pm_obj.product_modified.product_choice,
                    },
                    'uom_id': str(uom_obj.id) if uom_obj else None,
                    'uom_data': {
                        'id': str(uom_obj.id),
                        'title': uom_obj.title,
                        'code': uom_obj.code,
                        'uom_group': {
                            'id': str(uom_obj.group_id),
                            'title': uom_obj.group.title,
                            'code': uom_obj.group.code,
                            'uom_reference': {
                                'id': str(uom_obj.group.uom_reference_id),
                                'title': uom_obj.group.uom_reference.title,
                                'code': uom_obj.group.uom_reference.code,
                                'ratio': uom_obj.group.uom_reference.ratio,
                                'rounding': uom_obj.group.uom_reference.rounding,
                            } if uom_obj.group.uom_reference else {},
                        } if uom_obj.group else {},
                        'ratio': uom_obj.ratio,
                        'rounding': uom_obj.rounding,
                        'is_referenced_unit': uom_obj.is_referenced_unit,
                    } if uom_obj else {},
                    'product_unit_price': product_modified_value - value_minus + value_plus,
                    'product_quantity_order_actual': 1,
                    'quantity_import': 1,
                    'gr_warehouse_data': GRFromPMHandler.setup_product_wh(pm_obj=pm_obj),
                }]
        return []

    @classmethod
    def setup_product_wh(cls, pm_obj):
        if pm_obj:
            if pm_obj.prd_wh:
                return [{
                    'warehouse_id': str(pm_obj.prd_wh.warehouse_id),
                    'warehouse_data': {
                        'id': str(pm_obj.prd_wh.warehouse_id),
                        'title': pm_obj.prd_wh.warehouse.title,
                        'code': pm_obj.prd_wh.warehouse.code,
                    } if pm_obj.prd_wh.warehouse else {},
                    'quantity_import': 1,
                    'serial_data': [{
                        'expire_date': str(pm_obj.prd_wh_serial.expire_date)
                        if pm_obj.prd_wh_serial.expire_date is not None else None,
                        'manufacture_date': str(pm_obj.prd_wh_serial.manufacture_date)
                        if pm_obj.prd_wh_serial.manufacture_date is not None else None,
                        'serial_number': pm_obj.prd_wh_serial.serial_number,
                        'vendor_serial_number': pm_obj.prd_wh_serial.vendor_serial_number,
                        'warranty_start': str(pm_obj.prd_wh_serial.warranty_start)
                        if pm_obj.prd_wh_serial.warranty_start is not None else None,
                        'warranty_end': str(pm_obj.prd_wh_serial.warranty_end)
                        if pm_obj.prd_wh_serial.warranty_end is not None else None,
                    }] if pm_obj.prd_wh_serial else [],
                    'lot_data': [{
                        "lot_number": pm_obj.prd_wh_lot.lot_number,
                        "expire_date": str(pm_obj.prd_wh_lot.expire_date)
                        if pm_obj.prd_wh_lot.expire_date is not None else None,
                        "manufacture_date": str(pm_obj.prd_wh_lot.manufacture_date)
                        if pm_obj.prd_wh_lot.manufacture_date is not None else None,
                        "quantity_import": 1,
                    }] if pm_obj.prd_wh_lot else [],
                }]
        return []

    @classmethod
    def setup_component(cls, pm_obj):
        gr_products_data = []
        order = 1
        for pm_product_obj in pm_obj.removed_components.all():
            if pm_product_obj.component_product:
                uom_obj = pm_product_obj.component_product.inventory_uom
                gr_products_data.append({
                    'order': order,
                    'product_modification_product_id': str(pm_product_obj.id),
                    'product_id': str(pm_product_obj.component_product_id),
                    'product_data': {
                        'id': str(pm_product_obj.component_product_id),
                        'title': pm_product_obj.component_product.title,
                        'code': pm_product_obj.component_product.code,
                        'general_traceability_method': pm_product_obj.component_product.general_traceability_method,
                        'description': pm_product_obj.component_product.description,
                        'product_choice': pm_product_obj.component_product.product_choice,
                    },
                    'uom_id': str(uom_obj.id) if uom_obj else None,
                    'uom_data': {
                        'id': str(uom_obj.id),
                        'title': uom_obj.title,
                        'code': uom_obj.code,
                        'uom_group': {
                            'id': str(uom_obj.group_id),
                            'title': uom_obj.group.title,
                            'code': uom_obj.group.code,
                            'uom_reference': {
                                'id': str(uom_obj.group.uom_reference_id),
                                'title': uom_obj.group.uom_reference.title,
                                'code': uom_obj.group.uom_reference.code,
                                'ratio': uom_obj.group.uom_reference.ratio,
                                'rounding': uom_obj.group.uom_reference.rounding,
                            } if uom_obj.group.uom_reference else {},
                        } if uom_obj.group else {},
                        'ratio': uom_obj.ratio,
                        'rounding': uom_obj.rounding,
                        'is_referenced_unit': uom_obj.is_referenced_unit,
                    } if uom_obj else {},
                    'product_unit_price': pm_product_obj.fair_value,
                    'product_quantity_order_actual': pm_product_obj.component_quantity,
                })
            order += 1
        return gr_products_data

    @classmethod
    def run_create(cls, pm_obj, gr_products_data, model_cls, system_status):
        data = {
            'title': pm_obj.code,
            'goods_receipt_type': 3,
            'date_received': timezone.now(),
            'product_modification_id': pm_obj.id,
            'product_modification_data': {
                'id': str(pm_obj.id),
                'title': pm_obj.title,
                'code': pm_obj.code,
                'date_created': str(pm_obj.date_created),
            },
            'gr_products_data': gr_products_data,
            'tenant_id': pm_obj.tenant_id,
            'company_id': pm_obj.company_id,
            'employee_inherit_id': pm_obj.employee_inherit_id,
            'employee_created_id': pm_obj.employee_created_id,
        }
        goods_receipt = model_cls.objects.create(**data)
        if goods_receipt:
            GRFromPMHandler.run_create_sub_product(goods_receipt=goods_receipt)
            if system_status == 3:
                products_data = goods_receipt.gr_products_data
                if len(products_data) == 1:
                    goods_receipt.total_pretax = products_data[0].get('product_unit_price', 0)
                    goods_receipt.total = products_data[0].get('product_unit_price', 0)
                    goods_receipt.total_revenue_before_tax = products_data[0].get('product_unit_price', 0)
                goods_receipt.system_status = 3
                goods_receipt.date_approved = timezone.now()
                goods_receipt.save(update_fields=[
                    'total_pretax', 'total', 'total_revenue_before_tax', 'system_status', 'date_approved'
                ])
        return goods_receipt

    @classmethod
    def run_create_sub_product(cls, goods_receipt):
        model_product_cls = DisperseModel(app_model='inventory.goodsreceiptproduct').get_model()
        if model_product_cls and hasattr(model_product_cls, 'objects'):
            for gr_product in goods_receipt.gr_products_data:
                new_gr_product = model_product_cls.objects.create(goods_receipt=goods_receipt, **gr_product)
                gr_warehouse_data = gr_product.get('gr_warehouse_data', [])
                GRFromPMHandler.run_create_sub_warehouse(
                    goods_receipt=goods_receipt, new_gr_product=new_gr_product, gr_warehouse_data=gr_warehouse_data
                )
        return True

    @classmethod
    def run_create_sub_warehouse(cls, goods_receipt, new_gr_product, gr_warehouse_data):
        for warehouse in gr_warehouse_data:
            lot_data = warehouse.get('lot_data', [])
            serial_data = warehouse.get('serial_data', [])
            model_warehouse_cls = DisperseModel(app_model='inventory.goodsreceiptwarehouse').get_model()
            if model_warehouse_cls and hasattr(model_warehouse_cls, 'objects'):
                new_warehouse = model_warehouse_cls.objects.create(
                    goods_receipt=goods_receipt,
                    goods_receipt_request_product=None,
                    goods_receipt_product=new_gr_product,
                    **warehouse
                )
                model_lot_cls = DisperseModel(app_model='inventory.goodsreceiptlot').get_model()
                if model_lot_cls and hasattr(model_lot_cls, 'objects'):
                    for lot in lot_data:
                        model_lot_cls.objects.create(
                            goods_receipt=goods_receipt,
                            goods_receipt_warehouse=new_warehouse,
                            **lot
                        )
                model_serial_cls = DisperseModel(app_model='inventory.goodsreceiptserial').get_model()
                if model_serial_cls and hasattr(model_serial_cls, 'objects'):
                    for serial in serial_data:
                        model_serial_cls.objects.create(
                            goods_receipt=goods_receipt,
                            goods_receipt_warehouse=new_warehouse,
                            **serial
                        )
        return True
