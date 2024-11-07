__all__ = [
    'ProcessMsg'
]

from django.utils.translation import gettext_lazy as _


class ProcessMsg:
    NOT_SUPPORT_WITHOUT_OPP = _(
        "Cannot start the process when Opportunity data is skipped because this configuration only supports Opportunity"
    )
    PROCESS_DEACTIVATE = _("The process is deactivate")
    PROCESS_NOT_FOUND = _("The process is not found")

    STAGES_APP_NOT_ANALYSE = _("Unable to analyze the application's data")
    STAGES_APP_NEED_AMOUNT = _(
        "The number of documents created must be greater than or equal to {amount} in order to complete."
    )
    OPP_NOT_MATCH = _("This opportunity does not match the process's opportunity")
    APPLICATION_NOT_SUPPORT = _("This process does not support this application")
    DOCUMENT_QUALITY_IS_FULL = _("The number of documents for this feature has reached its limit in process")

    PROCESS_STAGES_REQUIRED = _("Process requires at least 1 stage (except system stage)")
    APPLICATION_LEASE_ONE = _("Stages requires at least 1 application")
    APPLICATION_NOT_FOUND = _("Application is not found")
    MIN_MAX_INCORRECT = _("Min or Max value is incorrect")
    MAX_MUST_LARGE_MIN = _("The maximum value must be equal or greater than the minimum value")
    FINISH_MUST_LARGE_START = _("Finish date must be greater than start date")
