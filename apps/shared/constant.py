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
    (1, 'Beneficiary'),
    (2, '1st manager'),
    (3, '2nd manager'),
    (4, 'Upper manager'),
    (5, 'Manager of x group level'),
)


# translate attribute value of above class
class WorkflowMsgNotify:
    new_task = 'New task'
    create_document = 'Create document'
    receive_document = 'Receive document'
    approved = 'Approved'
    rejected = 'Rejected'
    edit_by_zone = 'Edit data by zones'
    return_creator = 'Return to creator'
    document_returned = 'Document was returned'
    rerun_workflow = 'Rerun workflow'
    end_workflow = 'Workflow ended'

    @classmethod
    def translate_msg(cls, msg):
        # return _(msg)
        return msg


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
    'leave.leaverequest': 'title',
    'businesstrip.businessrequest': 'title',
    'assettools.assettoolsprovide': 'title',
    'assettools.assettoolsdelivery': 'title',
    'assettools.assettoolsreturn': 'title',
    'acceptance.finalacceptance': 'title',
    'project.projectbaseline': 'title',
    'contract.contractapproval': 'title',
    'production.productionorder': 'title',
    'production.workorder': 'title',
    'leaseorder.leaseorder': 'title',
    'inventory.goodsrecovery': 'title',
    'serviceorder.serviceorder': 'title',
    'servicequotation.servicequotation': 'title',
    # haind
    'cashoutflow.advancepayment': 'title',
    'cashoutflow.payment': 'title',
    'apinvoice.apinvoice': 'title',
    'arinvoice.arinvoice': 'title',
    'deliveryservice.deliveryservice': 'title',
    'inventory.goodsissue': 'title',
    'inventory.goodsreturn': 'title',
    'inventory.goodstransfer': 'title',
    'purchasing.purchasequotation': 'title',
    'purchasing.purchasequotationrequest': 'title',
    'purchasing.purchaserequest': 'title',
    'cashoutflow.returnadvance': 'title',
    'distributionplan.distributionplan': 'title',
    'production.bom': 'title',
    'reconciliation.reconciliation': 'title',
    'financialcashflow.cashinflow': 'title',
    'financialcashflow.cashoutflow': 'title',
    'productmodification.productmodification': 'title',
    'productmodificationbom.productmodificationbom': 'title',
    'equipmentloan.equipmentloan': 'title',
    'equipmentreturn.equipmentreturn': 'title',
    #
    'bidding.bidding': 'title',
    'consulting.consulting': 'title',
    'asset.fixedasset': 'title',
    'asset.instrumenttool': 'title',
    'asset.fixedassetwriteoff': 'title',
    'asset.instrumenttoolwriteoff': 'title',
    # KMS
    'documentapproval.kmsdocumentapproval': 'title',
    'incomingdocument.kmsincomingdocument': 'title',
    # HRM
    'absenceexplanation.absenceexplanation': 'title',
    'overtimerequest.overtimerequest': 'title',
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

PROJECT_WORK_STT = (
    (0, 'To do'),
    (1, 'In progress'),
    (2, 'Pending'),
    (3, 'Completed')
)

PROJECT_WORK_TYPE = (
    (0, 'Start to start'),
    (1, 'Finish to start')
)

# permissions
PERMISSION_OPTION_RANGE = (
    (0, 'All option range'),
    (1, 'Only company range'),
)

