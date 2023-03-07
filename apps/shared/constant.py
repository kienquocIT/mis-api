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
    (0, "Create"),
    (1, "Approve"),
    (2, "Reject"),
    (3, "Return"),
    (4, "Receive"),
    (5, "To do"),
)

OPTION_COLLABORATOR = (
    (0, "In form"),
    (1, "Out form"),
    (2, "In workflow"),
)

CONDITION_LOGIC = (
    (0, "And"),
    (1, "Or"),
)

