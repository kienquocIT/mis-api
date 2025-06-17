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

    @classmethod
    def create_from_product_modification(cls, pm_obj, issue_data):
        model_cls = DisperseModel(app_model='inventory.goodsreceipt').get_model()
        if pm_obj and model_cls and hasattr(model_cls, 'objects'):
            gr_products_data1 = GRHandler.setup_product_modification_product(pm_obj=pm_obj, issue_data=issue_data)
            if gr_products_data1:
                gr_products_data2 = GRHandler.setup_product_modification_component(pm_obj=pm_obj)
                gr_products_data1 += gr_products_data2
                GRHandler.run_create_from_product_modification(
                    pm_obj=pm_obj,
                    gr_products_data=gr_products_data1,
                    model_cls=model_cls,
                )
        return True

    @classmethod
    def setup_product_modification_product(cls, pm_obj, issue_data):
        new_logs = issue_data.get('new_logs', [])
        if pm_obj.product_modified and new_logs:
            for log in new_logs:
                if log.product_id == pm_obj.product_modified_id:
                    uom_obj = pm_obj.product_modified.inventory_uom
                    price_minus = 0
                    for pm_product_obj in pm_obj.removed_components.all():
                        price_minus += pm_product_obj.fair_value * pm_product_obj.component_quantity
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
                        'product_unit_price': log.cost - price_minus,
                        'product_quantity_order_actual': 1,
                    }]
        return []

    @classmethod
    def setup_product_modification_component(cls, pm_obj):
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
    def run_create_from_product_modification(cls, pm_obj, gr_products_data, model_cls):
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
        }
        goods_receipt = model_cls.objects.create(**data)
        model_product_cls = DisperseModel(app_model='inventory.goodsreceiptproduct').get_model()
        if goods_receipt and model_product_cls and hasattr(model_product_cls, 'objects'):
            for gr_product in goods_receipt.gr_products_data:
                model_product_cls.objects.create(goods_receipt=goods_receipt, **gr_product)
        return True
