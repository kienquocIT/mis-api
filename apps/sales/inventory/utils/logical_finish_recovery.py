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
                        model_product = DisperseModel(app_model='saledata.product').get_model()
                        if model_product and hasattr(model_product, 'objects'):
                            cloned_instance = deepcopy(original_instance)
                            # override data
                            cloned_instance.id = None  # Clear the primary key
                            cloned_instance.code = RecoveryFinishHandler.generate_code(
                                original_instance=original_instance,
                                model_product=model_product
                            ) # generate lease code
                            cloned_instance.stock_amount = 0
                            cloned_instance.wait_delivery_amount = 0
                            cloned_instance.wait_receipt_amount = 0
                            cloned_instance.production_amount = 0
                            cloned_instance.available_amount = 0

                            cloned_instance.save()  # Save as a new record
        return True

    @classmethod
    def find_max_number(cls, codes):
        current_year = str(timezone.now().year)
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
        current_year = str(timezone.now().year)
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
