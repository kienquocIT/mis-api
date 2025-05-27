from django.conf import settings
from django.utils.translation import gettext_lazy as trans

from apps.shared import DisperseModel


__all__ = ['MailDataResolver']

# key: app_label.model_code | value: {"title": "app title", "url": đường dẫn đến trang chi tiết chức năng trên UI}
APP_MAP_DATA = {
    'quotation.quotation': {'title': 'Quotation', 'url': 'quotation/detail/'},
    'saleorder.saleorder': {'title': 'Sale Order', 'url': 'saleorder/detail/'},
    'cashoutflow.advancepayment': {'title': 'Advance Payment', 'url': 'cashoutflow/advance-payment/detail/'},
    'cashoutflow.payment': {'title': 'Payment', 'url': 'cashoutflow/payment/detail/'},
    'cashoutflow.returnadvance': {'title': 'Return Advance', 'url': 'cashoutflow/return-advance/detail/'},
    'purchasing.purchaserequest': {'title': 'Purchase Request', 'url': 'purchasing/purchase-request/detail/'},
    'purchasing.purchasequotationrequest': {
        'title': 'Purchase Quotation Request', 'url': 'purchasing/purchase-quotation-request/detail/'
    },
    'purchasing.purchasequotation': {'title': 'Purchase Quotation', 'url': 'purchasing/purchase-quotation/detail/'},
    'purchasing.purchaseorder': {'title': 'Purchase Order', 'url': 'purchasing/purchase-order/detail/'},
    'inventory.goodsissue': {'title': 'Goods Issue', 'url': 'inventory/goods-issue/detail/'},
    'inventory.goodsreceipt': {'title': 'Goods Receipt', 'url': 'inventory/goods-receipt/detail/'},
    'inventory.goodsreturn': {'title': 'Goods Return', 'url': 'inventory/goods-return/detail/'},
    'inventory.goodstransfer': {'title': 'Goods Transfer', 'url': 'inventory/goods-transfer/detail/'},
    'delivery.orderdeliverysub': {'title': 'Delivery', 'url': 'delivery/detail/'},
    'project.project': {'title': 'Project', 'url': 'project/detail/'},
    'leave.leaverequest': {'title': 'Leave', 'url': 'leave/requests/detail/'},
    'meetingschedule.meetingschedule': {'title': 'Meeting Schedule', 'url': 'meeting/meeting-schedule/detail/'},
    'businesstrip.businessrequest': {'title': 'Business trip', 'url': 'business-trip/request/detail/'},
    'assettools.assettoolsprovide': {'title': 'Asset, Tools Provide', 'url': 'asset-tools/provide/detail/'},
    'assettools.assettoolsdelivery': {'title': 'Asset, Tools Delivery', 'url': 'asset-tools/delivery/detail/'},
    'assettools.assettoolsreturn': {'title': 'Asset, Tools Return', 'url': 'asset-tools/return/detail/'},
    'employeeinfo.EmployeeContractRuntime': {
        'title': 'Contract signature detail', 'url': 'hrm/employee-data/runtime-signature/detail/'
    },
    'leaseorder.leaseorder': {'title': 'Lease Order', 'url': 'leaseorder/detail/'},
    'bidding.bidding': {'title': 'Bidding', 'url': 'bidding/detail/'},
    'consulting.consulting': {'title': 'Consulting', 'url': 'consulting/detail/'},
}

WORKFLOW_TYPE_MAP_TXT = {
    0: 'You have a new task.',
    1: 'Your document was returned.',
    2: 'Your document was approved.',
    3: 'Your document was rejected.',
}

WORKFLOW_COMMON = {
    0: 'Feature:',
    1: 'Go to detail:',
    3: 'Here',
}


