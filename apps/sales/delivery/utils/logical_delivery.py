from rest_framework import serializers

from apps.core.diagram.models import DiagramSuffix
from apps.masterdata.saledata.models import UnitOfMeasure, ProductWareHouse, Product
from apps.sales.delivery.models import DeliveryConfig
from apps.shared.translations.sales import DeliverMsg


class DeliHandler:
    @classmethod
    def minus_tock(cls, source, target, config):
        # sản phầm trong phiếu
        # source: dict { uom: uuid, quantity: number }
        # sản phẩm trong kho
        # target: object of warehouse has prod (all prod)
        # kiểm tra kho còn hàng và trừ kho nếu ko đủ return failure
        if 'is_fifo_lifo' in config and config['is_fifo_lifo']:
            target = target.reverse()
        is_done = False
        list_update = []
        for item in target:
            if is_done:
                # nếu trừ đủ update vào warehouse, return true
                break
            final_ratio = 1
            uom_base = item.uom
            uom_delivery = UnitOfMeasure.objects.filter(id=source['uom']).first()
            if uom_base and uom_delivery:
                if uom_base.ratio > 0:
                    final_ratio = uom_delivery.ratio / uom_base.ratio
            delivery_quantity = source['quantity'] * final_ratio
            if item.stock_amount > 0:
                # số lượng trong kho đã quy đổi
                calc = item.stock_amount - delivery_quantity
                if calc >= 0:
                    # đủ hàng
                    is_done = True
                    item_sold = delivery_quantity
                    item.sold_amount += item_sold
                    item.stock_amount = item.receipt_amount - item.sold_amount
                    if config['is_picking']:
                        item.picked_ready = item.picked_ready - item_sold
                    list_update.append(item)
                # elif calc < 0:
                #     # else < 0 ko đù
                #     # gán số còn thiếu cho số lượng cần trừ kho (mediate_number_clone)
                #     # trừ kho tất cả của record này
                #     item.sold_amount += item.stock_amount
                #     item.stock_amount = item.receipt_amount - item.sold_amount
                #     if config['is_picking']:
                #         item.picked_ready = item.picked_ready - item.stock_amount
                #     list_update.append(item)
        ProductWareHouse.objects.bulk_update(list_update, fields=['sold_amount', 'picked_ready', 'stock_amount'])
        return True

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
    def push_product_warehouse(cls, instance):
        config = instance.config_at_that_point
        if not config:
            get_config = DeliveryConfig.objects.filter(company_id=instance.company_id).first()
            if get_config:
                config = {
                    "is_picking": get_config.is_picking,
                    "is_partial_ship": get_config.is_partial_ship
                }
        for deli_product in instance.delivery_product_delivery_sub.all():
            if deli_product.product and deli_product.delivery_data:
                for data in deli_product.delivery_data:
                    if all(key in data for key in ('warehouse', 'uom', 'stock')):
                        product_warehouse = ProductWareHouse.objects.filter(
                            tenant_id=instance.tenant_id,
                            company_id=instance.company_id,
                            product_id=deli_product.product_id,
                            warehouse_id=data['warehouse'],
                        )
                        source = {
                            "uom": data['uom'],
                            "quantity": data['stock']
                        }
                        DeliHandler.minus_tock(source, product_warehouse, config)
        return True

    @classmethod
    def push_diagram(cls, instance, validated_product):
        quantity = 0
        total = 0
        list_reference = []
        for product in validated_product:  # for product
            if all(key in product for key in ('product_id', 'delivery_data', 'done')):
                quantity += product.get('done', 0)
                product_obj = Product.objects.filter(id=product.get('product_id', None)).first()
                if product_obj:
                    total_all_wh = 0
                    for data_deli in product['delivery_data']:  # for warehouse
                        total_all_wh += product_obj.get_unit_cost_by_warehouse(
                            warehouse_id=data_deli.get('warehouse', None), get_type=1
                        )
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
                        'system_status': instance.system_status,
                        'date_created': str(instance.date_created),
                        # custom
                        'quantity': quantity,
                        'total': total,
                        'reference': reference,
                    }
                )
        return True
