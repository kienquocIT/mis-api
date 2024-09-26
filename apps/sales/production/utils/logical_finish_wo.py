class WorkOrderHandler:

    @classmethod
    def wo_info_for_so(cls, instance):
        if instance.product:
            so_product = instance.product.sale_order_product_product.first()
            if so_product:
                so_product.quantity_wo_remain -= instance.quantity
                if so_product.quantity_wo_remain >= 0:
                    so_product.save(update_fields=['quantity_wo_remain'])
        return True
