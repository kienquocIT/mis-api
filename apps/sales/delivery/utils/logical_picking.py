from django.utils import timezone
from rest_framework import serializers

from apps.masterdata.saledata.models import UnitOfMeasure, ProductWareHouse
from apps.shared import DisperseModel
from apps.shared.translations.sales import DeliverMsg


class PickingHandler:
    # PRODUCT WAREHOUSE
    @classmethod
    def push_pw_picked_ready(cls, instance, product_update):
        prod_id_temp = {}
        prod_wh_update = []
        for key, value in product_update.items():
            delivery_data = value['delivery_data'][0]
            key_prod = key.split('___')[0]
            if key_prod not in prod_id_temp:
                prod_id_temp[key_prod] = value['stock']
            else:
                prod_id_temp[key_prod] += value['stock']
            picked_uom = UnitOfMeasure.objects.filter(id=delivery_data['uom']).first()
            prod_warehouse = ProductWareHouse.objects.filter(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product_id=key_prod,
                warehouse_id=delivery_data['warehouse']
            ).first()
            if prod_warehouse:
                if prod_warehouse.product and prod_warehouse.warehouse and picked_uom:
                    final_ratio = cls.get_final_uom_ratio(
                        product_obj=prod_warehouse.product, uom_transaction=picked_uom
                    )
                    picked_unit = prod_id_temp[key_prod] * final_ratio
                    in_stock = prod_warehouse.stock_amount
                    in_stock = in_stock - prod_warehouse.picked_ready
                    if in_stock > 0 and in_stock >= picked_unit:
                        prod_warehouse.picked_ready += picked_unit
                        prod_wh_update.append(prod_warehouse)
                    else:
                        raise serializers.ValidationError({'products': DeliverMsg.ERROR_OUT_STOCK})
                    # case regis
                    PickingHandler.push_regis_picked_ready(value=value, prod_warehouse=prod_warehouse)
        ProductWareHouse.objects.bulk_update(prod_wh_update, fields=['picked_ready'])
        return True

    @classmethod
    def push_regis_picked_ready(cls, value, prod_warehouse):
        for picking_data in value.get('picking_data', []):
            prod_regis = prod_warehouse.warehouse.gre_item_prd_wh_warehouse.filter(
                gre_item__so_item__sale_order_id=picking_data.get('sale_order', None),
                gre_item__product_id=prod_warehouse.product_id,
            ).first()
            if prod_regis:
                prod_regis.picked_ready += picking_data.get('done', 0)
                prod_regis.save(update_fields=['picked_ready'])
        return True

    @classmethod
    def update_picking_to_delivery_prod(cls, instance, total, product_update):
        if instance.order_picking:
            if instance.order_picking.sale_order:
                if instance.order_picking.sale_order.delivery_of_sale_order:
                    delivery_sub = instance.order_picking.sale_order.delivery_of_sale_order.sub
                    # update stock cho delivery prod
                    obj_update = []
                    # loop trong picking product
                    for key, value in product_update.items():
                        delivery_data = value['delivery_data'][0]
                        key_prod = key.split('___')[0]
                        picking_data = value.get('picking_data', [])
                        delivery_prod = delivery_sub.delivery_product_delivery_sub.filter(
                            product_id=key_prod,
                            uom_id=delivery_data['uom'],
                            order=key.split('___')[1]
                        ).first()
                        if delivery_prod and len(picking_data) > 0:
                            # cộng vào stock cho delivery prod
                            delivery_prod.ready_quantity += value['stock']
                            delivery_prod.delivery_data.append(delivery_data)
                            obj_update.append(delivery_prod)

                    PickingHandler.push_pw_picked_ready(instance, product_update)
                    model_deli_product = DisperseModel(app_model='delivery.orderdeliveryproduct').get_model()
                    if model_deli_product and hasattr(model_deli_product, 'objects'):
                        model_deli_product.objects.bulk_update(obj_update, fields=['ready_quantity', 'delivery_data'])
                    # update ready stock cho delivery sub
                    delivery_sub.ready_quantity += total
                    if instance.delivery_option == 1 or instance.remaining_quantity == total:
                        delivery_sub.state = 1

                    delivery_sub.estimated_delivery_date = instance.estimated_delivery_date
                    delivery_sub.save(update_fields=['state', 'estimated_delivery_date', 'ready_quantity'])
        return True

    @classmethod
    def update_prod_current(cls, instance, prod_update, total_picked):
        pickup_data_temp = {}
        for key, item in prod_update.items():
            delivery_data = item['delivery_data'][0]
            key_prod = key.split('___')[0]
            # mỗi phiếu picking chỉ có 1 product match với warehouse nên có thể lấy value 0 của list delivery_data
            this_prod = instance.picking_product_picking_sub.filter(
                product_id=key_prod,
                uom_id=delivery_data['uom'],
                order=key.split('___')[1]
            ).first()
            if this_prod:
                pickup_data_temp[key] = {
                    'remaining_quantity': this_prod.remaining_quantity,
                    'picked_quantity': item['stock'],
                    'pickup_quantity': this_prod.pickup_quantity,
                    'picked_quantity_before': this_prod.picked_quantity_before
                }
                this_prod.picking_data = item.get('picking_data', [])
                if len(this_prod.picking_data) > 0:
                    this_prod.picked_quantity = item['stock']

                this_prod.save(update_fields=['picked_quantity', 'picking_data'])

        PickingHandler.update_picking_to_delivery_prod(instance, total_picked, prod_update)

        if total_picked > instance.remaining_quantity:
            raise serializers.ValidationError(
                {'products': DeliverMsg.ERROR_QUANTITY}
            )
        return pickup_data_temp

    @classmethod
    def create_new_picking_sub(cls, instance):
        picking = instance.order_picking
        remaining_quantity = instance.pickup_quantity - (instance.picked_quantity_before + instance.picked_quantity)
        # create new sub follow by prev sub
        model_picking_sub = DisperseModel(app_model='delivery.orderpickingsub').get_model()
        if model_picking_sub and hasattr(model_picking_sub, 'objects'):
            new_sub = model_picking_sub.objects.create(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                order_picking=picking,
                date_done=None,
                previous_step=instance,
                times=instance.times + 1,
                pickup_quantity=instance.pickup_quantity,
                picked_quantity_before=instance.picked_quantity_before + instance.picked_quantity,
                remaining_quantity=remaining_quantity,
                picked_quantity=0,
                pickup_data=instance.pickup_data,
                sale_order_data=picking.sale_order_data,
                delivery_option=instance.delivery_option,
                config_at_that_point=instance.config_at_that_point,
                employee_inherit=instance.employee_inherit
            )
            picking.sub = new_sub
            picking.save(update_fields=['sub'])
            # create prod with new sub id
            obj_new_prod = []
            model_picking_product = DisperseModel(app_model='delivery.orderpickingproduct').get_model()
            if model_picking_product and hasattr(model_picking_product, 'objects'):
                for key, value in instance.pickup_data.items():
                    old_obj = instance.picking_product_picking_sub.filter(product_id=key.split('___')[0]).first()
                    if old_obj:
                        quantity_before = value.get('picked_quantity_before', 0) + value.get('picked_quantity', 0)
                        remaining_quantity = value.get('pickup_quantity', 0) - quantity_before
                        new_item = old_obj.setup_new_obj(
                            old_obj=old_obj,
                            new_sub=new_sub,
                            pickup_quantity=value.get('pickup_quantity', 0),
                            picked_quantity_before=quantity_before,
                            remaining_quantity=remaining_quantity,
                        )
                        obj_new_prod.append(new_item)
                model_picking_product.objects.bulk_create(obj_new_prod)
        return True

    @classmethod
    def update_current_sub(cls, instance, pickup_data, total):
        # update sub after update product
        instance.date_done = timezone.now()
        instance.pickup_data = pickup_data
        instance.picked_quantity = total
        instance.state = 1
        instance.save(
            update_fields=['picked_quantity', 'pickup_data', 'ware_house', 'ware_house_data', 'to_location', 'remarks',
                           'date_done', 'state', 'estimated_delivery_date']
        )
        if 0 < total < instance.remaining_quantity:
            # giao hàng nhiều lần
            # update current sub
            # tạo mới sub and tạo mới prod, gán sub cho prod picking
            cls.create_new_picking_sub(instance)
        if total == instance.remaining_quantity:
            picking = instance.order_picking
            picking.state = 1
            picking.save(update_fields=['state'])
        return True

    @classmethod
    def get_final_uom_ratio(cls, product_obj, uom_transaction):
        if product_obj.general_uom_group:
            uom_base = product_obj.general_uom_group.uom_reference
            if uom_base and uom_transaction:
                return uom_transaction.ratio / uom_base.ratio if uom_base.ratio > 0 else 1
        return 1
