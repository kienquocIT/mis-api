from django.utils.translation import gettext_lazy as _


class ShippingMsg:
    UNIT_NOT_EXIST = _('unit of shipping not exist.')
    GREAT_THAN_ZERO = _('must be greater than zero')
    LOCATION_NOT_EXIST = _('appears location does not exist')
    REQUIRED_AMOUNT = _('Amount is required')
    NOT_YET_CONDITION = _('Not yet condition')
    CONDITION_NOT_NULL = _("Condition can't not null or blank")
