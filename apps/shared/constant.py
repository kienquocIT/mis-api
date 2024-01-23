from django.utils.translation import gettext_lazy as _

from .translations import WorkflowMsg, LeaveMsg

#
KEY_GET_LIST_FROM_APP = 'list_from_app'
KEY_GET_LIST_FROM_OPP = 'filter_list_from_opp'
SPLIT_CODE_FROM_APP = '.'

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
WORKFLOW_IN_WF_OPTION = (
    (1, 'Position title'),
    (2, 'Employee'),
)
WORKFLOW_IN_WF_POSITION = (
    (1, '1st manager'),
    (2, '2nd manager'),
    (3, 'Beneficiary'),
)


# translate attribute value of above class
class WorkflowMsgNotify:
    new_task = 'New Task'
    was_return_begin = 'Was return owner'

    @classmethod
    def translate_msg(cls, msg):
        return _(msg)


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
    'quotation.quotation': 'title',
    'saleorder.saleorder': 'title',
    'delivery.orderdeliverysub': 'title',
    'purchasing.purchaseorder': 'title',
    'inventory.goodsreceipt': 'title',
    'purchasing.purchaserequest': 'title',
    'leave.leaverequest': 'title',
    'cashoutflow.payment': 'title',
    'businesstrip.businessrequest': 'title',
    'cashoutflow.advancepayment': 'title',
    'cashoutflow.returnadvance': 'title',
    'assettools.assettoolsprovide': 'title',
    'assettools.assettoolsdelivery': 'title',
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

# base IndicatorParam
INDICATOR_PARAM_TYPE = (
    (0, 'Indicator'),
    (1, 'Property'),
    (2, 'Function'),
    (3, 'Operator'),
)

# opportunity task
TASK_PRIORITY = (
    (0, 'Low'),
    (1, 'Medium'),
    (2, 'High')
)

TASK_KIND = (
    (0, 'Normal'),
    (1, 'To do'),
    (2, 'Completed'),
    (3, 'Pending')
)

# permissions
PERMISSION_OPTION_RANGE = (
    (0, 'All option range'),
    (1, 'Only company range'),
)

# Purchase request
REQUEST_FOR = [
    (0, _('For Sale Order')),
    (1, _('For Stock')),
    (2, _('For Other')),
]

PURCHASE_STATUS = [
    (0, _('Wait')),
    (1, _('Partially ordered')),
    (2, _('Ordered')),
]

# Purchase order
RECEIPT_STATUS = (
    (0, _('None')),
    (1, _('Wait')),
    (2, _('Partially received')),
    (3, _('Received')),
)

# Good receipt
GOODS_RECEIPT_TYPE = (
    (0, 'For purchase order'),
    (1, 'For inventory adjustment'),
    (2, 'For production'),
)

# e-office Leave
LEAVE_YEARS_SENIORITY = [
    {'from_range': 5, 'to_range': 9, 'added': 1},
    {'from_range': 10, 'to_range': 14, 'added': 2},
    {'from_range': 15, 'to_range': 19, 'added': 3},
    {'from_range': 20, 'to_range': 24, 'added': 4},
    {'from_range': 25, 'to_range': 29, 'added': 5},
    {'from_range': 30, 'to_range': 34, 'added': 6},
]

TYPE_LIST = (
    (1, LeaveMsg.TYPE_AD),
    (2, LeaveMsg.TYPE_SYS),
    (3, LeaveMsg.TYPE_EM),
)

# Warehouse type
WAREHOUSE_TYPE = (
    (0, 'None'),
    (1, _('Drop Ship')),
    (2, _('Bin Location')),
    (3, _('Agency / Partner Location')),
)

# Goods transfer
GOODS_TRANSFER_TYPE = (
    (0, _('Goods transfer')),
    (1, _('Send/return consigned goods')),
)

# Inventory Adjustment Item action type

IA_ITEM_ACTION_TYPE = (
    (0, _('Equal')),
    (1, _('Decreasing')),
    (2, _('Increasing')),
)

# Goods issue type

GOODS_ISSUE_TYPE = (
    (0, _('For Inventory Adjustment')),
    (1, _('Liquidation')),
)

RETURN_ADVANCE_MONEY_RECEIVED = (
    (True, _('Received money')),
    (False, _('Waiting')),
)

# Quotation/ SaleOrder Indicator
ACCEPTANCE_AFFECT_BY = (
    (1, 'None'),
    (2, 'Plan value'),
    (3, 'Delivery'),
    (4, 'Payment'),
)

# Opportunity
OPPORTUNITY_LOG_TYPE = (
    (0, 'Application'),
    (1, 'Task'),
    (2, 'Call'),
    (3, 'Email'),
    (4, 'Meeting'),
    (5, 'Document'),
)

# Sale order
SALE_ORDER_DELIVERY_STATUS = (
    (0, _('None')),
    (1, _('Delivering')),
    (2, _('Partially delivered')),
    (3, _('Delivered')),
)

PAYMENT_TERM_STAGE = (
    (0, _('Sale order')),
    (1, _('Contract')),
    (2, _('Delivery')),
    (3, _('Final acceptance')),
)

# REPORT
REPORT_CASHFLOW_TYPE = (
    (0, _('Operation')),
    (1, _('Beginning balance')),
    (2, _('Cash sales')),
    (3, _('Product/ service costs')),
    (4, _('Net cash flow')),
    (5, _('Ending balance')),
)
