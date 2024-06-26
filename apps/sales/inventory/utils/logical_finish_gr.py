from apps.masterdata.saledata.models import ProductWareHouse


class GRFinishHandler:
    @classmethod
    def update_gr_info_for_po(cls, instance):
        if instance.goods_receipt_type == 0:  # check type GR for PO
            for gr_po_product in instance.goods_receipt_product_goods_receipt.all():
                if gr_po_product.purchase_order_product:
                    gr_po_product.purchase_order_product.gr_completed_quantity += gr_po_product.quantity_import
                    gr_po_product.purchase_order_product.gr_completed_quantity = round(
                        gr_po_product.purchase_order_product.gr_completed_quantity, 2
                    )
                    gr_po_product.purchase_order_product.gr_remain_quantity -= gr_po_product.quantity_import
                    gr_po_product.purchase_order_product.gr_remain_quantity = round(
                        gr_po_product.purchase_order_product.gr_remain_quantity, 2
                    )
                    gr_po_product.purchase_order_product.save(update_fields=[
                        'gr_completed_quantity', 'gr_remain_quantity'
                    ])
            for gr_pr_product in instance.goods_receipt_request_product_goods_receipt.all():
                if gr_pr_product.purchase_order_request_product:
                    gr_pr_product.purchase_order_request_product.gr_completed_quantity += gr_pr_product.quantity_import
                    gr_pr_product.purchase_order_request_product.gr_completed_quantity = round(
                        gr_pr_product.purchase_order_request_product.gr_completed_quantity, 2
                    )
                    gr_pr_product.purchase_order_request_product.gr_remain_quantity -= gr_pr_product.quantity_import
                    gr_pr_product.purchase_order_request_product.gr_remain_quantity = round(
                        gr_pr_product.purchase_order_request_product.gr_remain_quantity, 2
                    )
                    gr_pr_product.purchase_order_request_product.save(update_fields=[
                        'gr_completed_quantity',
                        'gr_remain_quantity'
                    ])
        return True

    @classmethod
    def update_gr_info_for_ia(cls, instance):
        if instance.goods_receipt_type == 1:  # check type GR for IA
            for gr_ia_product in instance.goods_receipt_product_goods_receipt.all():
                if gr_ia_product.ia_item:
                    gr_ia_product.ia_item.gr_completed_quantity += gr_ia_product.quantity_import
                    gr_ia_product.ia_item.gr_completed_quantity = round(
                        gr_ia_product.ia_item.gr_completed_quantity, 2
                    )
                    gr_ia_product.ia_item.gr_remain_quantity -= gr_ia_product.quantity_import
                    gr_ia_product.ia_item.gr_remain_quantity = round(
                        gr_ia_product.ia_item.gr_remain_quantity, 2
                    )
                    gr_ia_product.ia_item.save(update_fields=['gr_completed_quantity', 'gr_remain_quantity'])
        return True

    @classmethod
    def update_is_all_receipted_po(cls, instance):
        if instance.goods_receipt_type == 0 and instance.purchase_order:
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
    def update_is_all_receipted_ia(cls, instance):
        if instance.goods_receipt_type == 1 and instance.inventory_adjustment:
            ia_product = instance.inventory_adjustment.inventory_adjustment_item_mapped.all()
            ia_product_done = instance.inventory_adjustment.inventory_adjustment_item_mapped.filter(
                gr_remain_quantity=0
            )
            if ia_product.count() == ia_product_done.count():
                instance.inventory_adjustment.state = True
                instance.inventory_adjustment.save(update_fields=['state'])
        return True

    @classmethod
    def push_by_po(cls, instance):
        for gr_warehouse in instance.goods_receipt_warehouse_goods_receipt.all():
            if gr_warehouse.is_additional is False:  # check if not additional by Goods Detail
                uom_base, final_ratio, lot_data, serial_data = cls.setup_data_push_by_po(
                    instance=instance, gr_warehouse=gr_warehouse,
                )
                gr_product = gr_warehouse.goods_receipt_product
                if gr_product:
                    if gr_product.product:
                        ProductWareHouse.push_from_receipt(
                            tenant_id=instance.tenant_id,
                            company_id=instance.company_id,
                            product_id=gr_product.product_id,
                            warehouse_id=gr_warehouse.warehouse_id,
                            uom_id=uom_base.id,
                            tax_id=gr_product.product.purchase_tax_id,
                            amount=gr_warehouse.quantity_import * final_ratio,
                            unit_price=gr_product.product_unit_price,
                            lot_data=lot_data,
                            serial_data=serial_data,
                        )
        return True

    @classmethod
    def setup_data_push_by_po(cls, instance, gr_warehouse):
        product_obj = gr_warehouse.goods_receipt_product.product
        uom_product_gr = gr_warehouse.goods_receipt_product.uom
        if gr_warehouse.goods_receipt_request_product:  # Case has PR
            if gr_warehouse.goods_receipt_request_product.purchase_order_request_product:
                pr_product = gr_warehouse.goods_receipt_request_product.purchase_order_request_product
                if pr_product.is_stock is False:  # Case PR is Product
                    if pr_product.purchase_request_product:
                        uom_product_gr = pr_product.purchase_request_product.uom
                else:  # Case PR is Stock
                    uom_product_gr = pr_product.uom_stock
        final_ratio = cls.get_final_uom_ratio(
            product_obj=product_obj, uom_transaction=uom_product_gr
        )
        uom_base = cls.get_uom_base(product_obj=product_obj)
        lot_data = []
        serial_data = []
        for lot in gr_warehouse.goods_receipt_lot_gr_warehouse.all():
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
        return uom_base, final_ratio, lot_data, serial_data

    @classmethod
    def push_by_ia(cls, instance):
        for gr_warehouse in instance.goods_receipt_warehouse_goods_receipt.all():
            if gr_warehouse.is_additional is False:  # check if not additional by Goods Detail
                uom_base, final_ratio, lot_data, serial_data = cls.setup_data_push_by_ia(
                    instance=instance,
                    gr_warehouse=gr_warehouse,
                )
                gr_product = gr_warehouse.goods_receipt_product
                if gr_product:
                    if gr_product.product:
                        ProductWareHouse.push_from_receipt(
                            tenant_id=instance.tenant_id,
                            company_id=instance.company_id,
                            product_id=gr_product.product_id,
                            warehouse_id=gr_warehouse.warehouse_id,
                            uom_id=uom_base.id,
                            tax_id=gr_product.product.purchase_tax_id,
                            amount=gr_product.quantity_import * final_ratio,
                            unit_price=gr_product.product_unit_price,
                            lot_data=lot_data,
                            serial_data=serial_data,
                        )
        return True

    @classmethod
    def setup_data_push_by_ia(cls, instance, gr_warehouse):
        product_obj = gr_warehouse.goods_receipt_product.product
        uom_product_gr = gr_warehouse.goods_receipt_product.uom
        final_ratio = cls.get_final_uom_ratio(
            product_obj=product_obj, uom_transaction=uom_product_gr
        )
        uom_base = cls.get_uom_base(product_obj=product_obj)
        lot_data = []
        serial_data = []
        for lot in gr_warehouse.goods_receipt_lot_gr_warehouse.all():
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
        return uom_base, final_ratio, lot_data, serial_data

    @classmethod
    def push_to_warehouse_stock(cls, instance):
        # push data to ProductWareHouse
        if instance.goods_receipt_type == 0:  # GR for PO
            cls.push_by_po(instance=instance)
        elif instance.goods_receipt_type == 1:  # GR for IA
            cls.push_by_ia(instance=instance)
        return True

    @classmethod
    def push_product_info(cls, instance):
        if instance.purchase_order:  # GR for PO
            for product_receipt in instance.goods_receipt_product_goods_receipt.all():
                quantity_receipt_actual = 0
                for product_wh in product_receipt.goods_receipt_warehouse_gr_product.all():
                    if product_wh.is_additional is False:
                        quantity_receipt_actual += product_wh.quantity_import
                final_ratio = cls.get_final_uom_ratio(
                    product_obj=product_receipt.product, uom_transaction=product_receipt.uom
                )
                product_receipt.product.save(**{
                    'update_stock_info': {
                        'quantity_receipt_po': product_receipt.quantity_import * final_ratio,
                        'quantity_receipt_actual': quantity_receipt_actual * final_ratio,
                        'system_status': instance.system_status,
                    },
                    'update_fields': ['wait_receipt_amount', 'available_amount', 'stock_amount']
                })
        else:  # GR for IA
            for product_receipt in instance.goods_receipt_product_goods_receipt.all():
                quantity_receipt_actual = 0
                if product_receipt.is_additional is False:
                    quantity_receipt_actual += product_receipt.quantity_import
                final_ratio = cls.get_final_uom_ratio(
                    product_obj=product_receipt.product, uom_transaction=product_receipt.uom
                )
                product_receipt.product.save(**{
                    'update_stock_info': {
                        'quantity_receipt_ia': quantity_receipt_actual * final_ratio,
                        'system_status': instance.system_status,
                    },
                    'update_fields': ['available_amount', 'stock_amount']
                })
        return True

    @classmethod
    def get_final_uom_ratio(cls, product_obj, uom_transaction):
        if product_obj.general_uom_group:
            uom_base = product_obj.general_uom_group.uom_reference
            if uom_base and uom_transaction:
                return uom_transaction.ratio / uom_base.ratio if uom_base.ratio > 0 else 1
        return 1

    @classmethod
    def get_uom_base(cls, product_obj):
        if product_obj.general_uom_group:
            return product_obj.general_uom_group.uom_reference
        return None
