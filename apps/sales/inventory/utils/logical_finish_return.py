from apps.sales.acceptance.models import FinalAcceptanceIndicator
from apps.sales.saleorder.utils import SOFinishHandler


class ReturnFinishHandler:
    # PRODUCT INFO
    @classmethod
    def push_product_info(cls, instance):
        for return_product in instance.goods_return_product_detail.all():
            product = None
            value = 0
            is_redelivery = False
            if return_product.type == 0:  # no lot/serial
                product, value = cls.setup_return_quantity(return_product=return_product)
                if return_product.default_redelivery_number > 0:
                    is_redelivery = True
            if return_product.type == 1:  # lot
                product, value = cls.setup_return_quantity_lot(return_product=return_product)
                if return_product.lot_redelivery_number > 0:  # redelivery
                    is_redelivery = True
            if return_product.type == 2:  # serial
                product, value = cls.setup_return_quantity_serial(return_product=return_product)
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
    def setup_return_quantity(cls, return_product):
        if return_product.delivery_item:
            return return_product.delivery_item.product, return_product.default_return_number
        return None, 0

    @classmethod
    def setup_return_quantity_lot(cls, return_product):
        if return_product.lot_no:
            if return_product.lot_no.product_warehouse:
                return return_product.lot_no.product_warehouse.product, return_product.lot_return_number
        return None, 0

    @classmethod
    def setup_return_quantity_serial(cls, return_product):
        if return_product.serial_no:
            if return_product.serial_no.product_warehouse:
                return return_product.serial_no.product_warehouse.product, 1
        return None, 1

    # FINAL ACCEPTANCE
    @classmethod
    def update_final_acceptance(cls, instance):
        product_data_json = {}
        for return_product in instance.goods_return_product_detail.all():
            product_id = None
            value = 0
            if return_product.type == 0:  # no lot/serial
                product_id, value = cls.setup_return_value(return_product=return_product, instance=instance)
            if return_product.type == 1:  # lot
                product_id, value = cls.setup_return_value_lot(return_product=return_product)
            if return_product.type == 2:  # serial
                product_id, value = cls.setup_return_value_serial(return_product=return_product)
            if product_id:
                if str(product_id) not in product_data_json:
                    product_data_json.update({str(product_id): value})
                else:
                    product_data_json[str(product_id)] += value
            cls.update_fa_delivery(instance=instance, product_data_json=product_data_json)
        return True

    @classmethod
    def update_fa_delivery(cls, instance, product_data_json):
        for fa_ind_delivery in FinalAcceptanceIndicator.objects.filter(
                tenant_id=instance.tenant_id, company_id=instance.company_id,
                sale_order_id=instance.sale_order_id, delivery_sub_id=instance.delivery_id,
        ):
            fa_ind_product_id = str(fa_ind_delivery.product_id)
            if fa_ind_product_id in product_data_json:
                fa_ind_delivery.actual_value = fa_ind_delivery.actual_value - product_data_json[fa_ind_product_id]
                fa_ind_delivery.save(update_fields=['actual_value'])
        return True

    @classmethod
    def setup_return_value(cls, return_product, instance):
        if return_product.delivery_item:
            if return_product.delivery_item.product and instance.return_to_warehouse:
                product_obj = return_product.delivery_item.product
                cost = product_obj.get_unit_cost_by_warehouse(warehouse_id=instance.return_to_warehouse_id, get_type=1)
                return product_obj.id, cost * return_product.default_return_number
        return None, 0

    @classmethod
    def setup_return_value_lot(cls, return_product):
        if return_product.lot_no:
            if return_product.lot_no.product_warehouse:
                product_obj = return_product.lot_no.product_warehouse.product
                if product_obj:
                    cost = product_obj.get_unit_cost_by_warehouse(
                        warehouse_id=return_product.lot_no.product_warehouse.warehouse_id, get_type=1
                    )
                    return product_obj.id, cost * return_product.lot_return_number
        return None, 0

    @classmethod
    def setup_return_value_serial(cls, return_product):
        if return_product.serial_no:
            if return_product.serial_no.product_warehouse:
                product_obj = return_product.serial_no.product_warehouse.product
                if product_obj:
                    return product_obj.id, product_obj.get_unit_cost_by_warehouse(
                        warehouse_id=return_product.serial_no.product_warehouse.warehouse_id, get_type=1
                    )
        return None, 0

    # REPORT
    @classmethod
    def update_report(cls, instance):
        if instance.sale_order:
            product_data_json = {}
            for return_product in instance.goods_return_product_detail.all():
                product = None
                value = 0
                if return_product.type == 0:  # no lot/serial
                    product, value = cls.setup_return_quantity(return_product=return_product)
                    if return_product.default_redelivery_number > 0:
                        return True
                if return_product.type == 1:  # lot
                    product, value = cls.setup_return_quantity_lot(return_product=return_product)
                    if return_product.lot_redelivery_number > 0:  # redelivery => not update report
                        return True
                if return_product.type == 2:  # serial
                    product, value = cls.setup_return_quantity_serial(return_product=return_product)
                    if return_product.is_redelivery is True:  # redelivery => not update report
                        return True
                if product:
                    if str(product.id) not in product_data_json:
                        product_data_json.update({str(product.id): value})
                    else:
                        product_data_json[str(product.id)] += value
            cls.update_report_revenue(instance=instance, product_data_json=product_data_json)
        return True

    @classmethod
    def update_report_revenue(cls, instance, product_data_json):
        gross_profit_rate = 0
        net_income_rate = 0
        discount_diff_rate = SOFinishHandler.find_discount_diff(instance=instance.sale_order)
        return_revenue_total = 0
        if instance.sale_order.indicator_revenue > 0:
            gross_profit_rate = instance.sale_order.indicator_gross_profit / instance.sale_order.indicator_revenue
            net_income_rate = instance.sale_order.indicator_net_income / instance.sale_order.indicator_revenue
        for so_product in instance.sale_order.sale_order_product_sale_order.all():
            if str(so_product.product_id) in product_data_json:
                product_discount_diff = so_product.product_unit_price * discount_diff_rate / 100
                price_ad = so_product.product_unit_price - so_product.product_discount_amount - product_discount_diff
                return_revenue = price_ad * product_data_json[str(so_product.product_id)]
                return_gross = return_revenue * gross_profit_rate
                return_net = return_revenue * net_income_rate
                cls.report_product(
                    sale_order=instance.sale_order, product_id=so_product.product_id,
                    return_revenue=return_revenue, return_gross=return_gross,
                    return_net=return_net
                )
                return_revenue_total += return_revenue
        return_gross_total = return_revenue_total * gross_profit_rate
        return_net_total = return_revenue_total * net_income_rate
        cls.report_revenue(
            sale_order=instance.sale_order, return_revenue=return_revenue_total,
            return_gross=return_gross_total, return_net=return_net_total
        )
        cls.report_customer(
            sale_order=instance.sale_order, return_revenue=return_revenue_total,
            return_gross=return_gross_total, return_net=return_net_total
        )
        return True

    @classmethod
    def report_revenue(cls, sale_order, return_revenue, return_gross, return_net):
        if hasattr(sale_order, 'report_revenue_sale_order'):
            report_revenue_obj = sale_order.report_revenue_sale_order
            report_revenue_obj.revenue -= return_revenue
            report_revenue_obj.gross_profit -= return_gross
            report_revenue_obj.net_income -= return_net
            report_revenue_obj.save(update_fields=['revenue', 'gross_profit', 'net_income'])
        return True

    @classmethod
    def report_product(cls, sale_order, product_id, return_revenue, return_gross, return_net):
        if hasattr(sale_order, 'report_product_sale_order'):
            report_product_obj = sale_order.report_product_sale_order.filter(
                product_id=product_id
            ).first()
            if report_product_obj:
                report_product_obj.revenue -= return_revenue
                report_product_obj.gross_profit -= return_gross
                report_product_obj.net_income -= return_net
                report_product_obj.save(update_fields=['revenue', 'gross_profit', 'net_income'])
        return True

    @classmethod
    def report_customer(cls, sale_order, return_revenue, return_gross, return_net):
        if hasattr(sale_order, 'report_customer_sale_order'):
            report_customer_obj = sale_order.report_customer_sale_order.first()
            if report_customer_obj:
                report_customer_obj.revenue -= return_revenue
                report_customer_obj.gross_profit -= return_gross
                report_customer_obj.net_income -= return_net
                report_customer_obj.save(update_fields=['revenue', 'gross_profit', 'net_income'])
        return True
