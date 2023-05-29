from .translations import WorkflowMsg


# Core
GENDER_CHOICE = (
    ('male', 'Male'),
    ('female', 'Female')
)
DOCUMENT_MODE = (
    (0, 'Global'),
    (1, 'Private'),
    (2, 'Team'),
)

SYSTEM_STATUS = (
    (0, 'Draft'),
    (1, 'Created'),
    (2, 'Added'),
    (3, 'Finish'),
    (4, 'Cancel'),
)

# Perm
PERMISSION_OPTION = (
    (1, 'Of owner'),
    (2, "All staff of owner"),
    (3, "All staff in owner group"),
    (4, "All staff in owner company"),
)

# workflow
WORKFLOW_ACTION = (
    (0, WorkflowMsg.ACTION_CREATE),
    (1, WorkflowMsg.ACTION_APPROVE),
    (2, WorkflowMsg.ACTION_REJECT),
    (3, WorkflowMsg.ACTION_RETURN),
    (4, WorkflowMsg.ACTION_RECEIVE),
    (5, WorkflowMsg.ACTION_TODO),
)

OPTION_COLLABORATOR = (
    (0, WorkflowMsg.COLLABORATOR_IN),
    (1, WorkflowMsg.COLLABORATOR_OUT),
    (2, WorkflowMsg.COLLABORATOR_WF),
)

CONDITION_LOGIC = (
    (0, "And"),
    (1, "Or"),
)

MAP_FIELD_TITLE = {
    'saledata.contact': 'fullname',
}
