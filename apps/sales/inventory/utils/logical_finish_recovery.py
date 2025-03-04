from copy import deepcopy

from django.utils import timezone

from apps.shared import DisperseModel


class RecoveryFinishHandler:

    @ classmethod
    def run_logics(cls, instance):
        for recovery_product in instance.recovery_product_recovery.all():
            # Trừ remain_recovery cho phiếu tiếp theo
            RecoveryFinishHandler.minus_remain(recovery_product=recovery_product)
            # Kiểm tra có thu hồi SP mới thì clone ra thành SP cho thuê
            RecoveryFinishHandler.clone_lease_product(instance=instance, recovery_product=recovery_product)
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
    def clone_lease_product(cls, instance, recovery_product):
        model_product = DisperseModel(app_model='saledata.product').get_model()
        if model_product and hasattr(model_product, 'objects'):
            original_instance = recovery_product.offset
            lease_time = recovery_product.product_quantity_time
            date_first_delivery = recovery_product.recovery_delivery.delivery_data.get(
                'actual_delivery_date', None
            ) if recovery_product.recovery_delivery else None
            check = recovery_product.quantity_recovery - len(recovery_product.product_quantity_leased_data)
            if original_instance and check > 0:
                cloned_instance = deepcopy(original_instance)
                # Override data
                cloned_instance.id = None  # Clear the primary key
                cloned_instance.code = ""  # Clear the code
                cloned_instance.date_created = timezone.now()
                cloned_instance.date_modified = timezone.now()
                cloned_instance.stock_amount = 0
                cloned_instance.wait_delivery_amount = 0
                cloned_instance.wait_receipt_amount = 0
                cloned_instance.production_amount = 0
                cloned_instance.available_amount = 0

                cloned_instance.lease_source = original_instance
                cloned_instance.lease_code = RecoveryFinishHandler.generate_code(
                    original_instance=original_instance,
                    model_product=model_product
                )  # Generate lease code
                cloned_instance.lease_time_previous = lease_time
                cloned_instance.origin_cost = recovery_product.product_unit_price
                cloned_instance.date_first_delivery = date_first_delivery
                cloned_instance.depreciation_price = recovery_product.product_depreciation_price
                cloned_instance.depreciation_method = recovery_product.product_depreciation_method
                cloned_instance.depreciation_adjustment = recovery_product.product_depreciation_adjustment
                cloned_instance.depreciation_time = recovery_product.product_depreciation_time
                cloned_instance.depreciation_start_date = recovery_product.product_depreciation_start_date
                cloned_instance.depreciation_end_date = recovery_product.product_depreciation_end_date

                cloned_instance.save()  # Save as a new record

                # handle after clone
                RecoveryFinishHandler.after_clone(
                    instance=instance, recovery_product=recovery_product, cloned_instance=cloned_instance
                )
        return True

    @classmethod
    def after_clone(cls, instance, recovery_product, cloned_instance):
        if cloned_instance:
            # Clone m2m
            RecoveryFinishHandler.clone_m2m(
                original_instance=cloned_instance.lease_source, cloned_instance=cloned_instance
            )
            # Push to product warehouse + product info
            for recovery_warehouse in recovery_product.recovery_warehouse_rp.filter(
                    recovery_product_leased__isnull=True
            ):
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
                        product_id=cloned_instance.id,
                        warehouse_id=warehouse_id,
                        uom_id=recovery_product.uom_id,
                        lot_data=[],
                        serial_data=serial_data,
                        amount=quantity_receipt,
                    )
                    # To product info
                    cloned_instance.save(**{
                        'update_stock_info': {
                            'quantity_receipt_po': 0,
                            'quantity_receipt_actual': quantity_receipt,
                            'system_status': 3,
                        },
                        'update_fields': ['wait_receipt_amount', 'available_amount', 'stock_amount']
                    })

    @classmethod
    def clone_m2m(cls, original_instance, cloned_instance):
        model_m2m_type = DisperseModel(app_model='saledata.productproducttype').get_model()
        if model_m2m_type and hasattr(model_m2m_type, 'objects'):
            # model_m2m_type.objects.bulk_create(
            #     [model_m2m_type(
            #         product=cloned_instance, product_type=product_type,
            #     ) for product_type in original_instance.general_product_types_mapped.all()]
            # )
            for product_type in original_instance.general_product_types_mapped.all():
                model_m2m_type.objects.create(product=cloned_instance, product_type=product_type,)
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
