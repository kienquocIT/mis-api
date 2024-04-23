from apps.masterdata.saledata.models import ProductWareHouse


class GRFinishHandler:
    @classmethod
    def update_gr_info_for_po(cls, instance):
        if instance.goods_receipt_type == 0:  # GR for PO
            for gr_po_product in instance.goods_receipt_product_goods_receipt.all():
                gr_po_product.purchase_order_product.gr_completed_quantity += gr_po_product.quantity_import
                gr_po_product.purchase_order_product.gr_completed_quantity = round(
                    gr_po_product.purchase_order_product.gr_completed_quantity,
                    2
                )
                gr_po_product.purchase_order_product.gr_remain_quantity -= gr_po_product.quantity_import
                gr_po_product.purchase_order_product.gr_remain_quantity = round(
                    gr_po_product.purchase_order_product.gr_remain_quantity,
                    2
                )
                gr_po_product.purchase_order_product.save(update_fields=['gr_completed_quantity', 'gr_remain_quantity'])
            for gr_pr_product in instance.goods_receipt_request_product_goods_receipt.all():
                gr_pr_product.purchase_order_request_product.gr_completed_quantity += gr_pr_product.quantity_import
                gr_pr_product.purchase_order_request_product.gr_completed_quantity = round(
                    gr_pr_product.purchase_order_request_product.gr_completed_quantity,
                    2
                )
                gr_pr_product.purchase_order_request_product.gr_remain_quantity -= gr_pr_product.quantity_import
                gr_pr_product.purchase_order_request_product.gr_remain_quantity = round(
                    gr_pr_product.purchase_order_request_product.gr_remain_quantity,
                    2
                )
                gr_pr_product.purchase_order_request_product.save(update_fields=[
                    'gr_completed_quantity',
                    'gr_remain_quantity'
                ])
        return True

    @classmethod
    def update_is_all_receipted_po(cls, instance):
        if instance.purchase_order:
            po_product = instance.purchase_order.purchase_order_product_order.all()
            po_product_done = instance.purchase_order.purchase_order_product_order.filter(gr_remain_quantity=0)
            if po_product.count() == po_product_done.count():
                instance.purchase_order.receipt_status = 3
                instance.purchase_order.is_all_receipted = True
                instance.purchase_order.save(update_fields=['receipt_status', 'is_all_receipted'])
            else:
                instance.purchase_order.receipt_status = 2
                instance.purchase_order.save(update_fields=['receipt_status'])
        return True

    @classmethod
    def push_by_po(cls, instance):
        for gr_warehouse in instance.goods_receipt_warehouse_goods_receipt.all():
            uom_product_inventory = gr_warehouse.goods_receipt_product.product.inventory_uom
            uom_product_gr = gr_warehouse.goods_receipt_product.uom
            if gr_warehouse.goods_receipt_request_product:  # Case has PR
                if gr_warehouse.goods_receipt_request_product.purchase_order_request_product:
                    pr_product = gr_warehouse.goods_receipt_request_product.purchase_order_request_product
                    if pr_product.is_stock is False:  # Case PR is Product
                        if pr_product.purchase_request_product:
                            uom_product_gr = pr_product.purchase_request_product.uom
                    else:  # Case PR is Stock
                        uom_product_gr = pr_product.uom_stock
            final_ratio = 1
            if uom_product_inventory and uom_product_gr:
                final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
            lot_data = []
            serial_data = []
            for lot in gr_warehouse.goods_receipt_lot_gr_warehouse.all():
                if lot.lot:
                    lot.lot.quantity_import += lot.quantity_import * final_ratio
                    lot.lot.save(update_fields=['quantity_import'])
                else:
                    lot_data.append({
                        'lot_number': lot.lot_number,
                        'quantity_import': lot.quantity_import * final_ratio,
                        'expire_date': lot.expire_date,
                        'manufacture_date': lot.manufacture_date,
                        'goods_receipt_id': instance.id,
                    })
            for serial in gr_warehouse.goods_receipt_serial_gr_warehouse.all():
                serial_data.append({
                    'vendor_serial_number': serial.vendor_serial_number,
                    'serial_number': serial.serial_number,
                    'expire_date': serial.expire_date,
                    'manufacture_date': serial.manufacture_date,
                    'warranty_start': serial.warranty_start,
                    'warranty_end': serial.warranty_end,
                    'goods_receipt_id': instance.id,
                })
            ProductWareHouse.push_from_receipt(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product_id=gr_warehouse.goods_receipt_product.product_id,
                warehouse_id=gr_warehouse.warehouse_id,
                uom_id=uom_product_inventory.id,
                tax_id=gr_warehouse.goods_receipt_product.product.purchase_tax_id,
                amount=gr_warehouse.quantity_import * final_ratio,
                unit_price=gr_warehouse.goods_receipt_product.product_unit_price,
                lot_data=lot_data,
                serial_data=serial_data,
            )
        return True

    @classmethod
    def push_by_ia(cls, instance):
        for gr_warehouse in instance.goods_receipt_warehouse_goods_receipt.all():
            uom_product_inventory = gr_warehouse.goods_receipt_product.product.inventory_uom
            uom_product_gr = gr_warehouse.goods_receipt_product.uom
            final_ratio = 1
            if uom_product_inventory and uom_product_gr:
                final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
            lot_data = []
            serial_data = []
            for lot in gr_warehouse.goods_receipt_lot_gr_warehouse.all():
                if lot.lot:  # if GR for exist LOT => update quantity
                    lot.lot.quantity_import += lot.quantity_import * final_ratio
                    lot.lot.save(update_fields=['quantity_import'])
                else:  # GR with new LOTS => setup data to create ProductWarehouseLot
                    lot_data.append({
                        'lot_number': lot.lot_number,
                        'quantity_import': lot.quantity_import * final_ratio,
                        'expire_date': lot.expire_date,
                        'manufacture_date': lot.manufacture_date,
                        'goods_receipt_id': instance.id,
                    })
            for serial in gr_warehouse.goods_receipt_serial_gr_warehouse.all():
                serial_data.append({
                    'vendor_serial_number': serial.vendor_serial_number,
                    'serial_number': serial.serial_number,
                    'expire_date': serial.expire_date,
                    'manufacture_date': serial.manufacture_date,
                    'warranty_start': serial.warranty_start,
                    'warranty_end': serial.warranty_end,
                    'goods_receipt_id': instance.id,
                })
            ProductWareHouse.push_from_receipt(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product_id=gr_warehouse.goods_receipt_product.product_id,
                warehouse_id=gr_warehouse.warehouse_id,
                uom_id=uom_product_inventory.id,
                tax_id=gr_warehouse.goods_receipt_product.product.purchase_tax_id,
                amount=gr_warehouse.goods_receipt_product.quantity_import * final_ratio,
                unit_price=gr_warehouse.goods_receipt_product.product_unit_price,
                lot_data=lot_data,
                serial_data=serial_data,
            )
        return True

    @classmethod
    def push_to_product_warehouse(cls, instance):
        # push data to ProductWareHouse
        if instance.goods_receipt_type == 0:  # GR for PO
            cls.push_by_po(instance=instance)
        elif instance.goods_receipt_type == 1:  # GR for IA
            cls.push_by_ia(instance=instance)
        return True

    @classmethod
    def update_product_wait_receipt_amount(cls, instance):
        if instance.purchase_order:  # GR for PO
            for product_receipt in instance.goods_receipt_product_goods_receipt.all():
                uom_product_inventory = product_receipt.product.inventory_uom
                uom_product_gr = product_receipt.uom
                final_ratio = 1
                if uom_product_inventory and uom_product_gr:
                    final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
                product_receipt.product.save(**{
                    'update_transaction_info': True,
                    'quantity_receipt_po': product_receipt.quantity_import * final_ratio,
                    'update_fields': ['wait_receipt_amount', 'available_amount', 'stock_amount']
                })
        else:  # GR for IA
            for product_receipt in instance.goods_receipt_product_goods_receipt.all():
                uom_product_inventory = product_receipt.product.inventory_uom
                uom_product_gr = product_receipt.uom
                final_ratio = 1
                if uom_product_inventory and uom_product_gr:
                    final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
                product_receipt.product.save(**{
                    'update_transaction_info': True,
                    'quantity_receipt_ia': product_receipt.quantity_import * final_ratio,
                    'update_fields': ['available_amount', 'stock_amount']
                })
        return True
