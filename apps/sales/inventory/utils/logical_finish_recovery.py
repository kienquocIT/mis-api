from django.utils import timezone

from apps.shared import DisperseModel


class RecoveryFinishHandler:

    @ classmethod
    def run_logics(cls, instance):
        for recovery_product in instance.recovery_product_recovery.all():
            # Trừ remain_recovery cho phiếu tiếp theo
            RecoveryFinishHandler.minus_remain(recovery_product=recovery_product)
            # Kiểm tra có thu hồi SP đã cho thuê thì chỉ cập nhật dữ liệu
            RecoveryFinishHandler.update_leased_product(instance=instance, recovery_product=recovery_product)
        return True

    @classmethod
    def minus_remain(cls, recovery_product):
        if recovery_product.recovery_delivery and recovery_product.product and recovery_product.offset:
            check = recovery_product.quantity_recovery - len(recovery_product.product_quantity_leased_data)
            deli_product = recovery_product.offset.delivery_product_offset.filter(
                delivery_sub=recovery_product.recovery_delivery.delivery
            ).first()
            if deli_product:
                deli_product.quantity_remain_recovery -= recovery_product.quantity_recovery
                deli_product.quantity_new_remain_recovery -= check
                deli_product.save(**{
                    'for_goods_recovery': True,
                    'update_fields': ['quantity_remain_recovery', 'quantity_new_remain_recovery']
                })
            for product_leased in recovery_product.recovery_product_leased_recovery_product.all():
                deli_product_leased = product_leased.offset.delivery_product_leased_offset.filter(
                    delivery_product__delivery_sub=product_leased.recovery_product.recovery_delivery.delivery,
                    product_id=product_leased.product_id,
                ).first()
                if deli_product_leased:
                    deli_product_leased.quantity_leased_remain_recovery -= product_leased.quantity_recovery
                    deli_product_leased.save(update_fields=['quantity_leased_remain_recovery'])

        return True

    @classmethod
    def update_leased_product(cls, instance, recovery_product):
        # Push to product warehouse + product info
        for recovery_warehouse in recovery_product.recovery_warehouse_rp.filter(
                recovery_product_leased__isnull=False
        ):
            if recovery_warehouse.recovery_product_leased.offset:
                warehouse_id = recovery_warehouse.warehouse_id
                quantity_receipt = recovery_warehouse.quantity_recovery
                if warehouse_id and quantity_receipt > 0:
                    # To product warehouse
                    serial_data = [{
                        'vendor_serial_number': lease_generate.serial.vendor_serial_number,
                        'serial_number': lease_generate.serial.serial_number,
                        'expire_date': lease_generate.serial.expire_date,
                        'manufacture_date': lease_generate.serial.manufacture_date,
                        'warranty_start': lease_generate.serial.warranty_start,
                        'warranty_end': lease_generate.serial.warranty_end,
                    } for lease_generate in recovery_warehouse.recovery_lease_generate_rw.filter(serial__isnull=False)]
                    cls.run_push_to_warehouse_stock(
                        instance=instance,
                        product_id=recovery_warehouse.recovery_product_leased.offset_id,
                        warehouse_id=warehouse_id,
                        uom_id=recovery_product.uom_id,
                        lot_data=[],
                        serial_data=serial_data,
                        amount=quantity_receipt,
                    )
                    # To product info
                    recovery_warehouse.recovery_product_leased.offset.save(**{
                        'update_stock_info': {
                            'quantity_receipt_po': 0,
                            'quantity_receipt_actual': quantity_receipt,
                            'system_status': 3,
                        },
                        'update_fields': ['wait_receipt_amount', 'available_amount', 'stock_amount']
                    })
        return True

    @classmethod
    def find_max_number(cls, codes):
        current_year = str(timezone.now().year)[-2:]
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split(current_year)[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, original_instance, model_product):
        company_id = original_instance.company_id
        original_code = original_instance.code
        current_year = str(timezone.now().year)[-2:]
        base_code = f'{original_code}{current_year}'
        existing_codes = model_product.objects.filter(
            company_id=company_id, lease_code__icontains=base_code
        ).values_list('lease_code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            code = f'{original_code}{current_year}0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'{original_code}{current_year}{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if model_product.objects.filter(lease_code=code, company_id=company_id).exists():
            return cls.generate_code(original_instance=original_instance, model_product=model_product)
        return code

    # PRODUCT WAREHOUSE
    @classmethod
    def run_push_to_warehouse_stock(cls, instance, product_id, warehouse_id, uom_id, lot_data, serial_data, amount):
        model_target = DisperseModel(app_model='saledata.productwarehouse').get_model()
        if model_target and hasattr(model_target, 'objects') and hasattr(model_target, 'push_from_receipt'):
            model_target.push_from_receipt(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product_id=product_id,
                warehouse_id=warehouse_id,
                uom_id=uom_id,
                tax_id=None,
                unit_price=0,
                amount=amount,
                lot_data=lot_data,
                serial_data=serial_data,
            )
        return True