# Purchase request
REQUEST_FOR = [
    (0, _('For Sale Order')),
    (1, _('For Stock Free')),
    (2, _('For Fixed Asset')),
    (3, _('For Stock Plan')),
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
    (3, 'For product modification'),
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

# Goods transfer
GOODS_TRANSFER_TYPE = (
    (0, _('Goods transfer')),
    (1, _('Send/return consigned goods')),
    (2, _('Equipment loan')),
    (3, _('Equipment return')),
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
    (2, _('For Production')),
    (2, _('For Product Modification')),
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
    (5, 'Invoice'),
    (6, 'Project'),
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
    (4, _('Invoice')),
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

# Notify Push
PUSH_NOTIFY_TYPE = (
    (0, 'E-Mail'),
    (1, 'SMS'),
)

OTP_TYPE = (
    (0, 'E-Mail'),
    (1, 'SMS'),
    (2, 'Call'),
    (2, 'Application'),
    (4, 'Other'),
)

# ProductWarehouse
TYPE_LOT_TRANSACTION = (
    (0, 'Goods receipt'),
    (1, 'Delivery'),
    (2, 'Goods return'),
    (3, 'Goods transfer'),
    (4, 'Goods issue')
)

# Production order
TYPE_PRODUCTION = (
    (0, 'Production'),
    (1, 'Assembly'),
    (2, 'Disassembly'),
)

STATUS_PRODUCTION = (
    (0, 'Planned'),
    (1, 'In production'),
    (2, 'Done'),
)

# Production report
PRODUCTION_REPORT_TYPE = (
    (0, 'For production order'),
    (1, 'For work order'),
)

LIST_BANK = (
    (0, 'VBSP'),
    (1, 'VDP'),
    (3, 'Agribank'),
    (4, 'CB'),
    (5, 'Oceanbank'),
    (6, 'GPBank'),
    (7, 'BIDV'),
    (8, 'Vietcombank'),
    (9, 'Vietinbank'),
    (10, 'VPBank'),
    (11, 'MB'),
    (12, 'ACB'),
    (13, 'SHB'),
    (14, 'Techcombank'),
    (15, 'HDBank'),
    (16, 'LPBank'),
    (17, 'VIB'),
    (18, 'SeABank'),
    (19, 'TPBank'),
    (20, 'OCB'),
    (21, 'SCB'),
    (22, 'MSB'),
    (23, 'Sacombank'),
    (24, 'Eximbank'),
    (25, 'NCB'),
    (26, 'NamABank'),
    (27, 'ABBank'),
    (28, 'PVComBank'),
    (29, 'BacABank'),
    (30, 'VietBank'),
    (31, 'VAB'),
    (32, 'BVBank'),
    (33, 'DongABank'),
    (34, 'KLB'),
    (35, 'SaigonBank'),
    (36, 'Baoviet'),
    (37, 'PGBank'),
    (38, 'ShinhanBank'),
    (39, 'HSBC'),
    (40, 'StanChart'),
    (41, 'WooriBank'),
    (42, 'CIMB'),
    (43, 'PublicBank'),
    (44, 'HongLeongBank'),
    (45, 'UOB'),
    (46, 'Citibank'),
    (47, 'KBank'),
    (48, 'BangkokBank'),
    (49, 'DeutscheBank'),
)

# Recurrence
RECURRENCE_PERIOD = (
    (1, 'Daily'),
    (2, 'Weekly'),
    (3, 'Monthly'),
    (4, 'Yearly'),
)

RECURRENCE_STATUS = (
    (0, 'Active'),
    (1, 'Expired'),
)

RECURRENCE_ACTION = (
    (0, 'Wait'),
    (1, 'Done'),
    (2, 'Skip'),
)

CONTRACT_TYPE = (
    (0, 'Probationary contract'),
    (1, 'Labor contract'),
    (2, 'Addendum contract')
)

# Lease order
ASSET_TYPE = (
    (1, 'Product'),
    (2, 'Tool'),
    (3, 'Fixed asset'),
)

PRODUCT_CONVERT_INTO = (
    (1, _('Tool')),
    (2, _('Fixed asset')),
)

# goods recovery
STATUS_RECOVERY = (
    (0, 'Open'),
)

# Serial
SERIAL_STATUS = (
    (0, _('Available')),
    (1, _('Delivered')),
)

# kms
SECURITY_LEVEL = (
    (0, 'Low'),
    (1, 'Medium'),
    (2, 'High')
)


# shift master data
WORKING_DAYS = (
    (0, 'Mon'),
    (1, 'Tue'),
    (2, 'Wed'),
    (3, 'Thu'),
    (4, 'Fri'),
    (5, 'Sat'),
    (6, 'Sun'),
)


# attendance
ATTENDANCE_STATUS = (
    (0, 'Absent'),
    (1, 'Present'),
    (2, 'Leave'),
    (3, 'Business'),
    (4, 'Weekend'),
    (5, 'Holiday'),
    (6, 'Overtime'),
    (7, 'Overtime on business trip')
)

# absence explanation
ABSENCE_TYPE = (
    (0, 'Check in'),
    (1, 'Check out'),
    (2, 'All day')
)

# Attribute
PRICE_CONFIG_TYPE = (
    (0, 'Numeric'),
    (1, 'List'),
    (2, 'Warranty'),
)
