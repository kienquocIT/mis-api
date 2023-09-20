from django.utils.translation import gettext_lazy as _


class OpportunityMsg:
    NOT_EXIST = _('does not exist')
    NOT_BLANK = _('dose not blank')
    VALUE_GREATER_THAN_ZERO = _('must be greater than zero')
    ACTIVITIES_CALL_LOG_RESULT_NOT_NULL = _('Result must not be null')
    EMAIL_TO_NOT_VALID = _('Email to is not valid.')
    EMAIL_CC_NOT_VALID = _('Email Cc is not valid.')
    ACTIVITIES_MEETING_RESULT_NOT_NULL = _('Result must not be null')
    CAN_NOT_SEND_EMAIL = _('Can not send email')

    MEMBER_NOT_EXIST = _('Member does not exist in sale team')

    EMPLOYEE_DELETE_NOT_EXIST = _('Employee delete does not exist in sale team')

    EXIST_TASK_NOT_COMPLETED = _('All her (his) tasks not completed')

    EMPLOYEE_CAN_NOT_DELETE = _('You can not delete member because you do not have permission')
    EMPLOYEE_CAN_ADD_MEMBER = _('You can not add member because you do not have permission')
    EMPLOYEE_NOT_IN_SALE_TEAM = _('You can not delete or add member because you not in sale team')

    APPLICATION_NOT_EXIST = _('Application not exist')
    NOT_EDIT_PERM_MEMBER = _('Only Sale Person can update member permissions')

    NOT_DELETE_SALE_PERSON = _('Can not delete sale person in sale team')
