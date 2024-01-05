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
    WORKFLOW_NOT_ALLOW_CHANGE = _(
        "Don't permit edit, the flow have {} process using. Go to instructions page for the way apply new flow or "
        "reconfigure old flow."
    )
    WORKFLOW_APPLY_REQUIRED_WF = _("The workflow currently is required when mode is apply")