class MailDataResolver:
    @classmethod
    def welcome(cls, user_obj):
        return {
            '_user': {
                'full_name': user_obj.get_full_name(),
                'user_name': user_obj.username,
            },
        }

    @classmethod
    def otp_verify(cls, user_obj, otp):
        return {
            'full_name': user_obj.get_full_name(),
            'user_name': user_obj.username,
            '_otp': str(otp) if otp else '',
        }

    @classmethod
    def calendar(cls):
        return {}

    @classmethod
    def workflow(cls, runtime_id, workflow_type, tenant_id, company_id):
        if runtime_id and settings.UI_DOMAIN_SUFFIX:
            model_runtime = DisperseModel(app_model="workflow.Runtime").get_model()
            model_tenant = DisperseModel(app_model='tenant.Tenant').get_model()
            if model_runtime and hasattr(
                    model_runtime, 'objects'
            ) and model_tenant and hasattr(
                model_tenant, 'objects'
            ):
                runtime_obj = model_runtime.objects.filter(
                    tenant_id=tenant_id, company_id=company_id, id=runtime_id
                ).first()
                tenant_obj = model_tenant.objects.filter(pk=tenant_id).first()
                return MailDataResolver.workflow_sub(
                    runtime_obj=runtime_obj, tenant_obj=tenant_obj, workflow_type=workflow_type
                )
        return {}

    @classmethod
    def workflow_sub(cls, runtime_obj, tenant_obj, workflow_type):
        if runtime_obj and tenant_obj:
            full_domain = f'{settings.UI_DOMAIN_PROTOCOL}://{tenant_obj.code.lower()}{settings.UI_DOMAIN_SUFFIX}'
            wf_application_title = ''
            wf_application_url = ''
            doc_id = ''
            wf_title = str(trans(WORKFLOW_TYPE_MAP_TXT.get(workflow_type, '')))
            if runtime_obj.app_code:
                wf_application_title = str(trans(APP_MAP_DATA.get(runtime_obj.app_code, {}).get('title', '')))
                wf_application_url = APP_MAP_DATA.get(runtime_obj.app_code, {}).get('url', '')
            if runtime_obj.doc_id:
                doc_id = str(runtime_obj.doc_id)
            wf_common_text_0 = str(trans(WORKFLOW_COMMON.get(0, '')))
            wf_common_text_1 = str(trans(WORKFLOW_COMMON.get(1, '')))
            wf_common_text_3 = str(trans(WORKFLOW_COMMON.get(3, '')))
            return {
                '_workflow': {
                    'wf_title': wf_title,
                    'wf_application_title': wf_application_title,
                    'wf_doc_id': doc_id,
                    'wf_common_text_0': wf_common_text_0,
                    'wf_common_text_1': wf_common_text_1,
                    'wf_common_text_2': f'{full_domain}/{wf_application_url}{doc_id}',
                    'wf_common_text_3': wf_common_text_3,
                },
            }
        return {}

    @classmethod
    def project_new(cls, tenant_obj, prj_owner, prj_member, prj_obj):
        full_domain = f'{settings.UI_DOMAIN_PROTOCOL}://{tenant_obj.code.lower()}{settings.UI_DOMAIN_SUFFIX}'
        prj_app_url = APP_MAP_DATA.get('project.project', {}).get('url', '')
        return {
            '_project': {
                'prj_title': prj_obj.title,
                'prj_member': prj_member.get_full_name(),
                'prj_owner': prj_owner.get_full_name(),
                'prj_url': f'{full_domain}/{prj_app_url}{prj_obj.id}'
            },
        }

    @classmethod
    def new_contract(cls, tenant_obj, assignee, employee_created, contract, signature_runtime):
        full_domain = f'{settings.UI_DOMAIN_PROTOCOL}://{tenant_obj.code.lower()}{settings.UI_DOMAIN_SUFFIX}'
        app_url = APP_MAP_DATA.get('employeeinfo.EmployeeContractRuntime', {}).get('url', '')
        return {
            '_contract': {
                'title': contract.title,
                'member': assignee.get_full_name(),
                'created_email': employee_created.get_full_name(),
                'url': f'{full_domain}/{app_url}{signature_runtime}'
            },
        }

    @classmethod
    def new_leave_approved(cls, tenant_obj, employee, day_off, date_back, link_id, employee_lead):
        full_domain = f'{settings.UI_DOMAIN_PROTOCOL}://{tenant_obj.code.lower()}{settings.UI_DOMAIN_SUFFIX}'
        app_url = APP_MAP_DATA.get('leave.leaverequest', {}).get('url', '')
        return {
            '_leave': {
                'employee': employee.get_full_name(),
                'leader_name': employee_lead.get('full_name'),
                'leader_email': employee_lead.get('email'),
                'day_off': day_off,
                'date_back': date_back,
                'url': f'{full_domain}/{app_url}{link_id}'
            },
        }
