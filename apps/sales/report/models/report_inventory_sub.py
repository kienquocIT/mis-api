from apps.sales.inventory.models.goods_registration import GoodsRegistration
from apps.sales.report.models import LatestSub, ReportInventoryProductWarehouse


class LoggingSubFunction:
    @classmethod
    def regis_stock(cls, stock_obj, item):
        if item.get('trans_title') == 'Delivery':
            sale_order = stock_obj.order_delivery.sale_order
            GoodsRegistration.update_registered_quantity(
                sale_order, item, **{'delivery_id': stock_obj.id}
            )
            return True
        if item.get('trans_title') == 'Goods receipt':
            for po_pr_mapped in stock_obj.purchase_order.purchase_order_request_order.all():
                sale_order = po_pr_mapped.purchase_request.sale_order
                if sale_order:
                    GoodsRegistration.update_registered_quantity(
                        sale_order, item, **{'goods_receipt_id': stock_obj.id}
                    )
            return True
        return False

    @classmethod
    def get_latest_log(cls, product_id, **kwargs):
        """
        * kwargs_format:
        - required: []
        - option 1: [warehouse_id]
        Hàm lấy Log gần nhất theo sp và kho. Không có trả về None
        """
        last_record = LatestSub.objects.filter(
            product_id=product_id,
            **kwargs
        ).first()
        return last_record.latest_log if last_record else None

    @classmethod
    def get_latest_log_by_month(cls, period_obj, sub_period_order, product_id, **kwargs):
        """
        * kwargs_format:
        - required: []
        - option 1: [warehouse_id]
        Hàm để lấy Log cuối cùng của tháng trước theo sp và kho. Truyền vào tham số tháng này
        """
        if int(sub_period_order) == 1:
            last_rp_prd_wh = ReportInventoryProductWarehouse.objects.filter(
                product_id=product_id,
                period_mapped__fiscal_year=period_obj.fiscal_year - 1,
                sub_period_order=12,
                **kwargs
            ).first()
        else:
            last_rp_prd_wh = ReportInventoryProductWarehouse.objects.filter(
                product_id=product_id,
                period_mapped=period_obj,
                sub_period_order=int(sub_period_order) - 1,
                **kwargs
            ).first()
        return last_rp_prd_wh.sub_latest_log if last_rp_prd_wh else None

    @classmethod
    def get_latest_log_value_dict(cls, div, product_id, **kwargs):
        """
        * kwargs_format:
        - required: []
        - option 1: [warehouse_id]
        Hàm tìm value_dict Log gần nhất, không có trả về đầu kỳ hiện tại
        """
        latest_trans = LoggingSubFunction.get_latest_log(
            product_id,
            **kwargs
        )
        if latest_trans:
            return {
                'quantity': latest_trans.current_quantity,
                'cost': latest_trans.current_cost,
                'value': latest_trans.current_value
            } if div == 0 else {
                'quantity': latest_trans.periodic_current_quantity,
                'cost': 0,
                'value': 0
            }
        return cls.get_opening_balance_value_dict(
            product_id,
            3,
            **kwargs
        )

    @classmethod
    def calculate_new_value_dict_in_perpetual_inventory(cls, log, latest_value_dict):
        """ Hàm tính toán cho Phương pháp Kê khai thường xuyên """
        if log.stock_type == 1:
            new_quantity = latest_value_dict['quantity'] + log.quantity
            sum_value = latest_value_dict['value'] + log.value
            new_cost = (sum_value / new_quantity) if new_quantity else 0
            new_value = sum_value
        else:
            new_quantity = latest_value_dict['quantity'] - log.quantity
            new_cost = latest_value_dict['cost']
            new_value = new_cost * new_quantity
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}

    @classmethod
    def calculate_new_value_dict_in_periodic_inventory(cls, log, latest_value_dict):
        """ Hàm tính toán cho Phương pháp Kiểm kê định kì """
        if log.stock_type == 1:
            # Lúc này sum nhập đã được cập nhập
            new_quantity = latest_value_dict['quantity'] + log.quantity
            new_cost = 0
            new_value = 0
        else:
            new_quantity = latest_value_dict['quantity'] - log.quantity
            new_cost = 0
            new_value = 0
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}

    @classmethod
    def get_opening_balance_value_dict(cls, product_id, data_type=1, **kwargs):
        """
        * kwargs_format:
        - required: []
        - option 1: [warehouse_id]
        Hàm để lấy Số dư đầu kì theo SP và KHO
        (0-quantity, 1-cost, 2-value, 3-{'quantity':, 'cost':, 'value':}, else-return1)
        """
        # tìm số dư đầu kì
        this_record = ReportInventoryProductWarehouse.objects.filter(
            product_id=product_id,
            for_balance=True,
            **kwargs
        ).first()
        if this_record:
            if data_type == 0:
                return this_record.opening_balance_quantity
            if data_type == 1:
                return this_record.opening_balance_cost
            if data_type == 2:
                return this_record.opening_balance_value
            if data_type == 3:
                return {
                    'quantity': this_record.opening_balance_quantity,
                    'cost': this_record.opening_balance_cost,
                    'value': this_record.opening_balance_value
                }
            return this_record.opening_balance_cost
        return 0 if data_type != 3 else {'quantity': 0, 'cost': 0, 'value': 0}

    @classmethod
    def get_balance_data_this_sub(cls, this_rp_prd_wh):
        """
        Hàm lấy opening và ending của kỳ này
        """
        # Begin get Opening
        opening_quantity = this_rp_prd_wh.opening_balance_quantity
        opening_cost = this_rp_prd_wh.opening_balance_cost
        opening_value = this_rp_prd_wh.opening_balance_value
        # End

        # Begin get Ending
        if this_rp_prd_wh.sub_latest_log:
            if this_rp_prd_wh.company.company_config.definition_inventory_valuation == 0:
                ending_quantity = this_rp_prd_wh.sub_latest_log.current_quantity
                ending_cost = this_rp_prd_wh.sub_latest_log.current_cost
                ending_value = this_rp_prd_wh.sub_latest_log.current_value
            else:
                ending_quantity = this_rp_prd_wh.periodic_ending_balance_quantity
                ending_cost = this_rp_prd_wh.periodic_ending_balance_cost
                ending_value = this_rp_prd_wh.periodic_ending_balance_value
        else:
            ending_quantity = opening_quantity
            ending_cost = opening_cost
            ending_value = opening_value
        # End

        return {
            'opening_balance_quantity': opening_quantity,
            'opening_balance_cost': opening_cost,
            'opening_balance_value': opening_value,
            'ending_balance_quantity': ending_quantity,
            'ending_balance_cost': ending_cost,
            'ending_balance_value': ending_value,
        }

    @classmethod
    def calculate_ending_balance_for_periodic(cls, period_obj, sub_period_order, tenant, company):
        for this_record in ReportInventoryProductWarehouse.objects.filter(
                tenant=tenant,
                company=company,
                period_mapped=period_obj,
                sub_period_order=sub_period_order
        ):
            sum_input_quantity = this_record.sum_input_quantity
            sum_input_value = this_record.sum_input_value
            sum_output_quantity = this_record.sum_output_quantity

            if sum_input_quantity > 0:
                quantity = sum_input_quantity - sum_output_quantity
                cost = (sum_input_value / sum_input_quantity) if sum_input_quantity > 0 else 0
                value = quantity * cost
            else:
                quantity = this_record.opening_balance_quantity
                cost = this_record.opening_balance_cost
                value = this_record.opening_balance_value

            value_list = {'quantity': quantity, 'cost': cost, 'value': value}
            if value_list['quantity'] > 0:
                this_record.periodic_ending_balance_quantity = value_list['quantity']
                this_record.periodic_ending_balance_cost = value_list['cost']
                this_record.periodic_ending_balance_value = value_list['value']
            else:
                this_record.periodic_ending_balance_quantity = 0
                this_record.periodic_ending_balance_cost = 0
                this_record.periodic_ending_balance_value = 0
            this_record.periodic_closed = True
            this_record.save(update_fields=[
                'periodic_ending_balance_quantity',
                'periodic_ending_balance_cost',
                'periodic_ending_balance_value',
                'periodic_closed'
            ])
        return True
