from apps.sales.acceptance.models import FinalAcceptanceIndicator


class ReturnFinishHandler:
    # PRODUCT INFO
    @classmethod
    def push_product_info(cls, instance):
        for return_product in instance.goods_return_product_detail.all():
            product = None
            value = 0
            is_redelivery = False
            if return_product.type == 1:  # lot
                product, value = cls.setup_product_info_by_lot(return_product=return_product)
                if return_product.lot_redelivery_number > 0:  # redelivery
                    is_redelivery = True
            if return_product.type == 2:  # serial
                product, value = cls.setup_product_info_by_serial(return_product=return_product)
                if return_product.is_redelivery is True:  # redelivery
                    is_redelivery = True
            if product and is_redelivery is False:  # update product no redelivery
                product.save(**{
                    'update_transaction_info': True,
                    'quantity_return': value,
                    'update_fields': ['stock_amount', 'available_amount']
                })
            if product and is_redelivery is True:  # update product with redelivery
                product.save(**{
                    'update_transaction_info': True,
                    'quantity_return_redelivery': value,
                    'update_fields': ['wait_delivery_amount', 'stock_amount', 'available_amount']
                })
        return True

    @classmethod
    def setup_product_info_by_lot(cls, return_product):
        product = None
        value = 0
        if return_product.type == 1:  # lot
            if return_product.lot_no:
                if return_product.lot_no.product_warehouse:
                    product = return_product.lot_no.product_warehouse.product
                    value = return_product.lot_return_number
        return product, value

    @classmethod
    def setup_product_info_by_serial(cls, return_product):
        product = None
        value = 0
        if return_product.type == 2:  # serial
            if return_product.serial_no:
                if return_product.serial_no.product_warehouse:
                    product = return_product.serial_no.product_warehouse.product
                    value = 1
        return product, value

    # FINAL ACCEPTANCE
    @classmethod
    def update_final_acceptance(cls, instance):
        product_data_json = {}
        for return_product in instance.goods_return_product_detail.all():
            product_id = None
            value = 0
            if return_product.type == 1:  # lot
                product_id, value = cls.setup_fa_by_lot(return_product=return_product)
            if return_product.type == 2:  # serial
                product_id, value = cls.setup_fa_by_serial(return_product=return_product)
            if product_id:
                if str(product_id) not in product_data_json:
                    product_data_json.update({
                        str(product_id): value
                    })
                else:
                    product_data_json[str(product_id)] += value
            cls.update_fa_delivery(instance=instance, product_data_json=product_data_json)
        return True

    @classmethod
    def update_fa_delivery(cls, instance, product_data_json):
        for fa_ind_delivery in FinalAcceptanceIndicator.objects.filter_current(
                fill__tenant=True, fill__company=True,
                sale_order_id=instance.sale_order_id, delivery_sub_id=instance.delivery_id,
        ):
            fa_ind_product_id = str(fa_ind_delivery.product_id)
            if fa_ind_product_id in product_data_json:
                fa_ind_delivery.actual_value = fa_ind_delivery.actual_value - product_data_json[fa_ind_product_id]
                fa_ind_delivery.save(update_fields=['actual_value'])
        return True

    @classmethod
    def setup_fa_by_lot(cls, return_product):
        product_id = None
        value = 0
        if return_product.type == 1:  # lot
            if return_product.lot_no:
                if return_product.lot_no.product_warehouse:
                    product_obj = return_product.lot_no.product_warehouse.product
                    product_id = return_product.lot_no.product_warehouse.product_id
                    warehouse_id = return_product.lot_no.product_warehouse.warehouse_id
                    if product_obj and product_id and warehouse_id:
                        cost = product_obj.get_unit_cost_by_warehouse(warehouse_id=warehouse_id, get_type=1)
                        value = cost * return_product.lot_return_number
        return product_id, value

    @classmethod
    def setup_fa_by_serial(cls, return_product):
        product_id = None
        value = 0
        if return_product.type == 2:  # serial
            if return_product.serial_no:
                if return_product.serial_no.product_warehouse:
                    product_obj = return_product.serial_no.product_warehouse.product
                    product_id = return_product.serial_no.product_warehouse.product_id
                    warehouse_id = return_product.serial_no.product_warehouse.warehouse_id
                    if product_obj and product_id and warehouse_id:
                        value = product_obj.get_unit_cost_by_warehouse(warehouse_id=warehouse_id, get_type=1)
        return product_id, value
