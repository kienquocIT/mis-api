from django.utils.translation import gettext_lazy as _


class KMSMsg:
    # document approval
    CREATE_APPROVAL_ERROR = _("Can not create document approval, please verify again.")
    INTERNAL_RECIPIENT_NOT_FOUND = _("Internal recipient not found")
    DUPLICATE_DATA_CODE = _("Code is exists")
    RECIPIENT_PERMISSION_ERROR = _("Permission recipient is missing")

    # incoming document
    CREATE_INCOMING_DOC_ERROR = _("Can not create incoming document, please verify again.")
    EXPIRED_DATE_ERROR = _('Expired date must be later than effective date.')
