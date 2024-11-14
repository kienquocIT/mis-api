from django.utils.translation import gettext_lazy as _


__all__ = ['OpportunityOnlyMsg']


class OpportunityOnlyMsg:
    OPP_NOT_EXIST = _('Opportunity does not exist')
    RESULT_NOT_NULL = _('Result must not be null')
    DONT_HAVE_PERMISSION = _('Permission denied')
    PIC_NOT_NULL = _('Person in charge is not null')
    EMP_NOT_EXIST = _('Employee does not exist')
