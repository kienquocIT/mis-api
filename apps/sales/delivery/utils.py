from rest_framework import serializers

from apps.shared.translations.sales import DeliverMsg


class CommonFunc:
    @classmethod
    def check_update_prod_and_emp(cls, instance, validate_data):
        crt_emp = str(instance.employee_inherit_id)
        is_same_emp = False
        if crt_emp == str(validate_data['employee_inherit_id']):
            is_same_emp = True
        if 'products' in validate_data and len(validate_data['products']) > 0 and not is_same_emp:
            raise serializers.ValidationError(
                {
                    'detail': DeliverMsg.ERROR_UPDATE_RULE
                }
            )
        return True
