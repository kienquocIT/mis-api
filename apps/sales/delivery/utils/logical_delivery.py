from rest_framework import serializers

from apps.core.diagram.models import DiagramSuffix
from apps.shared.translations.sales import DeliverMsg


class DeliHandler:
    @classmethod
    def check_update_prod_and_emp(cls, instance, validate_data):
        crt_emp = str(instance.employee_inherit_id)
        is_same_emp = False
        if crt_emp == str(validate_data['employee_inherit_id']):
            is_same_emp = True
        if 'products' in validate_data and len(validate_data['products']) > 0 and not is_same_emp:
            raise serializers.ValidationError(
                {
                    'detail': DeliverMsg.ERROR_UPDATE_RULE
                }
            )
        return True

    @classmethod
    def push_diagram(cls, instance):
        quantity = 0
        total = 0
        list_reference = []
        for deli_product in instance.delivery_product_delivery_sub.all():  # for in product
            quantity += deli_product.picked_quantity
            total_all_wh = cls.diagram_get_total_cost_by_wh(deli_product=deli_product)
            total += total_all_wh
        if instance.order_delivery:
            if hasattr(instance.order_delivery, 'sale_order'):
                if instance.order_delivery.sale_order:
                    list_reference.append(instance.order_delivery.sale_order.code)
                    list_reference.reverse()
                    reference = ", ".join(list_reference)
                    DiagramSuffix.push_diagram_suffix(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        app_code_main=instance.order_delivery.sale_order.__class__.get_model_code(),
                        doc_id_main=instance.order_delivery.sale_order.id,
                        app_code=instance.__class__.get_model_code(),
                        doc_id=instance.id,
                        doc_data={
                            'id': str(instance.id),
                            'title': instance.title,
                            'code': instance.code,
                            'system_status': instance.system_status,
                            'date_created': str(instance.date_created),
                            # custom
                            'quantity': quantity,
                            'total': total,
                            'reference': reference,
                        }
                    )
        return True

    @classmethod
    def diagram_get_total_cost_by_wh(cls, deli_product):
        total_all_wh = 0
        product_obj, delivery_data = deli_product.product, deli_product.delivery_data
        if product_obj:
            if len(delivery_data) == 0:
                return deli_product.picked_quantity * deli_product.product_unit_price
            for data_deli in delivery_data:  # for in warehouse to get cost of warehouse
                quantity_deli = data_deli.get('picked_quantity', 0)
                cost = product_obj.get_unit_cost_by_warehouse(warehouse_id=data_deli.get('warehouse_id', None), get_type=1)
                total_all_wh += cost * quantity_deli

        return total_all_wh

    @classmethod
    def get_final_uom_ratio(cls, product_obj, uom_transaction):
        if product_obj.general_uom_group:
            uom_base = product_obj.general_uom_group.uom_reference
            if uom_base and uom_transaction:
                return uom_transaction.ratio / uom_base.ratio if uom_base.ratio > 0 else 1
        return 1
