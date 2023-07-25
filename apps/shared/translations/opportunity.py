from django.utils.translation import gettext_lazy as _


class OpportunityMsg:
    NOT_EXIST = _('does not exist')
    NOT_BLANK = _('dose not blank')
    VALUE_GREATER_THAN_ZERO = _('must be greater than zero')
    ACTIVITIES_CALL_LOG_RESULT_NOT_NULL = _('Result must not be null')
    EMAIL_TO_NOT_VALID = _('Email to is not valid.')
    EMAIL_CC_NOT_VALID = _('Email Cc is not valid.')
    ACTIVITIES_MEETING_RESULT_NOT_NULL = _('Result must not be null')
