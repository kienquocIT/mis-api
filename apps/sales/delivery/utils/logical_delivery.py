from rest_framework import serializers

from apps.core.diagram.models import DiagramSuffix
from apps.masterdata.saledata.models import Product
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
    def push_diagram(cls, instance, validated_product):
        quantity = 0
        total = 0
        list_reference = []
        for product_data in validated_product:  # for in product
            if all(key in product_data for key in ('product_id', 'delivery_data', 'done')):
                quantity += product_data.get('done', 0)
                product_obj = Product.objects.filter(id=product_data.get('product_id', None)).first()
                if product_obj:
                    total_all_wh = cls.diagram_get_total_cost_by_wh(product_obj=product_obj, product_data=product_data)
                    total += total_all_wh
        if instance.order_delivery:
            if hasattr(instance.order_delivery, 'sale_order'):
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
                        'system_status': 3,
                        'date_created': str(instance.date_created),
                        # custom
                        'quantity': quantity,
                        'total': total,
                        'reference': reference,
                    }
                )
        return True

    @classmethod
    def diagram_get_total_cost_by_wh(cls, product_obj, product_data):
        total_all_wh = 0
        for data_deli in product_data['delivery_data']:  # for in warehouse to get cost of warehouse
            lot_data = data_deli.get('lot_data', [])
            serial_data = data_deli.get('serial_data', [])
            quantity_deli = 0
            if lot_data:
                for lot in lot_data:
                    quantity_deli += lot.get('quantity_delivery')
            if serial_data:
                quantity_deli = len(serial_data)
            cost = product_obj.get_unit_cost_by_warehouse(warehouse_id=data_deli.get('warehouse', None), get_type=1)
            total_all_wh += cost * quantity_deli
        return total_all_wh

    @classmethod
    def get_final_uom_ratio(cls, product_obj, uom_transaction):
        if product_obj.general_uom_group:
            uom_base = product_obj.general_uom_group.uom_reference
            if uom_base and uom_transaction:
                return uom_transaction.ratio / uom_base.ratio if uom_base.ratio > 0 else 1
        return 1
