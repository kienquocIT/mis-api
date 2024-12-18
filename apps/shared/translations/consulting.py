from django.utils.translation import gettext_lazy as _


class ConsultingMsg:
    PRODUCT_CATEGORY_NOT_EXIST = _('Product Category does not exist')
    ESTIMATED_VALUE_NOT_EQUAL_TOTAL_VALUE = _('Estimated value must be equal to the sum of product category value')
    CONSULTING_VALUE_NOT_NEGATIVE = _('Value must be greater than 0')
    ERROR_CREATE_CONSULTING = _('Error creating consulting')
