from apps.core.diagram.models import DiagramSuffix


class ReturnHandler:

    @classmethod
    def push_diagram(cls, instance):
        quantity = 0
        total = 0
        list_reference = []
        if instance.delivery:
            list_reference.append(instance.delivery.code)
        for return_product in instance.goods_return_product_detail.all():
            if return_product.type == 0:  # no lot/serial
                quantity_sub, cost = cls.setup_return_quantity_value(return_product=return_product, instance=instance)
                quantity += quantity_sub
                total += cost
            if return_product.type == 1:  # lot
                quantity_sub, cost = cls.setup_return_quantity_value_lot(return_product=return_product)
                quantity += quantity_sub
                total += cost
            if return_product.type == 2:  # serial
                quantity_sub, cost = cls.setup_return_quantity_value_serial(return_product=return_product)
                quantity += quantity_sub
                total += cost
        if instance.sale_order:
            list_reference.append(instance.sale_order.code)
            list_reference.reverse()
            reference = ", ".join(list_reference)
            DiagramSuffix.push_diagram_suffix(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                app_code_main=instance.sale_order.__class__.get_model_code(),
                doc_id_main=instance.sale_order_id,
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
    def setup_return_quantity_value(cls, return_product, instance):
        if return_product.delivery_item:
            if return_product.delivery_item.product and instance.return_to_warehouse:
                product_obj = return_product.delivery_item.product
                cost = product_obj.get_unit_cost_by_warehouse(warehouse_id=instance.return_to_warehouse_id, get_type=1)
                return return_product.default_return_number, cost * return_product.default_return_number
        return 0, 0

    @classmethod
    def setup_return_quantity_value_lot(cls, return_product):
        if return_product.lot_no:
            if return_product.lot_no.product_warehouse:
                product_obj = return_product.lot_no.product_warehouse.product
                if product_obj:
                    cost = product_obj.get_unit_cost_by_warehouse(
                        warehouse_id=return_product.lot_no.product_warehouse.warehouse_id, get_type=1
                    )
                    return return_product.lot_return_number, cost * return_product.lot_return_number
        return 0, 0

    @classmethod
    def setup_return_quantity_value_serial(cls, return_product):
        if return_product.serial_no:
            if return_product.serial_no.product_warehouse:
                product_obj = return_product.serial_no.product_warehouse.product
                if product_obj:
                    return 1, product_obj.get_unit_cost_by_warehouse(
                        warehouse_id=return_product.serial_no.product_warehouse.warehouse_id, get_type=1
                    )
        return 0, 0
