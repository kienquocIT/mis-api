from django.utils.translation import gettext_lazy as _


class BiddingMsg:
    ATTACHMENT_REQUIRED = _('Documents must have attachment')
    BID_SECURITY_TYPE_REQUIRED = _('If there is a bond value, must choose a security type')
    CAUSE_OF_LOST_REQUIRED = _('If bid status is lost, must choose at least one cause of lost')
    OTHER_REASON_REQUIRED = _('If cause of lost is "other reason", must specify the reason')
    BID_VALUE_NOT_NEGATIVE = _('Value must be greater than 0')
