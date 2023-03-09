from django.utils.translation import gettext_lazy as _


class WorkflowMsg:
    ACTION_CREATE = _("Create")
    ACTION_APPROVE = _("Approve")
    ACTION_REJECT = _("Reject")
    ACTION_RETURN = _("Return")
    ACTION_RECEIVE = _("Receive")
    ACTION_TODO = _("To do")
    COLLABORATOR_IN = _("In form")
    COLLABORATOR_OUT = _("Out form")
    COLLABORATOR_WF = _("In workflow")
