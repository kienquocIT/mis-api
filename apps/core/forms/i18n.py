__all__ = ['FormMsg']

from django.utils.translation import gettext_lazy as _


class FormMsg:
    FORM_NOT_FOUND = _("The form is not found")
    FORM_REQUIRE_AUTHENTICATED = _('The form requires user authentication')
    FORM_SUBMIT_ONLY_ONE_PER_USER = _('The form allows submitting data only one time per user')
    FORM_ENTRY_EDIT_DENY = _("The update entry was not supported")
    FORM_DATA_CORRECT_TYPE = _("The data you have submitted is in an incorrect format")
    INPUT_DATA_LENGTH_INCORRECT = _("The input data is of incorrect length")
    FORM_CONFIG_EXCEPTION_DENY_RUNTIME_SUBMIT = _(
        "There was a problem with the form configuration so the data submission was rejected"
    )

    MINLENGTH_FAIL = _("The minimum value length is {0} characters")
    MAXLENGTH_FAIL = _("The maximum value length is {0} characters")
    REQUIRED_FAIL = _("This field is required")
    INPUT_TYPE_FAIL = _("The input data does not match the expected data type")
    INPUT_TEXT_CASE_FAIL = _("The input text base not match the expected \"{0}\" type")
    MIN_FAIL = _("The value must be greater than {0}")
    MAX_FAIL = _("The value must be less than {0}")
    CHARACTERS_LIMIT_FAIL = _("The value length must be between {0} and {1} characters")
    UNIT_CODE_FAIL = _("The unit code does not support")
    REGION_FAIL = _("The region does not support")
    EMAIL_TYPE_FAIL = _("The email data does not match the expected data type")
    EMAIL_ALLOW_FAIL = _("We cannot accept email addresses from this domain")
    EMAIL_RESTRICT_FAIL = _("We restrict email addresses from this domain")
    VALIDATE_VALUE_TYPE_FAIL_INT = _("This value should be of type integers")
    VALIDATE_VALUE_TYPE_FAIL_FLOAT = _("This value should be of type float")
    VALIDATE_VALUE_TYPE_FAIL_NUMBER = _("This value should be of type number")

    A_COPY = _("copy")
    FORM_COPY_FAILURE = _("The copy progress encountered a failure")
