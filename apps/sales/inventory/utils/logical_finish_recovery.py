from copy import deepcopy

from django.utils import timezone

from apps.shared import DisperseModel


class RecoveryFinishHandler:

    @classmethod
    def clone_product_to_lease_product(cls, instance):
        for lease_generate in instance.recovery_lease_generate_recovery.all():
            if lease_generate.recovery_warehouse:
                if lease_generate.recovery_warehouse.recovery_product:
                    if lease_generate.recovery_warehouse.recovery_product.offset:
                        original_instance = lease_generate.recovery_warehouse.recovery_product.offset
                        price = lease_generate.recovery_warehouse.recovery_product.product_depreciation_price
                        model_product = DisperseModel(app_model='saledata.product').get_model()
                        if model_product and hasattr(model_product, 'objects'):
                            cloned_instance = deepcopy(original_instance)
                            # Override data
                            cloned_instance.id = None  # Clear the primary key
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
                            cloned_instance.lease_depreciation_price = price
                            cloned_instance.serial_data = lease_generate.serial_data

                            cloned_instance.save()  # Save as a new record

                            # Push to product warehouse + product info
                            if cloned_instance:
                                product_id = cloned_instance.id
                                warehouse_id = lease_generate.recovery_warehouse.warehouse_id
                                uom_id = lease_generate.recovery_warehouse.recovery_product.uom_id
                                # To product warehouse
                                cls.run_push_to_warehouse_stock(
                                    instance=instance, product_id=product_id, warehouse_id=warehouse_id, uom_id=uom_id
                                )
                                # To product info
                                cloned_instance.save(**{
                                    'update_stock_info': {
                                        'quantity_receipt_po': 0,
                                        'quantity_receipt_actual': 1,
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
            company_id=company_id, code__icontains=base_code
        ).values_list('code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            code = f'{original_code}{current_year}0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'{original_code}{current_year}{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if model_product.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(original_instance=original_instance, model_product=model_product)
        return code

    # PRODUCT WAREHOUSE
    @classmethod
    def run_push_to_warehouse_stock(cls, instance, product_id, warehouse_id, uom_id):
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
                amount=1,
                lot_data=[],
                serial_data=[],
            )
        return True
