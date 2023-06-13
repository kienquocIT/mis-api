from django.utils.translation import gettext_lazy as _
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
WORKFLOW_CONFIG_MODE = (
    (0, 'UnApply'),
    (1, 'Apply'),
    (2, 'Pending'),
)
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
    'saledata.account': 'name',
}

CURRENCY_MASK_MONEY = {
    'VND': {
        'prefix': '',
        'suffix': ' VND',
        'affixesStay': True,
        'thousands': '.',
        'decimal': ',',
        'precision': 0,
        'allowZero': True,
        'allowNegative': False,
    },
    'USD': {
        'prefix': '$ ',
        'suffix': '',
        'affixesStay': True,
        'thousands': ',',
        'decimal': '.',
        'precision': 2,
        'allowZero': True,
        'allowNegative': True,
    }
}

ACCOUNT_COMPANY_SIZE = (
    (1, _('< 20 people')),
    (2, _('20-50 people')),
    (3, _('50-200 people')),
    (4, _('200-500 people')),
    (5, _('> 500 people')),
)

ACCOUNT_REVENUE = (
    (1, _('1-10 billions')),
    (2, _('10-20 billions')),
    (3, _('20-50 billions')),
    (4, _('50-200 billions')),
    (5, _('200-1000 billions')),
    (6, _('> 1000 billions')),
)

# sales delivery
DELIVERY_OPTION = (
    (0, 'Full'),
    (1, 'Partial'),
)
PICKING_STATE = (
    (0, 'Ready'),
    (1, 'Done'),
)
DELIVERY_STATE = (
    (0, 'Wait'),
    (1, 'Ready'),
    (2, 'Done'),
)
DELIVERY_WITH_KIND_PICKUP = (
    (0, 'Wait auto picking'),
    (1, 'Manual select product'),
)
