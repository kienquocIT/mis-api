class RecoveryFinishHandler:

    @ classmethod
    def run_logics(cls, instance):
        for recovery_product in instance.recovery_product_recovery.all():
            # Trừ remain_recovery cho phiếu tiếp theo
            RecoveryFinishHandler.minus_remain(recovery_product=recovery_product)
            # Kiểm tra có thu hồi SP đã cho thuê thì chỉ cập nhật dữ liệu
            RecoveryFinishHandler.update_asset_status(recovery_product=recovery_product)
        return True

    @classmethod
    def minus_remain(cls, recovery_product):
        if recovery_product.recovery_delivery and recovery_product.product:
            deli_product = recovery_product.product.delivery_product_product.filter(
                delivery_sub=recovery_product.recovery_delivery.delivery
            ).first()
            if deli_product:
                deli_product.quantity_remain_recovery -= recovery_product.quantity_recovery
                deli_product.save(**{
                    'for_goods_recovery': True,
                    'update_fields': ['quantity_remain_recovery']
                })

        return True

    @classmethod
    def update_asset_status(cls, recovery_product):
        for recovery_asset in recovery_product.recovery_product_asset_recovery_product.all():
            if recovery_asset.quantity_recovery > 0:
                recovery_asset.asset.status = 0
                recovery_asset.asset.save(update_fields=['status'])
        return True
