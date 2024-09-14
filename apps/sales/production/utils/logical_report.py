class ProductionReportHandler:

    @classmethod
    def push_product_info(cls, instance):
        if instance.product:
            uom_transaction = instance.uom
            final_ratio = cls.get_final_uom_ratio(
                product_obj=instance.product, uom_transaction=uom_transaction
            )
            instance.product.save(**{
                'update_stock_info': {
                    'quantity_production': instance.quantity_finished * final_ratio,
                    'system_status': 3,
                },
                'update_fields': ['production_amount', 'available_amount']
            })
        return True

    @classmethod
    def get_final_uom_ratio(cls, product_obj, uom_transaction):
        if product_obj.general_uom_group:
            uom_base = product_obj.general_uom_group.uom_reference
            if uom_base and uom_transaction:
                return uom_transaction.ratio / uom_base.ratio if uom_base.ratio > 0 else 1
        return 1
