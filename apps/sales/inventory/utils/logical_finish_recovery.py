class RecoveryFinishHandler:

    @ classmethod
    def run_logics(cls, instance):
        for recovery_product in instance.recovery_product_recovery.all():
            # Trừ remain_recovery cho phiếu tiếp theo
            RecoveryFinishHandler.minus_remain(recovery_product=recovery_product)
            RecoveryFinishHandler.update_tool_status(recovery_product=recovery_product)
            RecoveryFinishHandler.update_asset_status(recovery_product=recovery_product)
        return True

    @classmethod
    def minus_remain(cls, recovery_product):
        if recovery_product.recovery_delivery and recovery_product.product:
            # minus remain delivery product
            deli_product = recovery_product.product.delivery_product_product.filter(
                delivery_sub=recovery_product.recovery_delivery.delivery
            ).first()
            if deli_product:
                deli_product.quantity_remain_recovery -= recovery_product.quantity_recovery
                deli_product.save(**{
                    'for_goods_recovery': True,
                    'update_fields': ['quantity_remain_recovery']
                })
            # minus remain delivery product tool
            for recovery_tool in recovery_product.recovery_product_tool_recovery_product.all():
                if recovery_tool.tool:
                    deli_tool = recovery_tool.tool.delivery_pt_tool.filter(
                        delivery_sub=recovery_product.recovery_delivery.delivery
                    ).first()
                    if deli_tool:
                        deli_tool.quantity_remain_recovery -= recovery_tool.quantity_recovery
                        deli_tool.save(update_fields=['quantity_remain_recovery'])
            # minus remain delivery product asset
            for recovery_asset in recovery_product.recovery_product_asset_recovery_product.all():
                if recovery_asset.asset:
                    deli_asset = recovery_asset.asset.delivery_pa_asset.filter(
                        delivery_sub=recovery_product.recovery_delivery.delivery
                    ).first()
                    if deli_asset:
                        deli_asset.quantity_remain_recovery -= recovery_asset.quantity_recovery
                        deli_asset.save(update_fields=['quantity_remain_recovery'])

        return True

    @classmethod
    def update_tool_status(cls, recovery_product):
        for recovery_tool in recovery_product.recovery_product_tool_recovery_product.all():
            if recovery_tool.tool and recovery_tool.quantity_recovery > 0:
                recovery_tool.tool.status = 0
                recovery_tool.tool.quantity_leased -= recovery_tool.quantity_recovery
                recovery_tool.tool.save(update_fields=['status', 'quantity_leased'])
                # Update lease end date OrderDeliveryProductTool
                if recovery_product.recovery_delivery:
                    deli_tool = recovery_tool.tool.delivery_pt_tool.filter(
                        delivery_sub_id=recovery_product.recovery_delivery.delivery_id
                    ).first()
                    if deli_tool:
                        deli_tool.product_lease_end_date = recovery_tool.product_lease_end_date
                        deli_tool.save(update_fields=['product_lease_end_date'])
        return True

    @classmethod
    def update_asset_status(cls, recovery_product):
        for recovery_asset in recovery_product.recovery_product_asset_recovery_product.all():
            if recovery_asset.asset and recovery_asset.quantity_recovery > 0:
                recovery_asset.asset.status = 0
                recovery_asset.asset.save(update_fields=['status'])
                # Update lease end date OrderDeliveryProductAsset
                if recovery_product.recovery_delivery:
                    deli_asset = recovery_asset.asset.delivery_pa_asset.filter(
                        delivery_sub_id=recovery_product.recovery_delivery.delivery_id
                    ).first()
                    if deli_asset:
                        deli_asset.product_lease_end_date = recovery_asset.product_lease_end_date
                        deli_asset.save(update_fields=['product_lease_end_date'])
        return True
