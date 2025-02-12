from apps.masterdata.saledata.models import UnitOfMeasure, ProductWareHouse, ProductWareHouseLot
from apps.sales.acceptance.models import FinalAcceptance
from apps.shared import DisperseModel


class DeliFinishHandler:
    # UPDATE COST DELIVERY PRODUCT
    @classmethod
    def update_cost_delivery_product(cls, instance):
        for deli_product in instance.delivery_product_delivery_sub.all():  # for in product
            cls.update_cost_by_wh(deli_product=deli_product)
        return True

    @classmethod
    def update_cost_by_wh(cls, deli_product):
        product_obj, delivery_data = deli_product.product, deli_product.delivery_data
        if product_obj:
            for data_deli in delivery_data:  # for in warehouse to get cost of warehouse
                cost = product_obj.get_unit_cost_by_warehouse(warehouse_id=data_deli.get('warehouse_id', None), get_type=1)
                data_deli.update({'cost': cost})
            deli_product.save(update_fields=['delivery_data'])

        return True

    # NEW DELIVERY SUB + PRODUCT
    @classmethod
    def create_new(cls, instance):
        config = cls.get_delivery_config(instance=instance)
        is_picking = config['is_picking']
        total_done = 0
        for deli_product in instance.delivery_product_delivery_sub.all():
            total_done += deli_product.picked_quantity
        delivery_obj = instance.order_delivery
        if instance.remaining_quantity > total_done:  # still not delivery all items, create new sub
            new_sub = cls.create_new_sub(instance, total_done, 2 if is_picking is False else 4)
            cls.create_prod(new_sub, instance)
            delivery_obj.sub = new_sub
            delivery_obj.save(update_fields=['sub'])
        else:  # delivery all items, not create new sub
            delivery_obj.state = 2
            delivery_obj.save(update_fields=['state'])
        return True

    @classmethod
    def create_new_sub(cls, instance, total_done, case=0):
        quantity_before = instance.delivered_quantity_before + total_done
        remaining_quantity = instance.delivery_quantity - quantity_before
        model_deli_sub = DisperseModel(app_model='delivery.orderdeliverysub').get_model()
        if model_deli_sub and hasattr(model_deli_sub, 'objects'):
            return model_deli_sub.objects.create(
                company_id=instance.company_id,
                tenant_id=instance.tenant_id,
                order_delivery=instance.order_delivery,
                date_done=None,
                previous_step=instance,
                times=instance.times + 1,
                delivery_quantity=instance.delivery_quantity,
                delivered_quantity_before=quantity_before,
                remaining_quantity=remaining_quantity,
                ready_quantity=instance.ready_quantity - total_done if case == 4 else 0,
                delivery_data=None,
                is_updated=False,
                state=0 if case == 4 and instance.ready_quantity - total_done == 0 else 1,
                sale_order_data=instance.order_delivery.sale_order_data if instance.order_delivery else {},
                lease_order_data=instance.order_delivery.lease_order_data if instance.order_delivery else {},
                estimated_delivery_date=instance.estimated_delivery_date,
                actual_delivery_date=instance.actual_delivery_date,
                customer_data=instance.customer_data,
                contact_data=instance.contact_data,
                config_at_that_point=instance.config_at_that_point,
                employee_inherit=instance.employee_inherit,
                system_status=1,
            )
        return None

    @classmethod
    def create_prod(cls, new_sub, instance):
        # update to current product list of current sub
        prod_arr = []
        model_deli_product = DisperseModel(app_model='delivery.orderdeliveryproduct').get_model()
        if model_deli_product and hasattr(model_deli_product, 'objects'):
            for deli_product in instance.delivery_product_delivery_sub.all():
                quantity_before = deli_product.delivered_quantity_before + deli_product.picked_quantity
                remaining_quantity = deli_product.delivery_quantity - quantity_before
                ready_quantity = deli_product.ready_quantity - deli_product.picked_quantity
                new_prod = deli_product.setup_new_obj(
                    old_obj=deli_product,
                    new_sub=new_sub,
                    delivery_quantity=deli_product.delivery_quantity,
                    delivered_quantity_before=quantity_before,
                    remaining_quantity=remaining_quantity,
                    ready_quantity=ready_quantity if ready_quantity > 0 else 0
                )
                new_prod.before_save()
                prod_arr.append(new_prod)
            model_deli_product.objects.bulk_create(prod_arr)
        return True

    # PRODUCT WAREHOUSE
    @classmethod
    def push_product_warehouse(cls, instance):
        config = cls.get_delivery_config(instance=instance)
        for deli_product in instance.delivery_product_delivery_sub.all():
            # Nếu chưa giao hết thì bắt đầu trừ tồn kho
            if deli_product.remaining_quantity > 0:
                cls.update_pw(instance=instance, deli_product=deli_product, config=config)
                cls.update_pw_lot(deli_product=deli_product)
                cls.update_pw_serial(deli_product=deli_product)
        return True

    @classmethod
    def update_pw(cls, instance, deli_product, config):
        target = deli_product.product
        if deli_product.offset:
            target = deli_product.offset
        if target and deli_product.delivery_data:
            for data_deli in deli_product.delivery_data:
                if all(key in data_deli for key in ('warehouse_id', 'uom_id', 'picked_quantity')):
                    product_warehouse = target.product_warehouse_product.filter(
                        tenant_id=instance.tenant_id, company_id=instance.company_id,
                        warehouse_id=data_deli['warehouse_id'],
                    )
                    source = {"uom_id": data_deli['uom_id'], "quantity": data_deli['picked_quantity']}
                    DeliFinishHandler.minus_tock(source, product_warehouse, config)
        return True

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
            uom_delivery = UnitOfMeasure.objects.filter(id=source['uom_id']).first()
            if item.product and uom_delivery:
                final_ratio = cls.get_final_uom_ratio(product_obj=item.product, uom_transaction=uom_delivery)
            delivery_quantity = source['quantity'] * final_ratio
            if item.stock_amount > 0:
                # số lượng trong kho đã quy đổi
                fn_quantity = 0
                calc = item.stock_amount - delivery_quantity
                if calc >= 0:
                    fn_quantity = delivery_quantity
                if calc < 0:
                    fn_quantity = delivery_quantity + calc
                # đủ hàng
                is_done = True
                item_sold = fn_quantity
                # set data update product warehouse
                item.sold_amount += item_sold
                item.stock_amount = item.receipt_amount - item.sold_amount
                if config['is_picking']:
                    item.picked_ready = item.picked_ready - item_sold
                list_update.append(item)
        ProductWareHouse.objects.bulk_update(list_update, fields=['sold_amount', 'picked_ready', 'stock_amount'])
        return True

    @classmethod
    def update_pw_lot(cls, deli_product):
        for lot in deli_product.delivery_lot_delivery_product.all():
            final_ratio = 1
            uom_delivery_rate = deli_product.uom.ratio if deli_product.uom else 1
            if lot.product_warehouse_lot:
                product_warehouse = lot.product_warehouse_lot.product_warehouse
                if product_warehouse:
                    uom_wh_rate = product_warehouse.uom.ratio if product_warehouse.uom else 1
                    if uom_wh_rate and uom_delivery_rate:
                        final_ratio = uom_delivery_rate / uom_wh_rate if uom_wh_rate > 0 else 1
                    # push ProductWareHouseLot
                    lot_data = [{
                        'lot_number': lot.product_warehouse_lot.lot_number,
                        'quantity_import': lot.quantity_delivery * final_ratio,
                        'expire_date': lot.product_warehouse_lot.expire_date,
                        'manufacture_date': lot.product_warehouse_lot.manufacture_date,
                        'delivery_id': deli_product.delivery_sub_id,
                    }]
                    ProductWareHouseLot.push_pw_lot(
                        tenant_id=deli_product.delivery_sub.tenant_id,
                        company_id=deli_product.delivery_sub.company_id,
                        product_warehouse_id=product_warehouse.id,
                        lot_data=lot_data,
                        type_transaction=1,
                    )
        return True

    @classmethod
    def update_pw_serial(cls, deli_product):
        for serial in deli_product.delivery_serial_delivery_product.all():
            serial.product_warehouse_serial.is_delete = True
            serial.product_warehouse_serial.save(update_fields=['is_delete'])
        return True

    # PRODUCT INFO
    @classmethod
    def push_product_info(cls, instance):
        for deli_product in instance.delivery_product_delivery_sub.all():
            if deli_product.product and deli_product.uom:
                final_ratio = cls.get_final_uom_ratio(
                    product_obj=deli_product.product, uom_transaction=deli_product.uom
                )
                deli_product.product.save(**{
                    'update_stock_info': {
                        'quantity_delivery': deli_product.picked_quantity * final_ratio,
                        'system_status': 3,
                    },
                    'update_fields': ['wait_delivery_amount', 'available_amount', 'stock_amount']
                })
        return True

    # SALE/ LEASE ORDER STATUS
    @classmethod
    def push_so_lo_status(cls, instance):
        target = None
        if instance.order_delivery:
            if instance.order_delivery.sale_order:
                target = instance.order_delivery.sale_order
            if instance.order_delivery.lease_order:
                target = instance.order_delivery.lease_order

            if target:
                # update sale/ lease order delivery_status (Partially delivered)
                if target.delivery_status in [0, 1]:
                    target.delivery_status = 2
                    target.save(update_fields=['delivery_status'])
                # update sale/ lease order delivery_status (Delivered)
                if target.delivery_status in [2] and instance.order_delivery.state == 2:
                    target.delivery_status = 3
                    target.save(update_fields=['delivery_status'])
        return True

    # FINAL ACCEPTANCE
    @classmethod
    def push_final_acceptance(cls, instance):
        list_data_indicator = []
        sale_order_id = None
        lease_order_id = None
        opportunity_id = None
        if instance.order_delivery:
            if instance.order_delivery.sale_order:
                sale_order_id = instance.order_delivery.sale_order_id
                if instance.order_delivery.sale_order.opportunity:
                    opportunity_id = instance.order_delivery.sale_order.opportunity_id
            if instance.order_delivery.lease_order:
                lease_order_id = instance.order_delivery.lease_order_id
                if instance.order_delivery.lease_order.opportunity:
                    opportunity_id = instance.order_delivery.lease_order.opportunity_id

            for deli_product in instance.delivery_product_delivery_sub.all():
                if deli_product.product and deli_product.picked_quantity > 0:
                    list_data_indicator.append({
                        'tenant_id': instance.tenant_id,
                        'company_id': instance.company_id,
                        'sale_order_id': sale_order_id,
                        'lease_order_id': lease_order_id,
                        'delivery_sub_id': instance.id,
                        'product_id': deli_product.product_id,
                        'actual_value': DeliFinishHandler.get_delivery_cost(
                            deli_product=deli_product, sale_order=instance.order_delivery.sale_order
                        ),
                        'acceptance_affect_by': 3,
                    })
            FinalAcceptance.push_final_acceptance(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                sale_order_id=sale_order_id,
                lease_order_id=lease_order_id,
                employee_created_id=instance.employee_created_id,
                employee_inherit_id=instance.employee_inherit_id,
                opportunity_id=opportunity_id,
                list_data_indicator=list_data_indicator,
            )
        return True

    @classmethod
    def get_delivery_cost(cls, deli_product, sale_order):
        actual_value = 0
        if 1 in deli_product.product.product_choice:  # case: product allow inventory
            for data_deli in deli_product.delivery_data:
                if all(key in data_deli for key in ('warehouse_id', 'picked_quantity')):
                    cost = deli_product.product.get_current_unit_cost(
                        get_type=1,
                        **{
                            'warehouse_id': data_deli.get('warehouse_id', None),
                            'sale_order_id': data_deli.get('sale_order_id', None),
                        }
                    )
                    actual_value += cost * data_deli['picked_quantity']
        else:  # case: product not allow inventory
            so_cost = deli_product.product.sale_order_cost_product.filter(sale_order=sale_order).first()
            if so_cost:
                actual_value = so_cost.product_cost_price * deli_product.picked_quantity
        return actual_value

    @classmethod
    def get_delivery_config(cls, instance):
        config = instance.config_at_that_point
        if not config:
            if hasattr(instance.company, 'sales_delivery_config_detail'):
                get_config = instance.company.sales_delivery_config_detail
                if get_config:
                    return {"is_picking": get_config.is_picking, "is_partial_ship": get_config.is_partial_ship}
        return config

    @classmethod
    def get_final_uom_ratio(cls, product_obj, uom_transaction):
        if product_obj.general_uom_group:
            uom_base = product_obj.general_uom_group.uom_reference
            if uom_base and uom_transaction:
                return uom_transaction.ratio / uom_base.ratio if uom_base.ratio > 0 else 1
        return 1
