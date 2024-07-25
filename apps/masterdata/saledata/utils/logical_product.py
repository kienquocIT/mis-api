class ProductHandler:
    @classmethod
    def update_stock_info(cls, instance, **kwargs):
        update_info = kwargs['update_stock_info']
        del kwargs['update_stock_info']
        # If product doesn't have inventory choice
        if 1 not in instance.product_choice:
            return {}
        # If product have inventory choice
        if 'system_status' in update_info:
            cls.by_purchase(instance=instance, update_info=update_info)
            cls.by_receipt_po(instance=instance, update_info=update_info)
            cls.by_receipt_ia(instance=instance, update_info=update_info)
            cls.by_order(instance=instance, update_info=update_info)
            cls.by_delivery(instance=instance, update_info=update_info)
            cls.by_return(instance=instance, update_info=update_info)
            cls.by_return_redelivery(instance=instance, update_info=update_info)
            instance.available_amount = (
                    instance.stock_amount - instance.wait_delivery_amount + instance.wait_receipt_amount
            )
        return kwargs

    @classmethod
    def by_purchase(cls, instance, update_info):
        if 'quantity_purchase' in update_info:
            if update_info['system_status'] == 3:
                instance.wait_receipt_amount += update_info['quantity_purchase']
            if update_info['system_status'] == 4:
                instance.wait_receipt_amount -= update_info['quantity_purchase']
        return True

    @classmethod
    def by_receipt_po(cls, instance, update_info):
        if 'quantity_receipt_po' in update_info and 'quantity_receipt_actual' in update_info:
            if update_info['system_status'] == 3:
                instance.wait_receipt_amount -= update_info['quantity_receipt_po']
                instance.stock_amount += update_info['quantity_receipt_actual']
            if update_info['system_status'] == 4:
                instance.wait_receipt_amount += update_info['quantity_receipt_po']
                instance.stock_amount -= update_info['quantity_receipt_actual']
        return True

    @classmethod
    def by_receipt_ia(cls, instance, update_info):
        if 'quantity_receipt_ia' in update_info:
            if update_info['system_status'] == 3:
                instance.stock_amount += update_info['quantity_receipt_ia']
        return True

    @classmethod
    def by_order(cls, instance, update_info):
        if 'quantity_order' in update_info:
            if update_info['system_status'] == 3:
                instance.wait_delivery_amount += update_info['quantity_order']
            if update_info['system_status'] == 4:
                instance.wait_delivery_amount -= update_info['quantity_order']
        return True

    @classmethod
    def by_delivery(cls, instance, update_info):
        if 'quantity_delivery' in update_info:
            if update_info['system_status'] == 3:
                instance.wait_delivery_amount -= update_info['quantity_delivery']
                instance.stock_amount -= update_info['quantity_delivery']
        return True

    @classmethod
    def by_return(cls, instance, update_info):
        if 'quantity_return' in update_info:
            if update_info['system_status'] == 3:
                instance.stock_amount += update_info['quantity_return']
        return True

    @classmethod
    def by_return_redelivery(cls, instance, update_info):
        if 'quantity_return_redelivery' in update_info:
            if update_info['system_status'] == 3:
                instance.wait_delivery_amount += update_info['quantity_return_redelivery']
                instance.stock_amount += update_info['quantity_return_redelivery']
        return True
