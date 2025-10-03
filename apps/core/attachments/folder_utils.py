__ALL__ = ['MODULE_MAPPING', 'HIERARCHY_RULES', 'APP_FIELD', 'APP_NAME']

from django.utils.translation import gettext_lazy as _

MODULE_MAPPING = {
    'system': {'name': 'System', 'id': '9ac02039-a9a4-42e9-825e-169f740b5b5b'},
    'sale': {  # SAlE
        'name': 'Sales', 'id': '76ab081b-eee4-4923-97b9-1cbb09deef78',
        'plan': '4e082324-45e2-4c27-a5aa-e16a758d5627'
    },
    'kms': {  # KMS
        'name': 'KMS', 'id': 'c7a702aa-10e7-487a-ab6c-3fd219930504', 'plan': '02793f68-3548-45c1-98f5-89899a963091'
    },
    'hrm': {  # HRM
        'name': 'HRM', 'id': '3802739f-12c8-4f90-ac67-3f81e21ccffe', 'plan': '395eb68e-266f-45b9-b667-bd2086325522'
    },
    'e-office': {  # E-Office
        'name': 'E-Office', 'id': '57bc22f9-08a8-4a4b-b207-51c0f6428c56', 'plan': 'a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8'
    }

}

HIERARCHY_RULES = {
    'sale': {
        'apinvoice': {},
        'arinvoice': {},
        'bidding': {},
        'advancepayment': {},
        'payment': {},
        'consulting': {},
        'contractapproval': {},
        'orderdeliverysub': {},
        'equipmentloan': {},
        'goodsissue': {},
        'goodsreceipt': {},
        'goodsreturn': {},
        'leaseorder': {},
        'opportunity': {
            'child': {
                'opportunitytask': {},
                'quotation': {},
                'saleorder': {},
                'leaseorder': {},
                'serviceorder': {
                    'child': {
                        'opportunitytask'
                    }
                }
            }
        },
        'purchaseorder': {},
        'purchasequotationrequest': {},
        'purchaserequest': {},
        'quotation': {},
        'saleorder': {},
        'serviceorder': {
            'child': {
                'opportunitytask'
            },
        },
        'opportunitytask': {}
    },
    'e-office': {
        'assettoolsreturn': {},
        'assettoolsdelivery': {},
        'assettoolsprovide': {},
        'businessrequest': {},
        'meetingschedule': {},
    },
    'hrm': {
        'employeeinfo': {
            'child': {
                'employeecontract': {}
            }
        },
    },
    'kms': {
        'kmsdocumentapproval': {},
        'kmsincomingdocument': {}
    }
}
# trường này để truy vấn ngược từ app con lên app cha thông qua field dược khai báo
APP_FIELD = {
    'employeeinfo': 'employee_info',
    'serviceorder': 'service_order_work_order_task_task',
    'opportunity': 'opportunity',
}
APP_NAME = {
    'apinvoice': _('AP Invoice'),
    'arinvoice': _('AR Invoice'),
    'bidding': _('Bidding'),
    'advancepayment': _('Advance Payment'),
    'payment': _('Payment'),
    'consulting': _('Consulting'),
    'contractapproval': _('Contract Approval'),
    'orderdeliverysub': _('Delivery'),
    'equipmentloan': _('Equipment Loan'),
    'goodsissue': _('Good Issue'),
    'goodsreceipt': _('Good Receipt'),
    'goodsreturn': _('Good Return'),
    'leaseorder': _('Lease Order'),
    'opportunity': _('Sale Projects'),
    'purchaseorder': _('Purchase Order'),
    'purchasequotationrequest': _('Purchase Quotation Request'),
    'purchaserequest': _('Purchase Request'),
    'quotation': _('Quotation'),
    'saleorder': _('Sale Order'),
    'serviceorder': _('Service Order'),
    'opportunitytask': _('Task'),
    'assettoolsreturn': _('Asset, Tools Return'),
    'assettoolsdelivery': _('Asset, Tools Delivery'),
    'assettoolsprovide': _('Asset, Tools Provide'),
    'businessrequest': _('Business Request'),
    'meetingschedule': _('Meeting Schedule'),
    'employeeinfo': _('Employee Info'),
    'kmsdocumentapproval': _('Document Approval'),
    'kmsincomingdocument': _('Incoming Document')
}

# APP_NAME = {**Application_crm_data, **Application_eOffice_data, **Application_hrm_data, **Application_kms_data}
