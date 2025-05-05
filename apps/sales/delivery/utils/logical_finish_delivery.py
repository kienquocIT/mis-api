from apps.masterdata.saledata.models import UnitOfMeasure, ProductWareHouse, ProductWareHouseLot
from apps.sales.acceptance.models import FinalAcceptance
from apps.shared import DisperseModel


class DeliFinishHandler:

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
        # setup data để tạo records product mới cho sub mới
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
                    ready_quantity=ready_quantity if ready_quantity > 0 else 0,
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
                final_ratio = DeliFinishSubHandler.get_final_uom_ratio(
                    product_obj=item.product, uom_transaction=uom_delivery
                )
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
                        tenant_id=deli_product.tenant_id,
                        company_id=deli_product.company_id,
                        product_warehouse_id=product_warehouse.id,
                        lot_data=lot_data,
                        type_transaction=1,
                    )
        return True

    @classmethod
    def update_pw_serial(cls, deli_product):
        for serial in deli_product.delivery_serial_delivery_product.all():
            if serial.product_warehouse_serial:
                serial.product_warehouse_serial.serial_status = 1
                serial.product_warehouse_serial.save(update_fields=['serial_status'])
        return True

    # ASSET
    @classmethod
    def update_asset_status(cls, instance):
        for delivery_asset in instance.delivery_pa_delivery_sub.all():
            if delivery_asset.asset and delivery_asset.picked_quantity > 0:
                delivery_asset.asset.status = 2
                delivery_asset.asset.save(update_fields=['status'])
        return True

    @classmethod
    def force_create_new_asset(cls, instance):
        # Tạo ra sl tài sản theo sl giao với giá kho tương úng
        model_asset = DisperseModel(app_model='asset.fixedasset').get_model()
        model_asset_m2m = DisperseModel(app_model='asset.fixedassetusedepartment').get_model()
        model_lo_config = DisperseModel(app_model='leaseorder.leaseorderappConfig').get_model()
        if all(hasattr(model, 'objects') for model in [model_asset, model_asset_m2m, model_lo_config]):
            for delivery_product in instance.delivery_product_delivery_sub.all():
                asset_type = delivery_product.asset_type
                product_convert_into = delivery_product.product_convert_into
                if asset_type == 1 and product_convert_into == 2 and delivery_product.offset:
                    asset_data = []
                    for delivery_warehouse in delivery_product.delivery_pw_delivery_product.all():
                        asset_data += DeliFinishHandler.create_obj_and_set_asset_data(
                            model_asset=model_asset,
                            model_asset_m2m=model_asset_m2m,
                            model_lo_config=model_lo_config,
                            instance=instance,
                            delivery_product=delivery_product,
                            delivery_warehouse=delivery_warehouse
                        )
                    delivery_product.asset_data = asset_data
                    delivery_product.save(update_fields=['asset_data'])
        return True

    @classmethod
    def create_obj_and_set_asset_data(
            cls,
            model_asset,
            model_asset_m2m,
            model_lo_config,
            instance,
            delivery_product,
            delivery_warehouse
    ):
        asset_data = []
        cost = DeliFinishHandler.get_cost_by_warehouse(
            product_obj=delivery_product.offset,
            warehouse_id=delivery_warehouse.warehouse_id,
            sale_order_id=None,
        )
        lo_config = model_lo_config.objects.filter_on_company().first()
        if lo_config:
            for _ in range(int(delivery_warehouse.quantity_delivery)):
                asset_obj = model_asset.objects.create(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    classification_id=lo_config.asset_type_id,
                    manage_department_id=lo_config.asset_group_manage_id,
                    product_id=delivery_product.offset_id,
                    title=delivery_product.offset.title,
                    asset_code=delivery_product.offset.code,
                    source_type=1,
                    original_cost=cost,
                    depreciation_method=delivery_product.product_depreciation_method,
                    depreciation_time=delivery_product.product_depreciation_time,
                    adjustment_factor=delivery_product.product_depreciation_adjustment,
                    depreciation_start_date=delivery_product.product_depreciation_start_date,
                    depreciation_end_date=delivery_product.product_depreciation_end_date,
                    depreciation_value=delivery_product.product_depreciation_price * delivery_product.product_quantity,
                    depreciation_data=DeliFinishHandler.update_depreciation_data(
                        depreciation_data=delivery_product.depreciation_data,
                        old_cost=delivery_product.product_cost,
                        new_cost=cost,
                    ),
                    status=2,
                )
                if asset_obj:
                    asset_obj.system_status = 3
                    asset_obj.save(update_fields=['system_status'])
                    # m2m
                    model_asset_m2m.objects.bulk_create([
                        model_asset_m2m(fixed_asset=asset_obj, use_department_id=group.get('id', None))
                        for group in lo_config.asset_group_using_data
                    ])
                    asset_json = {
                        'asset_id': str(asset_obj.id),
                        'asset_data': {
                            "id": str(asset_obj.id),
                            "code": asset_obj.code,
                            "title": asset_obj.title,
                            "asset_id": str(asset_obj.id),
                            "net_value": 0,
                            "origin_cost": asset_obj.original_cost,
                            "depreciation_time": asset_obj.depreciation_time,
                            "depreciation_start_date": str(asset_obj.depreciation_start_date),
                            "depreciation_end_date": str(asset_obj.depreciation_end_date),
                            "depreciation_data": asset_obj.depreciation_data,
                        },
                        "product_id": str(delivery_product.product_id),
                        "product_data": delivery_product.product_data,
                        "uom_time_id": str(delivery_product.uom_time_id),
                        "uom_time_data": delivery_product.uom_time_data,
                        "product_quantity_time": delivery_product.product_quantity_time,
                        "product_depreciation_time": delivery_product.product_depreciation_time,
                        "product_depreciation_price": delivery_product.product_depreciation_price,
                        "product_depreciation_method": delivery_product.product_depreciation_method,
                        "product_depreciation_subtotal": delivery_product.product_depreciation_subtotal,
                        "product_depreciation_adjustment": delivery_product.product_depreciation_adjustment,
                        "product_depreciation_start_date": str(
                            delivery_product.product_depreciation_start_date
                        ),
                        "product_depreciation_end_date": str(
                            delivery_product.product_depreciation_end_date
                        ),

                        "product_lease_end_date": str(delivery_product.product_lease_end_date),
                        "product_lease_start_date": str(delivery_product.product_lease_start_date),

                        "depreciation_data": delivery_product.depreciation_data,

                        "quantity_remain_recovery": 1,
                    }
                    asset_data.append(asset_json)
        return asset_data

    @classmethod
    def force_create_new_tool(cls, instance):
        # Tạo ra 1 công cụ với giá lấy trung bình từ các kho
        model_tool = DisperseModel(app_model='asset.instrumenttool').get_model()
        model_asset_m2m = DisperseModel(app_model='asset.instrumenttoolusedepartment').get_model()
        model_lo_config = DisperseModel(app_model='leaseorder.leaseorderappConfig').get_model()
        if model_tool and hasattr(model_tool, 'objects') and model_lo_config and hasattr(model_lo_config, 'objects'):
            for delivery_product in instance.delivery_product_delivery_sub.all():
                asset_type = delivery_product.asset_type
                product_convert_into = delivery_product.product_convert_into
                if asset_type == 1 and product_convert_into == 1 and delivery_product.offset:
                    price_list = []
                    quantity = 0
                    for delivery_warehouse in delivery_product.delivery_pw_delivery_product.all():
                        cost = DeliFinishHandler.get_cost_by_warehouse(
                            product_obj=delivery_product.offset,
                            warehouse_id=delivery_warehouse.warehouse_id,
                            sale_order_id=None,
                        )
                        if cost not in price_list:
                            price_list.append(cost)
                        quantity += delivery_warehouse.quantity_delivery
                    tool_data = DeliFinishHandler.create_obj_and_set_tool_data(
                        model_tool=model_tool,
                        model_asset_m2m=model_asset_m2m,
                        model_lo_config=model_lo_config,
                        instance=instance,
                        delivery_product=delivery_product,
                        cost=(sum(price_list) / len(price_list)),
                        quantity=quantity
                    )
                    delivery_product.tool_data = tool_data
                    delivery_product.save(update_fields=['tool_data'])
        return True

    @classmethod
    def create_obj_and_set_tool_data(
            cls,
            model_tool,
            model_asset_m2m,
            model_lo_config,
            instance,
            delivery_product,
            cost,
            quantity,
    ):
        lo_config = model_lo_config.objects.filter_on_company().first()
        if lo_config:
            tool_obj = model_tool.objects.create(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                classification_id=lo_config.tool_type_id,
                manage_department_id=lo_config.tool_group_manage_id,
                product_id=delivery_product.offset_id,
                title=delivery_product.offset.title,
                asset_code=delivery_product.offset.code,
                source_type=1,
                unit_price=cost,
                quantity=quantity,
                depreciation_time=delivery_product.product_depreciation_time,
                depreciation_start_date=delivery_product.product_depreciation_start_date,
                depreciation_end_date=delivery_product.product_depreciation_end_date,
                depreciation_data=DeliFinishHandler.update_depreciation_data(
                    depreciation_data=delivery_product.depreciation_data,
                    old_cost=delivery_product.product_cost,
                    new_cost=cost,
                ),
                status=2,
            )
            if tool_obj:
                tool_obj.system_status = 3
                tool_obj.save(update_fields=['system_status'])
                # m2m
                model_asset_m2m.objects.bulk_create([
                    model_asset_m2m(instrument_tool=tool_obj, use_department_id=group.get('id', None))
                    for group in lo_config.tool_group_using_data
                ])
                tool_json = {
                    'tool_id': str(tool_obj.id),
                    'tool_data': {
                        "id": str(tool_obj.id),
                        "code": tool_obj.code,
                        "title": tool_obj.title,
                        "tool_id": str(tool_obj.id),
                        "net_value": 0,
                        "unit_price": tool_obj.unit_price,
                        "depreciation_time": tool_obj.depreciation_time,
                        "depreciation_start_date": str(tool_obj.depreciation_start_date),
                        "depreciation_end_date": str(tool_obj.depreciation_end_date),
                        "depreciation_data": tool_obj.depreciation_data,
                    },
                    "product_id": str(delivery_product.product_id),
                    "product_data": delivery_product.product_data,
                    "uom_time_id": str(delivery_product.uom_time_id),
                    "uom_time_data": delivery_product.uom_time_data,
                    "product_quantity_time": delivery_product.product_quantity_time,
                    "product_depreciation_time": delivery_product.product_depreciation_time,
                    "product_depreciation_price": delivery_product.product_depreciation_price,
                    "product_depreciation_method": delivery_product.product_depreciation_method,
                    "product_depreciation_subtotal": delivery_product.product_depreciation_subtotal,
                    "product_depreciation_adjustment": delivery_product.product_depreciation_adjustment,
                    "product_depreciation_start_date": str(
                        delivery_product.product_depreciation_start_date
                    ),
                    "product_depreciation_end_date": str(
                        delivery_product.product_depreciation_end_date
                    ),

                    "product_lease_end_date": str(delivery_product.product_lease_end_date),
                    "product_lease_start_date": str(delivery_product.product_lease_start_date),

                    "depreciation_data": delivery_product.depreciation_data,

                    "quantity_remain_recovery": delivery_product.quantity_remain_recovery,
                }
                return [tool_json]
        return []

    @classmethod
    def update_depreciation_data(cls, depreciation_data, old_cost, new_cost):
        factor = new_cost / old_cost  # Determine the scaling factor
        for entry in depreciation_data:
            entry["start_value"] = round(entry["start_value"] * factor)
            entry["end_value"] = round(entry["end_value"] * factor)
            entry["accumulative_value"] = round(entry["accumulative_value"] * factor)
            entry["depreciation_value"] = round(entry["depreciation_value"] * factor)
        return depreciation_data

    # PRODUCT INFO
    @classmethod
    def push_product_info(cls, instance):
        for deli_product in instance.delivery_product_delivery_sub.all():
            if deli_product.product and deli_product.uom:
                target = deli_product.product
                if deli_product.offset:
                    target = deli_product.offset
                final_ratio = DeliFinishSubHandler.get_final_uom_ratio(
                    product_obj=target, uom_transaction=deli_product.uom
                )
                target.save(**{
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
                    cost = DeliFinishHandler.get_cost_by_warehouse(
                        product_obj=deli_product.product,
                        warehouse_id=data_deli.get('warehouse_id', None),
                        sale_order_id=data_deli.get('sale_order_id', None),
                    )
                    actual_value += cost * data_deli['picked_quantity']
        else:  # case: product not allow inventory
            so_cost = deli_product.product.sale_order_cost_product.filter(sale_order=sale_order).first()
            if so_cost:
                actual_value = so_cost.product_cost_price * deli_product.picked_quantity
        return actual_value

    @classmethod
    def get_cost_by_warehouse(cls, product_obj, warehouse_id, sale_order_id):
        return product_obj.get_current_unit_cost(
            get_type=1,
            **{
                'warehouse_id': warehouse_id,
                'sale_order_id': sale_order_id,
            }
        )

    @classmethod
    def get_delivery_config(cls, instance):
        config = instance.config_at_that_point
        if not config:
            if hasattr(instance.company, 'sales_delivery_config_detail'):
                get_config = instance.company.sales_delivery_config_detail
                if get_config:
                    return {"is_picking": get_config.is_picking, "is_partial_ship": get_config.is_partial_ship}
        return config


class DeliFinishSubHandler:

    @classmethod
    def get_final_uom_ratio(cls, product_obj, uom_transaction):
        if product_obj.general_uom_group:
            uom_base = product_obj.general_uom_group.uom_reference
            if uom_base and uom_transaction:
                return uom_transaction.ratio / uom_base.ratio if uom_base.ratio > 0 else 1
        return 1
