import json
from apps.masterdata.saledata.models.periods import Periods
from apps.core.company.models import Company, CompanyFunctionNumber
from apps.masterdata.saledata.models.product import (
    ProductType, Product, UnitOfMeasure, UnitOfMeasureGroup
)
from apps.masterdata.saledata.models.price import (
    Tax, TaxCategory, Currency
)
from apps.masterdata.saledata.models.accounts import (
    Account, AccountCreditCards, AccountActivity, AccountContacts
)
from apps.core.base.models import (
    PlanApplication, ApplicationProperty, Application, SubscriptionPlan, NProvince, NWard
)
from apps.core.tenant.models import Tenant, TenantPlan
from apps.sales.cashoutflow.models import (
    AdvancePaymentCost, PaymentCost, AdvancePayment, Payment, ReturnAdvanceCost
)
from apps.core.workflow.models import (
    WorkflowConfigOfApp, Workflow, Runtime, RuntimeStage, RuntimeAssignee, RuntimeLog
)
from apps.masterdata.saledata.models import (
    ProductWareHouse, ProductWareHouseLot, ProductWareHouseSerial, DocumentType,
    FixedAssetClassificationGroup, FixedAssetClassification, Salutation, AccountGroup, Industry, AccountType, Contact,
)
from . import MediaForceAPI, DisperseModel

from .extends.signals import ConfigDefaultData, SaleDefaultData
from .permissions.util import PermissionController
from ..accounting.accountingsettings.models import DimensionSyncConfig
from ..accounting.accountingsettings.utils.dimension_utils import DimensionUtils
from ..core.account.models import User
from ..core.attachments.folder_utils import MODULE_MAPPING
from ..core.attachments.models import Folder
from ..core.hr.models import (
    Employee, Role, EmployeePermission, RolePermission,
)
from ..core.mailer.models import MailTemplateSystem
from ..core.provisioning.utils import TenantController
from ..eoffice.leave.leave_util import leave_available_map_employee
from ..eoffice.leave.models import LeaveAvailable, WorkingYearConfig, WorkingHolidayConfig, LeaveRequest
from ..hrm.employeeinfo.models import EmployeeHRNotMapEmployeeHRM
from ..hrm.payrolltemplate.models import AttributeComponent
from ..masterdata.promotion.models import Promotion
from ..masterdata.saledata.models.product_warehouse import ProductWareHouseLotTransaction
from ..sales.apinvoice.models import APInvoice, APInvoiceGoodsReceipt
from ..sales.arinvoice.models import ARInvoice, ARInvoiceItems, ARInvoiceDelivery
from ..sales.arinvoice.utils.logical_finish import ARInvoiceFinishHandler
from ..sales.delivery.models import DeliveryConfig, OrderDeliverySub, OrderDeliveryProduct, OrderPickingProduct, \
    OrderPickingSub
from ..sales.delivery.models.delivery import OrderDeliverySerial, OrderDeliveryProductWarehouse
from ..sales.delivery.utils import DeliFinishHandler
from ..sales.equipmentloan.models import EquipmentLoan
from ..sales.equipmentreturn.models import EquipmentReturn
from ..sales.financialcashflow.models import CashInflow, CashOutflow
from ..sales.financialcashflow.utils.logical_finish_cif import CashInFlowFinishHandler
from ..sales.financialcashflow.utils.logical_finish_cof import CashOutFlowFinishHandler
from ..sales.inventory.models import (
    InventoryAdjustmentItem, GoodsReceipt, GoodsReceiptWarehouse, GoodsReturn, GoodsDetail, GoodsReceiptRequestProduct
)
from ..sales.inventory.utils import GRFinishHandler, ReturnFinishHandler
from ..sales.lead.models import Lead
from ..sales.leaseorder.models import LeaseOrder
from ..sales.leaseorder.utils.logical_finish import LOFinishHandler
from ..sales.opportunity.models import (
    Opportunity, OpportunityConfigStage, OpportunitySaleTeamMember, OpportunityMeeting, OpportunityActivityLogs,
)
from ..sales.partnercenter.models import DataObject
from ..sales.paymentplan.models import PaymentPlan
from ..sales.project.models import Project, ProjectMapMember
from ..sales.purchasing.models import (
    PurchaseRequestProduct, PurchaseOrderRequestProduct, PurchaseOrder, PurchaseRequest,
)
from ..sales.purchasing.utils import POFinishHandler, POHandler, PRHandler
from ..sales.quotation.models import QuotationIndicatorConfig, Quotation
from ..sales.quotation.serializers import QuotationListSerializer
from ..sales.report.models import ReportCashflow, ReportLease
from ..sales.report.scripts import InventoryReportRun
from ..sales.report.utils import IRForGoodsReceiptHandler
from ..sales.revenue_plan.models import RevenuePlanGroupEmployee
from ..sales.saleorder.models import SaleOrderIndicatorConfig, SaleOrder, SaleOrderIndicator, SaleOrderPaymentStage, \
    SaleOrderInvoice
from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer
from ..sales.saleorder.utils import SOFinishHandler, SOHandler
from ..sales.task.models import OpportunityTaskStatus, OpportunityTask


def make_sure_delivery_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).delivery_config()
    print('Make sure delivery config is done!')


def make_sure_workflow_apps():
    for tenant_obj in Tenant.objects.all():
        plan_ids = TenantPlan.objects.filter(tenant=tenant_obj).values_list('plan_id', flat=True)
        app_objs = [
            x.application for x in
            PlanApplication.objects.select_related('application').filter(plan_id__in=plan_ids)
        ]

        for company_obj in Company.objects.filter(tenant=tenant_obj):
            for obj in WorkflowConfigOfApp.objects.filter(application__is_workflow=False):
                print('delete Workflow Config App: ', obj.application, obj.company)
                obj.delete()

            for app in app_objs:
                if app.is_workflow is True:
                    WorkflowConfigOfApp.objects.get_or_create(
                        company=company_obj,
                        application=app,
                        defaults={
                            'tenant': tenant_obj,
                            'workflow_currently': Workflow.objects.filter(
                                tenant=tenant_obj,
                                company=company_obj,
                                application=app,
                            ).first()
                        }
                    )
    print('Make sure workflow app is successfully.')


def refill_app_code_workflow_runtime():
    for obj in Runtime.objects.all():
        if obj.app:
            obj.app_code = obj.app.app_label
            obj.save(update_fields=['app_code'])
    print('App_code was updated for runtime!')


def make_sure_quotation_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).quotation_config()
    print('Make sure quotation config is done!')


def make_sure_sale_order_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).sale_order_config()
    print('Make sure sale order config is done!')


def fill_tenant_company_to_runtime():
    print('Workflow Fill data processing:')
    for obj in RuntimeStage.objects.all():
        obj.before_save(True)
        obj.save()
    print('Stage run done!')

    for obj in RuntimeAssignee.objects.all():
        obj.before_save(True)
        obj.save()
    print('Assignee run done!')

    for obj in RuntimeLog.objects.all():
        obj.before_save(True)
        obj.save()
    print('Log run done!')


def update_quotation_sale_order_for_opportunity():
    for opp in Opportunity.objects.all():
        quotation = opp.quotation_opportunity.first()
        if quotation:
            opp.quotation = quotation
        sale_order = opp.sale_order_opportunity.first()
        if sale_order:
            opp.sale_order = sale_order
        opp.save(update_fields=['quotation', 'sale_order'])
    print("update opportunity done.")
    return True


def make_sure_opportunity_config_stage():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).opportunity_config_stage()
    print('Make sure opportunity config stage is done!')


def update_is_delete_opportunity_config_stage():
    OpportunityConfigStage.objects.exclude(
        indicator__in=['Qualification', 'Closed Won', 'Closed Lost', 'Deal Close']
    ).update(is_delete=True)

    print('Done!')


def make_sure_quotation_indicator_config():
    QuotationIndicatorConfig.objects.all().delete()
    for obj in Company.objects.all():
        ConfigDefaultData(obj).quotation_indicator_config()
    print('Make sure quotation indicator config is done!')


def make_sure_sale_order_indicator_config():
    SaleOrderIndicatorConfig.objects.all().delete()
    for obj in Company.objects.all():
        ConfigDefaultData(obj).sale_order_indicator_config()
    print('Make sure sale order indicator config is done!')


def make_sure_sync_media(re_sync=False):
    for company_obj in Company.objects.all():
        if (not company_obj.media_company_id or not company_obj.media_company_code) or re_sync:
            MediaForceAPI.call_sync_company(company_obj)
            print('Force media company: ', company_obj.media_company_id, company_obj.media_company_code)

        # refresh company obj =
        company_obj.refresh_from_db()
        if company_obj.media_company_id or company_obj.media_company_code:
            for employee_obj in Employee.objects.filter(company=company_obj):
                if not employee_obj.media_user_id or re_sync:
                    MediaForceAPI.call_sync_employee(employee_obj)
                    print('Force media employee: ', employee_obj.media_user_id, employee_obj.media_access_token)
    print('Sync media successfully')


def make_sure_task_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).task_config()
    print('Make sure Task config is done!')


def update_plan_application_quotation():
    PlanApplication.objects.filter(
        application_id="eeab5d9e-54c6-4e85-af75-477b740d7523"
    ).delete()
    Application.objects.filter(id="eeab5d9e-54c6-4e85-af75-477b740d7523").delete()
    print("update done.")
    return True


def make_full_plan():
    TenantPlan.objects.all().delete()
    plan_objs = SubscriptionPlan.objects.all()
    for tenant in Tenant.objects.all():
        for plan in plan_objs:
            TenantPlan.objects.create(tenant=tenant, plan=plan, is_limited=False)
    print('Make full plan is successfully!')


def check_employee_code_unique():
    for com_obj in Company.objects.filter():
        dict_data = {}
        for obj in Employee.objects.filter(company=com_obj):
            if obj.code in dict_data:
                dict_data[obj.code].append(obj)
            else:
                dict_data[obj.code] = [obj]

        for code, objs in dict_data.items():
            if len(objs) > 1:
                counter = 0
                for obj in objs:
                    obj.code = f'{code}-{counter}'
                    print(f'change from: {code} to {obj.code}')
                    obj.save(update_fields=['code'])
                    counter += 1
    print('Make sure code employee is successfully.')


def reset_permissions_after_remove_space_plan():
    for obj in Employee.objects.all():
        obj.permission_by_id = {}
        obj.permissions_parsed = {}
        obj.permission_by_configured = []
        obj.save()

    for obj in Role.objects.all():
        obj.permission_by_id = {}
        obj.permissions_parsed = {}
        obj.permission_by_configured = []
        obj.save()

    print('Reset permissions after remove space and plan: done!')


def update_uom_group_uom_reference():
    for uom in UnitOfMeasure.objects.filter(is_referenced_unit=True):
        uom.group.uom_reference = uom
        uom.group.save(update_fields=['uom_reference'])
    print('update done.')


def update_parent_account():
    for obj in Account.objects.all():
        old_value = obj.parent_account
        if old_value:
            obj.parent_account_mapped_id = str(old_value).replace('-', '')
            obj.save()
    return True


def update_credit_card_type():
    AccountCreditCards.objects.all().update(credit_card_type=1)
    return True


def make_sure_leave_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).leave_config(None)
        ConfigDefaultData(obj).working_calendar_config()
    print('Leave config is done!')


def update_admin_not_have_available():
    for obj in Company.objects.all():
        for employee in Employee.objects.all():
            leave_list = LeaveAvailable.objects.filter(employee_inherit=employee)
            if not leave_list.exists():
                leave_available_map_employee(employee, obj)
    print('done update')


def re_init_available():
    # delete all leave available and for loop in company, get all employee and create new available via function
    # leave_available_map_employee
    LeaveAvailable.objects.all().delete()
    for obj in Company.objects.all():
        for employee in Employee.objects.filter(company=obj):
            leave_available_map_employee(employee, obj)


def update_special_leave():
    list_leave = LeaveAvailable.objects.filter(leave_type__code__in=['FF', 'MY', 'MC'])
    for item in list_leave:
        if item.leave_type.code == 'MC':
            item.total = 1
        else:
            item.total = 3
        item.used = 0
        item.available = 0
    LeaveAvailable.objects.bulk_update(list_leave, fields=['total', 'used', 'available'])
    print('Done re-init all leave available!')


def update_quantity_remain_pr_product():
    for pr_product in PurchaseRequestProduct.objects.all():
        pr_product.remain_for_purchase_order = pr_product.quantity
        pr_product.save(update_fields=['remain_for_purchase_order'])
    print('update done.')


def new_permit_parsed():
    print('New permit parsed is starting...')
    for obj in Employee.objects.all():
        if str(obj.id) in ['9afa6107-a1f9-4d06-b855-aa60b25a70aa', 'ad2fd817-2878-40d0-b05d-4d87a0189de7']:
            obj.permission_by_configured = []
        print('Employee: ', obj.id, obj.get_full_name())
        obj.permissions_parsed = PermissionController(tenant_id=obj.tenant_id).get_permission_parsed(instance=obj)
        obj.save()

    for obj in Role.objects.all():
        if str(obj.id) in ['88caae0f-c53a-44d4-b4d8-c9d3856eca66', '54233b73-a4ee-4c2e-8729-8dd33bcaa303']:
            obj.permission_by_configured = []
        print('Role: ', obj.id, obj.title)
        obj.permissions_parsed = PermissionController(tenant_id=obj.tenant_id).get_permission_parsed(instance=obj)
        obj.save()
    print('New permit parsed is successfully!')


def convert_permit_ids():
    print('New permit IDS is starting...')
    for obj in Employee.objects.all():
        print('Employee: ', obj.id, obj.get_full_name())
        ids = obj.permission_by_id
        result = {}
        if ids and isinstance(ids, dict):
            for perm_code, data in ids.items():
                if data:
                    if isinstance(data, list):
                        result[perm_code] = {
                            id_item: {} for id_item in data
                        }
                    elif isinstance(data, dict):
                        result[perm_code] = data
        obj.permission_by_id = result
        obj.permissions_parsed = PermissionController(tenant_id=obj.tenant_id).get_permission_parsed(instance=obj)
        obj.save()

    for obj in Role.objects.all():
        print('Role: ', obj.id, obj.title)
        ids = obj.permission_by_id
        result = {}
        if ids and isinstance(ids, dict):
            for perm_code, data in ids.items():
                if data:
                    if isinstance(data, list):
                        result[perm_code] = {
                            id_item: {} for id_item in data
                        }
                    elif isinstance(data, dict):
                        result[perm_code] = data
        obj.permission_by_id = result
        obj.permissions_parsed = PermissionController(tenant_id=obj.tenant_id).get_permission_parsed(instance=obj)
        obj.save()
    print('New permit IDS is successfully!')


def make_unique_together_opp_member():
    from apps.sales.opportunity.models import Opportunity, OpportunitySaleTeamMember

    print('Destroy duplicated opp member starting...')
    list_filter = []
    for opp in Opportunity.objects.all():
        for opp_member in OpportunitySaleTeamMember.objects.filter(opportunity=opp):
            tmp = {}
            if opp_member.tenant_id:
                tmp['tenant_id'] = opp_member.tenant_id
            else:
                tmp['tenant_id__isnull'] = True

            if opp_member.company_id:
                tmp['company_id'] = opp_member.company_id
            else:
                tmp['company_id__isnull'] = True

            if opp_member.member_id:
                tmp['member_id'] = opp_member.member_id
            else:
                tmp['member_id__isnull'] = True

            list_filter.append(tmp)

    for dict_filter in list_filter:
        objs = OpportunitySaleTeamMember.objects.filter(**dict_filter)
        print(objs.count(), dict_filter)
        if objs.count() >= 2:
            for obj in objs[1:]:
                obj.delete()
    print('Destroy duplicated opp member successfully!')


def make_permission_records():
    for obj in Employee.objects.all():
        print('Employee:', obj)
        obj_permit, _created = EmployeePermission.objects.get_or_create(employee=obj)
        obj_permit.call_sync()

    for obj in Role.objects.all():
        print('Role:', obj)
        obj_permit, _created = RolePermission.objects.get_or_create(role=obj)
        obj_permit.call_sync()

    for obj in OpportunitySaleTeamMember.objects.all():
        print('Opp-Member:', obj)
        obj.permission_by_configured = []
        obj.save()

    print('Make permission records is successful.')


def update_inherit_po():
    for po in PurchaseOrder.objects.all():
        po.employee_inherit_id = po.employee_created_id if po.employee_created else None
        po.save(update_fields=['employee_inherit_id'])
    print('update_inherit_po done.')


def update_space_range_opp_member():
    for obj in OpportunitySaleTeamMember.objects.all():
        for item in obj.permission_by_configured:
            print(item)
            if 'space' in item and isinstance(item['space'], int):
                item['space'] = str(item['space'])
            if isinstance(item['range'], int):
                item['range'] = str(item['range'])
        obj.save()
    return True


def update_tenant_delivery_config():
    for deli_config in DeliveryConfig.objects.all():
        if deli_config.company:
            deli_config.tenant = deli_config.company.tenant
            deli_config.save(update_fields=['tenant'])
    print('update_tenant_delivery_config done.')


def update_ap_title_in_payment_cost():
    for item in PaymentCost.objects.all():
        new_ap_cost_converted_list = []
        for child in item.ap_cost_converted_list:
            ap_cost_filter = AdvancePaymentCost.objects.filter(id=child['ap_cost_converted_id'])
            if ap_cost_filter.exists():
                ap_title_mapped = ap_cost_filter.first().advance_payment.title
                new_ap_cost_converted_list.append({
                    'ap_cost_converted_id': child['ap_cost_converted_id'],
                    'value_converted': child['value_converted'],
                    'ap_title': ap_title_mapped
                })
        item.ap_cost_converted_list = new_ap_cost_converted_list
        item.save()
    print('done')


def make_sure_asset_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).asset_tools_config()
    print('Asset tools config is done!')


def reset_and_run_reports_sale(run_type=0):
    if run_type == 0:  # run report revenue, customer, product, lease
        ReportRevenue.objects.all().delete()
        ReportCustomer.objects.all().delete()
        ReportProduct.objects.all().delete()
        ReportLease.objects.all().delete()
        for plan in RevenuePlanGroupEmployee.objects.all():
            if plan.revenue_plan_mapped:
                ReportRevenue.push_from_plan(
                    tenant_id=plan.revenue_plan_mapped.tenant_id,
                    company_id=plan.revenue_plan_mapped.company_id,
                    employee_created_id=plan.employee_mapped_id,
                    employee_inherit_id=plan.employee_mapped_id,
                    group_inherit_id=plan.employee_mapped.group_id if plan.employee_mapped else None,
                )
        # for quotation in Quotation.objects.filter(system_status=3):
        #     QuotationFinishHandler.push_to_report_revenue(instance=quotation)
        for sale_order in SaleOrder.objects.filter(system_status=3):
            SOFinishHandler.push_to_report_revenue(instance=sale_order)
            SOFinishHandler.push_to_report_product(instance=sale_order)
            SOFinishHandler.push_to_report_customer(instance=sale_order)
        for lease_order in LeaseOrder.objects.filter(system_status=3):
            LOFinishHandler.push_to_report_lease(instance=lease_order)
        for g_return in GoodsReturn.objects.filter(system_status=3):
            ReturnFinishHandler.update_report(instance=g_return)
    if run_type == 1:  # run report cashflow
        ReportCashflow.objects.all().delete()
        for sale_order in SaleOrder.objects.filter(system_status=3):
            SOFinishHandler.push_to_report_cashflow(instance=sale_order)
        for purchase_order in PurchaseOrder.objects.filter(system_status=3):
            POFinishHandler.push_to_report_cashflow(instance=purchase_order)
    print('reset_and_run_reports_sale done.')
    return True


def reset_and_run_warehouse_stock(company_id, run_type=0):
    # input, output, provide
    if run_type == 0:  # input
        for gr in GoodsReceipt.objects.filter(system_status=3, company_id=company_id):
            GRFinishHandler.push_to_warehouse_stock(instance=gr)
    if run_type == 1:  # output
        for product_warehouse in ProductWareHouse.objects.filter(company_id=company_id):
            product_warehouse.stock_amount = product_warehouse.receipt_amount
            product_warehouse.sold_amount = 0
            product_warehouse.save(update_fields=['stock_amount', 'sold_amount'])
        for deli_sub in OrderDeliverySub.objects.filter(system_status=3, company_id=company_id):
            DeliFinishHandler.push_product_warehouse(instance=deli_sub)
    print('reset_and_run_warehouse_stock done.')
    return True


def reset_and_run_pw_lot_transaction(run_type=0):
    if run_type == 0:  # goods receipt
        ProductWareHouseLotTransaction.objects.filter(type_transaction=0).delete()
        for gr in GoodsReceipt.objects.filter(system_status=3):
            for gr_warehouse in gr.goods_receipt_warehouse_goods_receipt.all():
                if gr_warehouse.is_additional is False:  # check if not additional by Goods Detail
                    gr_product = gr_warehouse.goods_receipt_product
                    uom_base, final_ratio, lot_data, serial_data = GRFinishHandler.setup_data_push_by_po(
                        instance=gr, gr_warehouse=gr_warehouse,
                    )
                    if gr_product and lot_data:
                        product_warehouse = ProductWareHouse.objects.filter(
                            product_id=gr_product.product_id, warehouse_id=gr_warehouse.warehouse_id, uom_id=uom_base.id
                        ).first()
                        if product_warehouse:
                            for lot in lot_data:
                                pw_lot = ProductWareHouseLot.objects.filter(
                                    tenant_id=gr.tenant_id, company_id=gr.company_id,
                                    product_warehouse_id=product_warehouse.id, lot_number=lot.get('lot_number', ''),
                                ).first()
                                if pw_lot:
                                    data = {
                                        'pw_lot_id': pw_lot.id,
                                        'goods_receipt_id': gr.id,
                                        'delivery_id': None,
                                        'quantity': lot.get('quantity_import', 0),
                                        'type_transaction': 0,
                                    }
                                    ProductWareHouseLotTransaction.create(data=data)
    if run_type == 1:  # delivery
        ProductWareHouseLotTransaction.objects.filter(type_transaction=1).delete()
        for deli_product in OrderDeliveryProduct.objects.all():
            for lot in deli_product.delivery_lot_delivery_product.all():
                final_ratio = 1
                uom_delivery_rate = deli_product.uom.ratio if deli_product.uom else 1
                if lot.product_warehouse_lot:
                    product_warehouse = lot.product_warehouse_lot.product_warehouse
                    if product_warehouse:
                        uom_wh_rate = product_warehouse.uom.ratio if product_warehouse.uom else 1
                        if uom_wh_rate and uom_delivery_rate:
                            final_ratio = uom_delivery_rate / uom_wh_rate if uom_wh_rate > 0 else 1
                        data = {
                            'pw_lot_id': lot.product_warehouse_lot.id,
                            'goods_receipt_id': None,
                            'delivery_id': deli_product.delivery_sub_id,
                            'quantity': lot.quantity_delivery * final_ratio,
                            'type_transaction': 1,
                        }
                        ProductWareHouseLotTransaction.create(data=data)
    print('reset_and_run_pw_lot_transaction done.')
    return True


def update_task_config():
    OpportunityTaskStatus.objects.filter(task_kind=2, order=3).update(is_finish=True)
    print('Update Completed task status is done!')


def reset_run_customer_activity():
    AccountActivity.objects.all().delete()
    for opportunity in Opportunity.objects.all():
        if opportunity.customer:
            AccountActivity.push_activity(
                tenant_id=opportunity.tenant_id,
                company_id=opportunity.company_id,
                account_id=opportunity.customer_id,
                app_code=opportunity._meta.label_lower,
                document_id=opportunity.id,
                title=opportunity.title,
                code=opportunity.code,
                date_activity=opportunity.date_created,
                revenue=None,
            )
    for meeting in OpportunityMeeting.objects.all():
        if meeting.opportunity:
            if meeting.opportunity.customer:
                AccountActivity.push_activity(
                    tenant_id=meeting.opportunity.tenant_id,
                    company_id=meeting.opportunity.company_id,
                    account_id=meeting.opportunity.customer_id,
                    app_code=meeting._meta.label_lower,
                    document_id=meeting.id,
                    title=meeting.subject,
                    code='',
                    date_activity=meeting.meeting_date,
                    revenue=None,
                )
    for quotation in Quotation.objects.filter(system_status__in=[2, 3]):
        if quotation.customer:
            AccountActivity.push_activity(
                tenant_id=quotation.tenant_id,
                company_id=quotation.company_id,
                account_id=quotation.customer_id,
                app_code=quotation._meta.label_lower,
                document_id=quotation.id,
                title=quotation.title,
                code=quotation.code,
                date_activity=quotation.date_approved,
                revenue=quotation.indicator_revenue,
            )
    for so in SaleOrder.objects.filter(system_status__in=[2, 3]):
        if so.customer:
            AccountActivity.push_activity(
                tenant_id=so.tenant_id,
                company_id=so.company_id,
                account_id=so.customer_id,
                app_code=so._meta.label_lower,
                document_id=so.id,
                title=so.title,
                code=so.code,
                date_activity=so.date_approved,
                revenue=so.indicator_revenue,
            )
    print('reset_run_customer_activity done.')


def change_duplicate_group():
    from apps.core.hr.models import Group

    for item in Group.objects.all():
        item.code = item.code.upper()
        item.save()

    for item in Group.objects.all():
        if Group.objects.filter(company=item.company, code=item.code).exclude(id=item.id).exists():
            old_code = item.code
            item.code = item.code + '01'
            item.save()
            print('Change:', item.id, old_code, 'TO', item.code)
    print('Function run successful')


def init_folder():
    for employee in Employee.objects.all():
        Folder.objects.bulk_create([
            Folder(
                tenant_id=employee.tenant_id, company_id=employee.company_id,
                title=title, is_system=True,
                employee_inherit_id=employee.id,
            )
            for title in ["System", "Personal", "Shared with me"]
        ])
    print("init_folder done.")
    return True


def update_pw_uom_base(product):
    if product.general_uom_group:
        uom_base = product.general_uom_group.uom_reference
        if uom_base:
            for pw_base in ProductWareHouse.objects.filter(
                    product_id=product.id, uom_id=uom_base.id
            ):
                total_receipt = 0
                total_sold = 0
                for product_warehouse in ProductWareHouse.objects.filter(
                        product_id=product.id, warehouse=pw_base.warehouse_id
                ).exclude(uom_id=uom_base.id):
                    final_ratio = product_warehouse.uom.ratio / uom_base.ratio if uom_base.ratio > 0 else 1
                    total_receipt += product_warehouse.receipt_amount * final_ratio
                    total_sold += product_warehouse.sold_amount * final_ratio

                    ProductWareHouseLot.objects.filter(product_warehouse=product_warehouse).delete()
                    ProductWareHouseSerial.objects.filter(product_warehouse=product_warehouse).delete()
                    product_warehouse.delete()

                pw_base.receipt_amount += total_receipt
                pw_base.sold_amount += total_sold
                pw_base.stock_amount += total_receipt - total_sold
                pw_base.save(update_fields=['receipt_amount', 'sold_amount', 'stock_amount'])
    return True


def run_update_pw_uom_base(run_type=0, product_id=None):
    if run_type == 0:  # run all
        for product in Product.objects.all():
            update_pw_uom_base(product=product)
    if run_type == 1:  # by product_id
        product = Product.objects.filter(id=product_id).first()
        if product:
            update_pw_uom_base(product=product)
    print('run_update_pw_uom_base done.')
    return True


def delete_gr_map_wh():
    gr_wh = GoodsReceiptWarehouse.objects.filter(id="80afc5ee-f7b9-486f-a756-b66a3c642c40").first()
    if gr_wh:
        gr_wh.delete()
    print('delete_gr_map_wh done.')


def make_sure_project_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).project_config()
    print('Project config is done!')


def parse_data_json_quo_so():
    for quotation in Quotation.objects.all():
        for data in quotation.quotation_products_data:
            data.update({
                'product_id': data.get('product', {}).get('id', None),
                'product_data': data.get('product', {}),
                'promotion_id': data.get('promotion', {}).get('id', None),
                'promotion_data': data.get('promotion', {}),
                'shipping_id': data.get('shipping', {}).get('id', None),
                'shipping_data': data.get('shipping', {}),
                'unit_of_measure_id': data.get('unit_of_measure', {}).get('id', None),
                'uom_data': data.get('unit_of_measure', {}),
                'tax_id': data.get('tax', {}).get('id', None),
                'tax_data': data.get('tax', {}),
            })
        for data in quotation.quotation_costs_data:
            data.update({
                'product_id': data.get('product', {}).get('id', None),
                'product_data': data.get('product', {}),
                'shipping_id': data.get('shipping', {}).get('id', None),
                'shipping_data': data.get('shipping', {}),
                'unit_of_measure_id': data.get('unit_of_measure', {}).get('id', None),
                'uom_data': data.get('unit_of_measure', {}),
                'tax_id': data.get('tax', {}).get('id', None),
                'tax_data': data.get('tax', {}),
            })
        for data in quotation.quotation_expenses_data:
            data.update({
                'expense_id': data.get('expense', {}).get('id', None),
                'expense_data': data.get('expense', {}),
                'expense_item_id': data.get('expense_item', {}).get('id', None),
                'expense_item_data': data.get('expense_item', {}),
                'unit_of_measure_id': data.get('unit_of_measure', {}).get('id', None),
                'uom_data': data.get('unit_of_measure', {}),
                'tax_id': data.get('tax', {}).get('id', None),
                'tax_data': data.get('tax', {}),
            })
        quotation.save(update_fields=['quotation_products_data', 'quotation_costs_data', 'quotation_expenses_data'])
    for order in SaleOrder.objects.all():
        for data in order.sale_order_products_data:
            data.update({
                'product_id': data.get('product', {}).get('id', None),
                'product_data': data.get('product', {}),
                'promotion_id': data.get('promotion', {}).get('id', None),
                'promotion_data': data.get('promotion', {}),
                'shipping_id': data.get('shipping', {}).get('id', None),
                'shipping_data': data.get('shipping', {}),
                'unit_of_measure_id': data.get('unit_of_measure', {}).get('id', None),
                'uom_data': data.get('unit_of_measure', {}),
                'tax_id': data.get('tax', {}).get('id', None),
                'tax_data': data.get('tax', {}),
            })
        for data in order.sale_order_costs_data:
            data.update({
                'product_id': data.get('product', {}).get('id', None),
                'product_data': data.get('product', {}),
                'shipping_id': data.get('shipping', {}).get('id', None),
                'shipping_data': data.get('shipping', {}),
                'unit_of_measure_id': data.get('unit_of_measure', {}).get('id', None),
                'uom_data': data.get('unit_of_measure', {}),
                'tax_id': data.get('tax', {}).get('id', None),
                'tax_data': data.get('tax', {}),
            })
        for data in order.sale_order_expenses_data:
            data.update({
                'expense_id': data.get('expense', {}).get('id', None),
                'expense_data': data.get('expense', {}),
                'expense_item_id': data.get('expense_item', {}).get('id', None),
                'expense_item_data': data.get('expense_item', {}),
                'unit_of_measure_id': data.get('unit_of_measure', {}).get('id', None),
                'uom_data': data.get('unit_of_measure', {}),
                'tax_id': data.get('tax', {}).get('id', None),
                'tax_data': data.get('tax', {}),
            })
        order.save(update_fields=['sale_order_products_data', 'sale_order_costs_data', 'sale_order_expenses_data'])
    print('parse_data_json_quo_so done.')


def run_working_year():
    for year in WorkingYearConfig.objects.all():
        year.tenant = year.working_calendar.tenant
        year.company = year.working_calendar.company
        if not year.tenant:
            year.tenant = year.company.tenant
        year.save(update_fields=['tenant', 'company'])
    for holiday in WorkingHolidayConfig.objects.all():
        holiday.tenant = holiday.year.tenant
        holiday.company = holiday.year.company
        holiday.save(update_fields=['tenant', 'company'])
    print('update company is done')


def remove_wf_sys_template():
    MailTemplateSystem.objects.filter(system_code=6).delete()  # workflow
    print('remove_wf_sys_template done.')
    return True


def parse_contact_data_quo_so():
    for quotation in Quotation.objects.all():
        quotation.contact_data = {
            'id': str(quotation.contact_id),
            'fullname': quotation.contact.fullname,
            'email': quotation.contact.email,
            'mobile': quotation.contact.mobile,
            'job_title': quotation.contact.job_title,
        } if quotation.contact else {}
        quotation.save(update_fields=['contact_data'])
    for order in SaleOrder.objects.all():
        order.contact_data = {
            'id': str(order.contact_id),
            'fullname': order.contact.fullname,
            'email': order.contact.email,
            'mobile': order.contact.mobile,
            'job_title': order.contact.job_title,
        } if order.contact else {}
        order.save(update_fields=['contact_data'])
    print('parse_contact_data_quo_so done.')
    return True


def update_default_document_types():
    document_type_data = [
        {'code': 'DOCTYPE01', 'title': 'Đơn dự thầu', 'is_default': 1},
        {'code': 'DOCTYPE02', 'title': 'Tài liệu chứng minh tư cách pháp nhân', 'is_default': 1},
        {'code': 'DOCTYPE03', 'title': 'Giấy ủy quyền', 'is_default': 1},
        {'code': 'DOCTYPE04', 'title': 'Thỏa thuận liên doanh', 'is_default': 1},
        {'code': 'DOCTYPE05', 'title': 'Bảo đảm dự thầu', 'is_default': 1},
        {'code': 'DOCTYPE06', 'title': 'Tài liệu chứng minh năng lực nhà thầu', 'is_default': 1},
        {'code': 'DOCTYPE07', 'title': 'Đề xuất kĩ thuật', 'is_default': 1},
        {'code': 'DOCTYPE08', 'title': 'Đề xuất giá', 'is_default': 1},
    ]
    company_obj_list = Company.objects.all()
    bulk_data = []
    for company_obj in company_obj_list:
        if not DocumentType.objects.filter(company=company_obj, is_default=1).exists():
            for item in document_type_data:
                bulk_data.append(
                    DocumentType(
                        tenant=company_obj.tenant,
                        company=company_obj,
                        **item,
                    )
                )
    if len(bulk_data) > 0:
        DocumentType.objects.bulk_create(bulk_data)
    return True


def create_empl_map_hrm():
    avai_lst = []
    for employee in Employee.objects.all():
        obj, _created = EmployeeHRNotMapEmployeeHRM.objects.get_or_create(
            company_id=employee.company_id, employee=employee,
            defaults={
                'company_id': employee.company_id,
                'employee_id': employee.id,
                'is_mapped': False
            }
        )
        if not _created:
            avai_lst.append(obj)
    print('init create hrm data list done!')


def reset_remain_gr_for_po():
    for pr_product in PurchaseOrderRequestProduct.objects.filter(
            purchase_order_id="c9e2df0f-227d-4ee1-9b9e-6ba486724b02"
    ):
        pr_product.gr_remain_quantity = pr_product.quantity_order
        pr_product.save(update_fields=['gr_remain_quantity'])
    print("reset_remain_gr_for_po done.")
    return True


def update_flag_recurrence():
    for sale_order in SaleOrder.objects.filter(is_recurring=True):
        sale_order.is_recurrence_template = True
        sale_order.is_recurring = False
        sale_order.save(update_fields=['is_recurrence_template', 'is_recurring'])
    print('update_flag_recurrence done.')
    return True


def reset_remain_gr_for_ia():
    for ia_product in InventoryAdjustmentItem.objects.filter(
            inventory_adjustment_mapped_id__in=[
                "c16020f3-924c-4c00-9da4-55b7b9f0bd3d",
                "17d441b0-b90e-455f-85e0-9b2128889733",
                "55b92874-5a63-4dd0-9c34-6d7a55a6f163"
            ]
    ):
        difference = ia_product.count - ia_product.book_quantity
        ia_product.gr_remain_quantity = difference if difference > 0 else 0
        ia_product.save(update_fields=['gr_remain_quantity'])
    print("reset_remain_gr_for_ia done.")
    return True


def re_runtime_again(doc_id):
    runtime = Runtime.objects.filter(doc_id=doc_id).first()
    if runtime:
        if runtime.app_code:
            model_app = DisperseModel(app_model=runtime.app_code).get_model()
            if model_app and hasattr(model_app, 'objects'):
                doc_obj = model_app.objects.filter(id=doc_id).first()
                if doc_obj:
                    doc_obj.system_status = 0
                    doc_obj.code = ''
                    doc_obj.save(update_fields=['system_status', 'code'])
        runtime.delete()
    print("re_runtime_again successfully.")
    return True


def init_models_child_task_count():
    for company in Company.objects.all():
        company_task = OpportunityTask.objects.filter(company=company, tenant=company.tenant)
        for task in company_task:
            count = company_task.filter(parent_n=task).count()
            task.child_task_count = count
            task.save(update_fields=['child_task_count'])

    print('done init child task count')


def parse_quotation_data_so():
    for order in SaleOrder.objects.all():
        if order.quotation:
            quotation_data = QuotationListSerializer(order.quotation).data
            order.quotation_data = quotation_data
            order.save(update_fields=['quotation_data'])
    print('parse_quotation_data_so done.')
    return True


def update_current_document_type__doc_type_category_to_bidding():
    count = 0
    for item in DocumentType.objects.all():
        item.doc_type_category = 'bidding'
        item.save()
        count += 1
    print(f'{count} rows have been updated')


def set_system_status_doc(app_code, doc_id, system_status):
    model_target = DisperseModel(app_model=app_code).get_model()
    if model_target and hasattr(model_target, 'objects'):
        obj_target = model_target.objects.filter(id=doc_id).first()
        if obj_target:
            obj_target.system_status = system_status
            obj_target.save(update_fields=['system_status'])
    print('set_system_status_doc done.')
    return True


def remove_prop_indicator(application_id, code_list):
    objs = ApplicationProperty.objects.filter(
        application_id=application_id, code__in=code_list, is_sale_indicator=True
    )
    objs.delete()
    print("remove_prop_indicator done.")
    return True


def create_data_object():
    try:
        account = DataObject.objects.create(title='Account', application_id='4e48c863861b475aaa5e97a4ed26f294')
        print(
            f'{account.title} data object created'
        )
        contact = DataObject.objects.create(title='Contact', application_id='828b785a8f574a039f90e0edf96560d7')
        print(
            f'{contact.title} data object created'
        )
    except Exception as e:
        print(e)


def update_check_lock_date_project():
    for prj in Project.objects.all():
        lst_emp = [str(prj.employee_inherit.id)]
        if hasattr(prj.project_pm, 'id'):
            lst_emp.append(str(prj.project_pm.id))
        for item in ProjectMapMember.objects.filter(
                tenant=prj.tenant, company=prj.company,
                project=prj, member_id__in=lst_emp
        ):
            item.permit_lock_fd = True
            item.save(update_fields=['permit_lock_fd'])
    print('done update lock finish date')


def update_employee_for_promotion():
    for company in Company.objects.all():
        admin = Employee.objects.filter(company=company, is_admin_company=True).first()
        Promotion.objects.filter(company=company).update(
            employee_inherit=admin, employee_created=admin, employee_modified=admin
        )
    print('Done update_employee_for_promotion !!')


def change_field_doc_id_to_lead_id_in_lead():
    lead_instance_list = Lead.objects.all().values_list('id', flat=True)
    activity_logs = OpportunityActivityLogs.objects.all()
    count = 0
    for activity_log in activity_logs:
        if activity_log.doc_id in lead_instance_list:
            activity_log.lead_id = activity_log.doc_id
            activity_log.doc_id = None
            activity_log.save(update_fields=['lead_id', 'doc_id'])
            count += 1
    print(
        f'{count} rows updated'
    )


def create_default_masterdata_fixed_asset():
    Fixed_Asset_Group_data = [
        {'code': 'FACG001', 'title': 'Tài sản cố định hữu hình', 'is_default': 1},
        {'code': 'FACG002', 'title': 'Tài sản cố định vô hình', 'is_default': 1},
        {'code': 'FACG003', 'title': 'Tài sản cố định thuê tài chính', 'is_default': 1}
    ]
    Fixed_Asset_data = [
        {'code': 'FAC001', 'title': 'Nhà cửa, vật kiến trúc - quản lý', 'is_default': 1},
        {'code': 'FAC002', 'title': 'Máy móc thiết bị - sản xuất', 'is_default': 1},
        {'code': 'FAC003', 'title': 'Phương tiện vận tải, truyền dẫn - kinh doanh', 'is_default': 1},
        {'code': 'FAC004', 'title': 'Quyền sử dụng đất', 'is_default': 1},
        {'code': 'FAC005', 'title': 'Quyền phát hành', 'is_default': 1},
        {'code': 'FAC006', 'title': 'Bản quyền, bằng sáng chế', 'is_default': 1},
        {'code': 'FAC007', 'title': 'TSCD hữu hình thuê tài chính', 'is_default': 1},
        {'code': 'FAC008', 'title': 'TSCD vô hình thuê tài chính', 'is_default': 1},
    ]
    count = 0
    print('Loading')
    for company in Company.objects.all():
        try:
            # tai san co dinh huu hinh
            tangible_fixed_asset_group_instance = FixedAssetClassificationGroup.objects.create(
                tenant=company.tenant,
                company=company,
                **Fixed_Asset_Group_data[0]
            )

            # tai san co dinh vo hinh
            intangible_fixed_asset_group_instance = FixedAssetClassificationGroup.objects.create(
                tenant=company.tenant,
                company=company,
                **Fixed_Asset_Group_data[1]
            )

            # tai san co dinh thue tai chinh
            finance_leasing_fixed_asset_group_instance = FixedAssetClassificationGroup.objects.create(
                tenant=company.tenant,
                company=company,
                **Fixed_Asset_Group_data[2]
            )

            # create asset classification
            for index, data in enumerate(Fixed_Asset_data):
                if index < 3:
                    # First 3 items belong to tangible_fixed_asset_group_instance
                    group_instance = tangible_fixed_asset_group_instance
                elif index < 6:
                    # Next 3 items belong to intangible_fixed_asset_group_instance
                    group_instance = intangible_fixed_asset_group_instance
                else:
                    # Last 2 items belong to finance_leasing_fixed_asset_group_instance
                    group_instance = finance_leasing_fixed_asset_group_instance

                # Create FixedAssetClassification instance
                FixedAssetClassification.objects.create(
                    tenant=company.tenant,
                    company=company,
                    group=group_instance,  # Assign the group
                    **data
                )
            count += 1
        except Exception as err:
            print(
                '[ERROR]',
                str(company.id), str(err)
            )
    print('Done')


def update_consulting_document_type():
    Consulting_Document_Type_data = [
        {'code': 'DOCTYPE09', 'title': 'Tài liệu xác định yêu cầu', 'is_default': 0, 'doc_type_category': 'consulting'},
        {'code': 'DOCTYPE10', 'title': 'Tài liệu giới thiệu sản phẩm', 'is_default': 0,
         'doc_type_category': 'consulting'},
        {'code': 'DOCTYPE11', 'title': 'Thuyết minh kĩ thuật', 'is_default': 0, 'doc_type_category': 'consulting'},
        {'code': 'DOCTYPE12', 'title': 'Tài liệu đề xuất giải pháp', 'is_default': 0,
         'doc_type_category': 'consulting'},
        {'code': 'DOCTYPE13', 'title': 'BOM', 'is_default': 0, 'doc_type_category': 'consulting'},
        {'code': 'DOCTYPE14', 'title': 'Giới thiệu dịch vụ hỗ trợ vận hành', 'is_default': 0,
         'doc_type_category': 'consulting'},
        {'code': 'DOCTYPE15', 'title': 'Thuyết trình phạm vi dự án', 'is_default': 0,
         'doc_type_category': 'consulting'},
    ]
    company_count = 0
    company_obj_list = Company.objects.all()
    bulk_data = []
    for company_obj in company_obj_list:
        company_count += 1
        for item in Consulting_Document_Type_data:
            bulk_data.append(
                DocumentType(
                    tenant=company_obj.tenant,
                    company=company_obj,
                    **item,
                )
            )
    if len(bulk_data) > 0:
        DocumentType.objects.bulk_create(bulk_data)
    print(f'{company_count} companies updated')


class SubScripts:
    """ Haind's scripts """

    @staticmethod
    def update_period_cfg_for_all_company():
        """ Đẩy cấu hình về QL tồn kho & cấu hình kế toán của công ty vào năm tài chính """
        for company in Company.objects.all():
            company_cfg = company.company_config
            if company_cfg:
                for period in Periods.objects.filter(company=company):
                    period.definition_inventory_valuation = company_cfg.definition_inventory_valuation
                    period.default_inventory_value_method = company_cfg.default_inventory_value_method
                    period.cost_per_warehouse = company_cfg.cost_per_warehouse
                    period.cost_per_lot = company_cfg.cost_per_lot
                    period.cost_per_project = company_cfg.cost_per_project
                    period.accounting_policies = company_cfg.accounting_policies
                    period.applicable_circular = company_cfg.applicable_circular
                    period.save(update_fields=[
                        'definition_inventory_valuation',
                        'default_inventory_value_method',
                        'cost_per_warehouse',
                        'cost_per_lot',
                        'cost_per_project',
                        'accounting_policies',
                        'applicable_circular',
                    ])
        print('Done :))')
        return True

    @staticmethod
    def update_opp_stage_is_delete_is_default():
        """ Cập nhập các trạng thái OPP thành mặc định """
        OpportunityConfigStage.objects.filter(is_default=True).update(is_delete=False)
        print('Done :))')
        return True

    @staticmethod
    def update_product_type_tool_import():
        """ Cập nhập Product Type Công Cụ Dụng Cụ + Import Group """
        ProductType.objects.filter(code='asset_tool', is_default=1).update(code='tool', is_tool=1)
        ProductType.objects.filter(code='tool', is_default=1, is_tool=1).update(title='Công cụ - Dụng cụ')
        UnitOfMeasureGroup.objects.filter(code='ImportGroup', is_default=1).update(code='Import')
        print('Done :))')
        return True

    @classmethod
    def run_all(cls):
        cls.update_period_cfg_for_all_company()
        cls.update_opp_stage_is_delete_is_default()
        cls.update_product_type_tool_import()
        return True

    @classmethod
    def create_data_json_for_ar_invoice(cls):
        for ar_invoice_obj in ARInvoice.objects.all():
            customer_mapped = ar_invoice_obj.customer_mapped
            billing_address = customer_mapped.account_mapped_billing_address.all()
            bank_account = customer_mapped.account_banks_mapped.all()
            ar_invoice_obj.customer_mapped_data = {
                'id': str(customer_mapped.id),
                'code': customer_mapped.code,
                'name': customer_mapped.name,
                'tax_code': customer_mapped.tax_code,
                'billing_address_id': str(billing_address.first().id) if billing_address.count() > 0 else '',
                'bank_account_id': str(bank_account.first().id) if bank_account.count() > 0 else '',
            } if customer_mapped else {}
            sale_order_mapped = ar_invoice_obj.sale_order_mapped
            ar_invoice_obj.sale_order_mapped_data = {
                'id': str(sale_order_mapped.id),
                'code': sale_order_mapped.code,
                'title': sale_order_mapped.title,
                'sale_order_payment_stage': sale_order_mapped.sale_order_payment_stage
            } if sale_order_mapped else {}
            ar_invoice_obj.save(update_fields=['customer_mapped_data', 'sale_order_mapped_data'])
        for item in ARInvoiceItems.objects.all():
            product_obj = item.product
            item.product_data = {
                'id': str(product_obj.id),
                'code': product_obj.code,
                'title': product_obj.title,
                'des': product_obj.description,
            } if product_obj else {}
            uom_obj = item.product_uom
            item.product_uom_data = {
                'id': str(uom_obj.id),
                'code': uom_obj.code,
                'title': uom_obj.title,
                'group_id': str(uom_obj.group_id)
            } if uom_obj else {}
            tax_obj = item.product_tax
            item.product_tax_data = {
                'id': str(tax_obj.id),
                'code': tax_obj.code,
                'title': tax_obj.title,
                'rate': tax_obj.rate,
            } if tax_obj else {}
            item.save(update_fields=['product_data', 'product_uom_data', 'product_tax_data'])
        for item in ARInvoiceDelivery.objects.all():
            delivery_obj = item.delivery_mapped
            item.delivery_mapped_data = {
                'id': str(delivery_obj.id),
                'code': delivery_obj.code
            } if delivery_obj else {}
            item.save(update_fields=['delivery_mapped_data'])
        print('Done :))')
        return True

    @classmethod
    def update_opp_stage_title(cls):
        for item in OpportunityConfigStage.objects.all():
            for data in item.condition_datas:
                if data['condition_property']['title'] == 'SaleOrder Status':
                    data['condition_property']['title'] = 'Order Status'
                elif data['condition_property']['title'] == 'SaleOrder Delivery Status':
                    data['condition_property']['title'] = 'Order Delivery Status'
            item.save(update_fields=['condition_datas'])
        print('Done :))')
        return True

    @classmethod
    def update_order_delivery_has_ar_invoice_already(cls):
        for obj in OrderDeliverySub.objects.all():
            obj.has_ar_invoice_already = ARInvoiceDelivery.objects.filter(
                ar_invoice__system_status=3,
                delivery_mapped=obj
            ).exists()
            obj.save(update_fields=['has_ar_invoice_already'], **{'skip_check_period': True})
        print('Done :))')
        return True

    @classmethod
    def update_master_data_multi_reference(cls, tenant_code):
        for company_obj in Company.objects.filter(tenant__code=tenant_code):
            tenant_obj = company_obj.tenant
            UnitOfMeasureGroup.objects.filter(tenant=tenant_obj, company=company_obj).delete()
            UnitOfMeasure.objects.filter(tenant=tenant_obj, company=company_obj).delete()

            UoM_Group_data = [
                {'code': 'ImportGroup', 'title': 'Nhóm đơn vị cho import', 'is_default': 1},
                {'code': 'Labor', 'title': 'Nhân công', 'is_default': 1},
                {'code': 'Size', 'title': 'Kích thước', 'is_default': 1},
                {'code': 'Time', 'title': 'Thời gian', 'is_default': 1},
                {'code': 'Unit', 'title': 'Đơn vị', 'is_default': 1},
            ]
            objs = [
                UnitOfMeasureGroup(tenant=tenant_obj, company=company_obj, **uom_group_item)
                for uom_group_item in UoM_Group_data
            ]
            UnitOfMeasureGroup.objects.bulk_create(objs)

            unit_group = UnitOfMeasureGroup.objects.filter(
                tenant=tenant_obj, company=company_obj, code='Unit', is_default=1
            ).first()
            if unit_group:
                referenced_unit_obj = UnitOfMeasure.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    code='UOM001',
                    title='Cái',
                    is_referenced_unit=1,
                    ratio=1,
                    rounding=4,
                    is_default=1,
                    group=unit_group
                )
                UnitOfMeasure.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    code='UOM002',
                    title='Con',
                    is_referenced_unit=0,
                    ratio=1,
                    rounding=4,
                    is_default=1,
                    group=unit_group
                )
                UnitOfMeasure.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    code='UOM003',
                    title='Thanh',
                    is_referenced_unit=0,
                    ratio=1,
                    rounding=4,
                    is_default=1,
                    group=unit_group
                )
                UnitOfMeasure.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    code='UOM004',
                    title='Lần',
                    is_referenced_unit=0,
                    ratio=1,
                    rounding=4,
                    is_default=1,
                    group=unit_group
                )
                UnitOfMeasure.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    code='UOM005',
                    title='Gói',
                    is_referenced_unit=0,
                    ratio=1,
                    rounding=4,
                    is_default=1,
                    group=unit_group
                )
                unit_group.uom_reference = referenced_unit_obj
                unit_group.save(update_fields=['uom_reference'])

            # add default uom for group time
            labor_group = UnitOfMeasureGroup.objects.filter(
                tenant=tenant_obj, company=company_obj, code='Labor', is_default=1
            ).first()
            if labor_group:
                referenced_unit_obj = UnitOfMeasure.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    code='Manhour',
                    title='Manhour',
                    is_referenced_unit=1,
                    ratio=1,
                    rounding=4,
                    is_default=1,
                    group=labor_group
                )
                UnitOfMeasure.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    code='Manday',
                    title='Manday',
                    is_referenced_unit=0,
                    ratio=8,
                    rounding=4,
                    is_default=1,
                    group=labor_group
                )
                UnitOfMeasure.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    code='Manmonth',
                    title='Manmonth',
                    is_referenced_unit=0,
                    ratio=176,
                    rounding=4,
                    is_default=1,
                    group=labor_group
                )
                labor_group.uom_reference = referenced_unit_obj
                labor_group.save(update_fields=['uom_reference'])
        print('Done :))')
        return True

    @classmethod
    def update_currency_default(cls):
        for company in Company.objects.all():
            print(company.title)
            Currency.objects.filter(
                company=company, abbreviation__in=['VND', 'USD', 'EUR', 'JPY']
            ).update(is_default=True)
        print('Done :))')
        return True

    @classmethod
    def update_currency_in_period(cls):
        for period in Periods.objects.all():
            print(period.company.title)
            vnd = Currency.objects.get(company=period.company, abbreviation='VND')
            period.currency_mapped = vnd
            period.save(update_fields=['currency_mapped'])
            period.company.company_config.master_data_currency = vnd
            period.company.company_config.currency = vnd.currency
            period.company.company_config.save(update_fields=['master_data_currency', 'currency'])
        print('Done :))')
        return True

    @classmethod
    def force_update_primary_currency(cls, company_id, abbreviation='VND'):
        """ Hàm hỗ trợ cập nhập primary_currency (khi đã kiểm tra dữ liệu) """
        company_obj = Company.objects.get(id=company_id)
        primary_currency_obj = Currency.objects.get(company=company_obj, abbreviation=abbreviation)

        company_obj.company_config.master_data_currency = primary_currency_obj
        company_obj.company_config.currency = primary_currency_obj.currency
        company_obj.company_config.save(update_fields=['master_data_currency', 'currency'])

        Currency.objects.filter(company=company_obj).exclude(abbreviation=primary_currency_obj.abbreviation).update(
            is_primary=False, rate=None
        )
        Currency.objects.filter(company=company_obj, abbreviation=primary_currency_obj.abbreviation).update(
            is_primary=True, rate=1
        )

        this_period = Periods.get_current_period(company_obj.tenant_id, company_obj.id)
        if this_period:
            this_period.currency_mapped = primary_currency_obj
            this_period.save(update_fields=['currency_mapped'])
        print('Done :))')
        return True

    @classmethod
    def update_print_field_for_sale_cashoutflow(cls):
        for ap in AdvancePayment.objects.all():
            advance_value_before_tax = 0
            advance_value_tax = 0
            advance_value = 0
            for item in ap.advance_payment.all():
                advance_value_before_tax += item.expense_subtotal_price
                advance_value_tax += item.expense_tax_price
                advance_value += item.expense_after_tax_price
            ap.advance_value_before_tax = advance_value_before_tax
            ap.advance_value_tax = advance_value_tax
            ap.advance_value = advance_value
            ap.save(update_fields=[
                'advance_value_before_tax',
                'advance_value_tax',
                'advance_value'
            ])
        for payment in Payment.objects.all():
            payment_value_before_tax = 0
            payment_value_tax = 0
            payment_value = 0
            for item in payment.payment.all():
                payment_value_before_tax += item.expense_subtotal_price
                payment_value_tax += item.expense_tax_price
                payment_value += item.expense_after_tax_price
            payment.payment_value_before_tax = payment_value_before_tax
            payment.payment_value_tax = payment_value_tax
            payment.payment_value = payment_value
            payment.save(update_fields=[
                'payment_value_before_tax',
                'payment_value_tax',
                'payment_value'
            ])
        print('Done :))')
        return True

    @classmethod
    def update_des_for_cashoutflow(cls):
        for item in AdvancePaymentCost.objects.all():
            item.expense_description = item.expense_name
            item.save(update_fields=['expense_description'])
        for item in ReturnAdvanceCost.objects.all():
            item.expense_description = item.expense_name
            item.save(update_fields=['expense_description'])
        print('Done :))')
        return True

    @classmethod
    def update_company_config_json_data(cls):
        for company_obj in Company.objects.all():
            print(company_obj.title)
            function_number_data = []
            for item in company_obj.company_function_number.all():
                function_number_data.append({
                    'app_type': item.app_type,
                    'app_code': item.app_code,
                    'app_title': item.app_title,
                    'schema_text': item.schema_text,
                    'schema': item.schema,
                    'first_number': item.first_number,
                    'last_number': item.last_number,
                    'reset_frequency': item.reset_frequency,
                    'min_number_char': item.min_number_char
                })
            company_obj.function_number_data = function_number_data
            company_obj.save(update_fields=['function_number_data'])
        print('Done :))')
        return True

    @classmethod
    def update_account_contacts_m2m(cls):
        bulk_info = []
        for account in Account.objects.all():
            for contact in Contact.objects.filter(account_name=account):
                is_account_owner = str(account.owner_id) == str(contact.id)
                bulk_info.append(
                    AccountContacts(account=account, contact=contact, is_owner=is_account_owner)
                )
        AccountContacts.objects.all().delete()
        AccountContacts.objects.bulk_create(bulk_info)
        print('Done :))')
        return True


def reset_run_indicator_fields(kwargs):
    for sale_order in SaleOrder.objects.filter(**kwargs):
        for so_indicator in SaleOrderIndicator.objects.filter(
                sale_order=sale_order, quotation_indicator__code__in=["IN0001", "IN0003", "IN0006"]
        ):
            if so_indicator.quotation_indicator.code == "IN0001":
                sale_order.indicator_revenue = so_indicator.indicator_value
            if so_indicator.quotation_indicator.code == "IN0003":
                sale_order.indicator_gross_profit = so_indicator.indicator_value
            if so_indicator.quotation_indicator.code == "IN0006":
                sale_order.indicator_net_income = so_indicator.indicator_value
        sale_order.save(update_fields=['indicator_revenue', 'indicator_gross_profit', 'indicator_net_income'])
    print('reset_run_indicator_fields done.')


def update_product_warehouse_serial_status(product_id, warehouse_id, serial_number, serial_status):
    pw_serial = ProductWareHouseSerial.objects.filter_on_company(
        product_warehouse__product_id=product_id,
        product_warehouse__warehouse_id=warehouse_id,
        serial_number=serial_number,
    ).first()
    if pw_serial:
        pw_serial.serial_status = serial_status
        pw_serial.save(update_fields=['serial_status'])
    print('update_product_warehouse_serial_status done.')


class DefaultSaleDataHandler:
    Salutation_data = [
        {'code': 'SA001', 'title': 'Anh', 'is_default': 1},
        {'code': 'SA002', 'title': 'Chị', 'is_default': 1},
        {'code': 'SA003', 'title': 'Ông', 'is_default': 1},
        {'code': 'SA004', 'title': 'Bà', 'is_default': 1}
    ]
    Account_groups_data = [
        {'code': 'AG001', 'title': 'Khách lẻ', 'is_default': 1},
        {'code': 'AG002', 'title': 'VIP1', 'is_default': 1},
        {'code': 'AG003', 'title': 'VIP2', 'is_default': 1},
    ]
    Industries_data = [
        {'code': 'IN001', 'title': 'Dịch vụ', 'is_default': 1},
        {'code': 'IN002', 'title': 'Sản xuất', 'is_default': 1},
        {'code': 'IN003', 'title': 'Phân phối', 'is_default': 1},
        {'code': 'IN004', 'title': 'Bán lẻ', 'is_default': 1},
        {'code': 'IN005', 'title': 'Giáo dục', 'is_default': 1},
        {'code': 'IN006', 'title': 'Y tế', 'is_default': 1},
    ]
    UOM_data = [
        {'code': 'UOM001', 'title': 'Cái', 'is_referenced_unit': 1, 'is_default': 1},
        {'code': 'UOM002', 'title': 'Con', 'is_default': 1},
        {'code': 'UOM003', 'title': 'Thanh', 'is_default': 1},
        {'code': 'UOM004', 'title': 'Lần', 'is_default': 1},
        {'code': 'UOM005', 'title': 'Gói', 'is_default': 1},
    ]
    Tax_data = [
        {'code': 'VAT_KCT', 'title': 'VAT-KCT', 'tax_type': 2, 'rate': 0, 'is_default': 1},
        {'code': 'VAT_0', 'title': 'VAT-0', 'tax_type': 2, 'rate': 0, 'is_default': 1},
        {'code': 'VAT_5', 'title': 'VAT-5', 'tax_type': 2, 'rate': 5, 'is_default': 1},
        {'code': 'VAT_8', 'title': 'VAT-8', 'tax_type': 2, 'rate': 8, 'is_default': 1},
        {'code': 'VAT_10', 'title': 'VAT-10', 'tax_type': 2, 'rate': 10, 'is_default': 1},
    ]

    def __init__(self):
        company_list = Company.objects.all()
        self.company_list = company_list

    def create_default_master_data(self):
        import logging
        from django.db import transaction
        logger = logging.getLogger(__name__)

        try:
            with transaction.atomic():
                self.create_salutation()
                self.create_account_groups()
                self.create_industry()
                self.create_uom()
                self.create_tax()
            return True
        except Exception as err:
            logger.error('Error create default data', err)
        return False

    def create_salutation(self):
        for company_obj in self.company_list:
            objs = []
            for item in self.Salutation_data:
                if not Salutation.objects.filter(
                        tenant=company_obj.tenant,
                        company=company_obj,
                        code=item['code']
                ).exists():
                    objs.append(Salutation(tenant=company_obj.tenant, company=company_obj, **item))

            if objs:
                Salutation.objects.bulk_create(objs)
            print(f'Default salutation created for company {company_obj.title}')
        print('Create default salutation finished')

    def create_account_groups(self):
        for company_obj in self.company_list:
            objs = []
            for item in self.Account_groups_data:
                if not AccountGroup.objects.filter(
                        tenant=company_obj.tenant,
                        company=company_obj,
                        code=item['code']
                ).exists():
                    objs.append(AccountGroup(tenant=company_obj.tenant, company=company_obj, **item))

            if objs:
                AccountGroup.objects.bulk_create(objs)
            print(f'Default account group created for company {company_obj.title}')
        print('Create default account group finished')

    def create_industry(self):
        for company_obj in self.company_list:
            objs = []
            for item in self.Industries_data:
                if not Industry.objects.filter(
                        tenant=company_obj.tenant,
                        company=company_obj,
                        code=item['code']
                ).exists():
                    objs.append(Industry(tenant=company_obj.tenant, company=company_obj, **item))

            if objs:
                Industry.objects.bulk_create(objs)
            print(f'Default industry created for company {company_obj.title}')
        print('Create default industry finished')

    def create_uom(self):
        for company_obj in self.company_list:
            unit_uom_group = UnitOfMeasureGroup.objects.filter(
                tenant=company_obj.tenant,
                company=company_obj,
                code='Unit'
            ).first()
            if unit_uom_group:
                objs = []
                for item in self.UOM_data:
                    if not UnitOfMeasure.objects.filter(
                            tenant=company_obj.tenant,
                            company=company_obj,
                            code=item['code']
                    ).exists():
                        objs.append(
                            UnitOfMeasure(
                                tenant=company_obj.tenant,
                                company=company_obj,
                                group=unit_uom_group,
                                **item
                            )
                        )

                if objs:
                    UnitOfMeasure.objects.bulk_create(objs)
                print(f'Default uom created for company {company_obj.title}')
        print('Create default uom finished')

    def create_tax(self):
        for company_obj in self.company_list:
            vat_tax_category = TaxCategory.objects.filter(
                tenant=company_obj.tenant,
                company=company_obj,
                code='TC001'
            ).first()
            if vat_tax_category:
                objs = []
                for item in self.Tax_data:
                    if not Tax.objects.filter(
                            tenant=company_obj.tenant,
                            company=company_obj,
                            code=item['code']
                    ).exists():
                        objs.append(
                            Tax(tenant=company_obj.tenant, company=company_obj, category=vat_tax_category, **item))

                if objs:
                    Tax.objects.bulk_create(objs)
                print(f'Default tax created for company {company_obj.title}')
        print('Create default tax finished')

    def update_code_document_type(self):
        code_mapping = {
            "DOCTYPE01": "BDT001",
            "DOCTYPE02": "BDT002",
            "DOCTYPE03": "BDT003",
            "DOCTYPE04": "BDT004",
            "DOCTYPE05": "BDT005",
            "DOCTYPE06": "BDT006",
            "DOCTYPE07": "BDT007",
            "DOCTYPE08": "BDT008",
            "DOCTYPE09": "CDT001",
            "DOCTYPE10": "CDT002",
            "DOCTYPE11": "CDT003",
            "DOCTYPE12": "CDT004",
            "DOCTYPE13": "CDT005",
            "DOCTYPE14": "CDT006",
            "DOCTYPE15": "CDT007",
        }

        document_types = DocumentType.objects.filter(code__in=code_mapping.keys())

        updated_objects = []
        for doc in document_types:
            if doc.code in code_mapping:
                doc.code = code_mapping[doc.code]
                updated_objects.append(doc)

        if updated_objects:
            DocumentType.objects.bulk_update(updated_objects, ["code"])

        print('Document type code updated')


def make_sure_lease_order_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).lease_order_config()
    print('Make sure lease order config is done!')


def update_bid_doctype_for_HongQuang():
    Document_Type_data = [
        {'code': 'BDT001', 'title': 'Đơn dự thầu', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT002', 'title': 'Tài liệu chứng minh tư cách pháp nhân', 'is_default': 1,
         'doc_type_category': 'bidding'},
        {'code': 'BDT003', 'title': 'Giấy ủy quyền', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT004', 'title': 'Thỏa thuận liên doanh', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT005', 'title': 'Bảo đảm dự thầu', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT006', 'title': 'Tài liệu chứng minh năng lực nhà thầu', 'is_default': 1,
         'doc_type_category': 'bidding'},
        {'code': 'BDT007', 'title': 'Đề xuất kĩ thuật', 'is_default': 1, 'doc_type_category': 'bidding'},
        {'code': 'BDT008', 'title': 'Đề xuất giá', 'is_default': 1, 'doc_type_category': 'bidding'}
    ]

    company_obj_list = Company.objects.all()

    for company_obj in company_obj_list:
        if not DocumentType.objects.filter(company=company_obj, tenant=company_obj.tenant, code='BDT001').exists():
            objs = [
                DocumentType(tenant=company_obj.tenant, company=company_obj, **item)
                for item in Document_Type_data
            ]
            DocumentType.objects.bulk_create(objs)
            print(f'Bidding default document type created for {company_obj.title}')


def delete_non_default_account_type():
    # KO cho tạo mới account type nữa
    company_obj_list = Company.objects.all()
    for company_obj in company_obj_list:
        # delete all account type with is_default=False
        non_default_account_type_list = AccountType.objects.filter(company=company_obj, tenant=company_obj.tenant,
                                                                   is_default=False)
        non_default_account_type_list.delete()
        print(f'Non-default account type deleted for {company_obj.title}')


def update_product_warehouse_picked_ready(product_id=None, warehouse_id=None):
    picked = 0
    delivered = 0
    for picked_obj in OrderPickingProduct.objects.filter_on_company(product_id=product_id):
        picked += picked_obj.picked_quantity
    for delivered_obj in OrderDeliveryProduct.objects.filter_on_company(product_id=product_id):
        delivered += delivered_obj.picked_quantity
    product_warehouse = ProductWareHouse.objects.filter_on_company(
        product_id=product_id, warehouse_id=warehouse_id
    ).first()
    if product_warehouse:
        product_warehouse.picked_ready = picked - delivered
        product_warehouse.save(update_fields=['picked_ready'])
    print('update_product_warehouse_picked_ready done.')


def add_delivery_pw_serial(sub_product_id=None, pw_serial_id=None):
    sub_product = OrderDeliveryProduct.objects.filter_on_company(id=sub_product_id).first()
    pw_serial = ProductWareHouseSerial.objects.filter_on_company(id=pw_serial_id).first()
    if sub_product and pw_serial:
        sub_product.delivery_data = [
            {
                "id": "b473c7aa-9a34-4190-a222-2b62f23cd09f",
                "uom": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "ratio": 1,
                    "title": "Cái"
                },
                "stock": 0,
                "uom_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product": {
                    "id": "28b33b97-33ba-421f-bb95-799bc7b36692",
                    "code": "SP001",
                    "title": "Server Super Micro 1111",
                    "general_traceability_method": 2
                },
                "lot_data": [

                ],
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "ratio": 1,
                    "title": "Cái"
                },
                "uom_stock": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "ratio": 1,
                    "title": "Cái"
                },
                "warehouse": {
                    "id": "15bbe829-5c82-4284-a0f7-2332a2a8826b",
                    "code": "W0001",
                    "title": "Kho hàng cho thuê"
                },
                "product_id": "28b33b97-33ba-421f-bb95-799bc7b36692",
                "is_regis_so": False,
                "serial_data": [
                    {
                        "product_warehouse_serial_id": "2d2e3296-c383-4027-984b-47818950b892",
                        "product_warehouse_serial_data": {
                            "id": "2d2e3296-c383-4027-984b-47818950b892",
                            "is_delete": False,
                            "expire_date": None,
                            "warranty_end": None,
                            "serial_number": "SPR005",
                            "warranty_start": None,
                            "manufacture_date": None,
                            "product_warehouse": {
                                "id": "b473c7aa-9a34-4190-a222-2b62f23cd09f",
                                "product": {
                                    "id": "28b33b97-33ba-421f-bb95-799bc7b36692",
                                    "code": "SP001",
                                    "title": "Server Super Micro 1111"
                                },
                                "warehouse": {
                                    "id": "15bbe829-5c82-4284-a0f7-2332a2a8826b",
                                    "code": "W0001",
                                    "title": "Kho hàng cho thuê"
                                }
                            },
                            "vendor_serial_number": None
                        }
                    }
                ],
                "sold_amount": 2,
                "picked_ready": 0,
                "product_data": {
                    "id": "28b33b97-33ba-421f-bb95-799bc7b36692",
                    "code": "SP001",
                    "title": "Server Super Micro 1111",
                    "general_traceability_method": 2
                },
                "stock_amount": 8,
                "uom_delivery": {
                    "id": "b6860398-0be3-4992-8dc2-18bf5b7fbbbb",
                    "code": "UOM002",
                    "ratio": 1,
                    "title": "Con",
                    "rounding": 4,
                    "is_referenced_unit": False
                },
                "warehouse_id": "15bbe829-5c82-4284-a0f7-2332a2a8826b",
                "receipt_amount": 10,
                "warehouse_data": {
                    "id": "15bbe829-5c82-4284-a0f7-2332a2a8826b",
                    "code": "W0001",
                    "title": "Kho hàng cho thuê"
                },
                "available_stock": 8,
                "picked_quantity": 1,
                "available_picked": 0,
                "lease_order_data": {
                    "id": "eadfa541-fbd1-4d26-81ef-3d5be2f991e6",
                    "code": "LO0009",
                    "title": "THUÊ SERVER",
                    "opportunity": {

                    }
                }
            }
        ]
        sub_product.save(update_fields=['delivery_data'])
        pw_serial.serial_status = 1
        pw_serial.save(update_fields=['serial_status'])
    print('add_delivery_pw_serial done.')


def create_new_tenant(tenant_code, tenant_data, user_data):
    TenantController().setup_new(
        tenant_code=tenant_code,
        tenant_data=tenant_data,
        user_data=user_data,
        create_company=True,
        create_employee=True,
        plan_data=[
            {"title": "HRM", "code": "hrm", "quantity": 50, "date_active": "2024-01-02 03:46:00",
             "date_end": "2025-01-02 03:46:00", "is_limited": False, "purchase_order": "PO-001"},
            {"title": "Personal", "code": "personal", "quantity": None, "date_active": "2024-01-02 03:46:00",
             "date_end": "2025-01-02 03:46:00", "is_limited": False, "purchase_order": "PO-001"},
            {"title": "Sale", "code": "sale", "quantity": 50, "date_active": "2024-01-02 03:46:00",
             "date_end": "2025-01-02 03:46:00", "is_limited": True, "purchase_order": "PO-001"},
            {"title": "E-Office", "code": "e-office", "quantity": 50, "date_active": "2024-01-02 03:46:00",
             "date_end": "2025-01-02 03:46:00", "is_limited": True, "purchase_order": "PO-001"}]
    )
    print('create_new_tenant done.')
    return True


def reset_push_payment_plan():
    PaymentPlan.objects.all().delete()
    for sale_order in SaleOrder.objects.filter(system_status=3):
        SOFinishHandler.push_to_payment_plan(instance=sale_order)
    for purchase_order in PurchaseOrder.objects.filter(system_status=3):
        POFinishHandler.push_to_payment_plan(instance=purchase_order)
    for cash_in_flow in CashInflow.objects.filter(system_status=3):
        CashInFlowFinishHandler.push_to_payment_plan(instance=cash_in_flow)
    for cash_out_flow in CashOutflow.objects.filter(system_status=3):
        CashOutFlowFinishHandler.push_to_payment_plan(instance=cash_out_flow)
    print('reset_push_payment_plan done.')
    return True


def update_pr_product_goods_receipt():
    pr_product_1 = GoodsReceiptRequestProduct.objects.create(
        quantity_import=1,
        goods_receipt_id="3942210b-7441-461c-8120-a9a690154e2f",
        goods_receipt_product_id="d3b95cb5-916b-4c8e-810f-33a644640cd9",
        purchase_order_request_product_id="22ca3981-12f8-49e8-8c7d-bad1f5020cb3",
        purchase_request_product_id="01e4b12d-a7b9-4cd9-8ea5-59b8f64c4595",
        quantity_order=1,
    )
    if pr_product_1:
        gr_wh_1 = GoodsReceiptWarehouse.objects.filter(id="6e516bc2-3fd8-4e03-a8c2-3e72f6bead6f").first()
        if gr_wh_1:
            gr_wh_1.goods_receipt_request_product_id = pr_product_1.id
            gr_wh_1.save(update_fields=['goods_receipt_request_product_id'])
        # gr_1 = GoodsReceipt.objects.filter(id="3942210b-7441-461c-8120-a9a690154e2f").first()
        # if gr_1:
        #     IRForGoodsReceiptHandler.push_to_inventory_report(gr_1)
    pr_product_2 = GoodsReceiptRequestProduct.objects.create(
        quantity_import=1,
        goods_receipt_id="b02fc96d-2fe0-4c18-9dfb-e05e997e5b83",
        goods_receipt_product_id="48e6d4bc-20e7-473c-9d3c-401083b140c3",
        purchase_order_request_product_id="1b2f0498-3283-493b-8522-57c714bb777e",
        purchase_request_product_id="81006664-a40a-4100-bab8-367896e87226",
        quantity_order=1,
    )
    if pr_product_2:
        gr_wh_2 = GoodsReceiptWarehouse.objects.filter(id="cb4a0d86-6b6f-47a4-a4eb-abdd0d9bb897").first()
        if gr_wh_2:
            gr_wh_2.goods_receipt_request_product_id = pr_product_2.id
            gr_wh_2.save(update_fields=['goods_receipt_request_product_id'])
        # gr_2 = GoodsReceipt.objects.filter(id="edaddf9f-60b4-4e6e-bea8-5d123ffe1a8c").first()
        # if gr_2:
        #     IRForGoodsReceiptHandler.push_to_inventory_report(gr_2)
    InventoryReportRun.run('0248237b-cb6b-46b1-82ad-9282115a0624', 2025)
    print('update_pr_product_goods_receipt done.')
    return True


def hong_quang_delete_employee_user():
    employee_objs = Employee.objects.filter(id__in=[
        "304b7593-1a55-40cc-9dc2-369b705e1495",
        "7c3e8a58-5bfb-4f34-8ada-5ef1775672f8",
        "bfcfe964-0927-4e32-b699-2986dde4a182",
        "c57adf7d-df03-4e88-bcc6-2ef055c39f48",
        "d8016733-a304-4bd9-9ea1-ad63fc7891ee",
        "0e6d2ccf-fea2-455f-801e-23d9be7d62b8",
        "47268955-c17f-4c55-a8dc-67429f78998b",
        "a54bc784-e703-4dcf-8b9a-a7e515cf918d",
        "72d2f1e8-4dbe-4c7c-b18c-a74e4af60465",
        "c4bd21d8-1925-45b4-8740-e7f122b33b11",
    ], company_id="0248237b-cb6b-46b1-82ad-9282115a0624")
    if employee_objs:
        employee_objs.delete()
    user_objs = User.objects.filter(id__in=[
        "c2270aaf-1a4c-4f5d-9a06-392466b90e65",
        "5179ca9c-4cd3-4f69-8756-3c5efe7d244f",
        "9ccc0add-284c-4cae-aa40-dda55d69ccda",
        "1f11c595-a52c-466f-b590-85b207db4c45",
        "845ae8ca-9468-4145-a01b-3e2ff86f591e",
        "74cf4e11-59f5-481c-889e-9bdefb1bb22a",
        "28d07573-b1c1-4311-be81-6aa1095e1e54",
        "f29aeb76-745c-4a27-9796-0716b9ea0a95",
        "29a51ae5-ab35-4811-85f4-64180a7d9430",
        "4637c760-33c9-42ab-a70f-0eae47668ae2",
    ])
    if user_objs:
        user_objs.delete()
    print('hong_quang_delete_employee_user done')


def hong_quang_delete_workflow():
    workflows_delete = Workflow.objects.filter(company="0248237b-cb6b-46b1-82ad-9282115a0624").exclude(id__in=[
        "d7f1d817-b469-4d6e-a9aa-82d45f9e96e2",
        "1f7fb6a6-3fea-4c46-be3d-6750e604c575",
        "32ccae59-ca45-4031-970e-0c5fa582ead4",
        "8c809b77-8ab6-400b-ae49-21ef1b29fe1d",
        "f452b3ca-8d1a-4449-bd44-7288242ee464",
        "212dfc8c-e37f-4391-985b-2fd7629aaa5c",
        "22f548e1-c040-41a5-9f80-94ecc9726341",
        "8363ab8c-a4c7-4d1a-a5fa-c599567211f8",
        "c5f6effd-1253-4d82-a648-d4b95de225d8",
    ])
    if workflows_delete:
        workflows_delete.delete()
    workflow_runtimes = Runtime.objects.filter(flow_id__in=[
        "d7f1d817-b469-4d6e-a9aa-82d45f9e96e2",
        "1f7fb6a6-3fea-4c46-be3d-6750e604c575",
        "32ccae59-ca45-4031-970e-0c5fa582ead4",
        "8c809b77-8ab6-400b-ae49-21ef1b29fe1d",
        "f452b3ca-8d1a-4449-bd44-7288242ee464",
        "212dfc8c-e37f-4391-985b-2fd7629aaa5c",
        "22f548e1-c040-41a5-9f80-94ecc9726341",
        "8363ab8c-a4c7-4d1a-a5fa-c599567211f8",
        "c5f6effd-1253-4d82-a648-d4b95de225d8",
    ])
    if workflow_runtimes:
        workflow_runtimes.delete()
    workflow_config_opp = WorkflowConfigOfApp.objects.filter(id="e5706d30-50f3-413f-9a30-312fae49a307").first()
    if workflow_config_opp:
        workflow_config_opp.delete()
    print("hong_quang_delete_workflow done.")
    return True


def hong_quang_delete_sales():
    opportunities = Opportunity.objects.filter(company="0248237b-cb6b-46b1-82ad-9282115a0624")
    if opportunities:
        opportunities.delete()
    quotations = Quotation.objects.filter(company="0248237b-cb6b-46b1-82ad-9282115a0624")
    if quotations:
        quotations.delete()
    sale_orders = SaleOrder.objects.filter(company="0248237b-cb6b-46b1-82ad-9282115a0624")
    if sale_orders:
        sale_orders.delete()
    advances = AdvancePayment.objects.filter(company="0248237b-cb6b-46b1-82ad-9282115a0624")
    if advances:
        advances.delete()
    payments = Payment.objects.filter(company="0248237b-cb6b-46b1-82ad-9282115a0624")
    if payments:
        payments.delete()
    purchases = PurchaseOrder.objects.filter(company="0248237b-cb6b-46b1-82ad-9282115a0624")
    if purchases:
        purchases.delete()
    print("hong_quang_delete_sales done.")
    return True


def hong_quang_delete_offices():
    leaves = LeaveRequest.objects.filter(company="0248237b-cb6b-46b1-82ad-9282115a0624")
    if leaves:
        leaves.delete()
    print("hong_quang_delete_offices done.")
    return True


def hong_quang_set_user_password():
    for user in User.objects.all():
        user.password = "pbkdf2_sha256$600000$USCJmMvz9hwi6yx90CZZQu$L4om3uuO+h9nPdRaldB2tw4yzjrpRhUxWWGqKTWdRpE="
        user.save(update_fields=['password'])
    print('hong_quang_set_user_password done.')
    return True


def hong_quang_delete_runtime_assignee():
    assignees = RuntimeAssignee.objects.filter(stage__runtime__doc_id="3c975cb5-9a63-44dd-99e1-5b34a2ff8ca6")
    if assignees:
        assignees.delete()
    print('hong_quang_delete_runtime_assignee done.')
    return True


def clean_data_svn():
    company_id = '696bbe7f-1d47-4752-ad3e-ce25881cf975'
    quotations = Quotation.objects.filter(company_id=company_id, system_status=0)
    if quotations:
        quotations.delete()
    products = Product.objects.filter(company_id=company_id)
    if products:
        products.delete()
    InventoryReportRun.run(company_id=company_id, fiscal_year=2025)
    print('clean_data_svn done.')
    return True


def run_push_diagram():
    for sale_order in SaleOrder.objects.all():
        SOHandler.push_diagram(instance=sale_order)
    for purchase_request in PurchaseRequest.objects.all():
        PRHandler.push_diagram(instance=purchase_request)
    for purchase_order in PurchaseOrder.objects.all():
        POHandler.push_diagram(instance=purchase_order)
    print('run_push_diagram done.')
    return True


def reset_picking_delivery(picking_id, delivery_id):
    picking_sub = OrderPickingSub.objects.filter(id=picking_id).first()
    if picking_sub:
        picking_sub.state = 0
        picking_sub.save(update_fields=['state'])
        delivery_sub = OrderDeliverySub.objects.filter(id=delivery_id).first()
        if delivery_sub:
            delivery_sub.ready_quantity = delivery_sub.ready_quantity - picking_sub.picked_quantity
            delivery_sub.save(update_fields=['ready_quantity'])
    print('reset_picking_delivery done.')
    return True


class VietnamAdministrativeAddress:
    @staticmethod
    def load_province():
        with open('apps/shared/new_address_json/province_with_uuid.json', 'r', encoding='utf-8') as f:
            province_data = json.load(f)

        bulk_info = []
        for province_id, province_info in province_data.items():
            bulk_info.append(NProvince(
                id=province_info.get('uuid', ''),
                country_id='bbf52b7b-77ed-4e8c-af0a-86ca00771d83',
                code=province_info.get('code', ''),
                slug=province_info.get('slug', ''),
                ptype=province_info.get('type', ''),
                name=province_info.get('name', ''),
                fullname=province_info.get('name_with_type', ''),
            ))
        NProvince.objects.all().delete()
        NProvince.objects.bulk_create(bulk_info)
        print('Done :))')
        return True

    @staticmethod
    def load_ward():
        with open('apps/shared/new_address_json/ward_with_uuid.json', 'r', encoding='utf-8') as f:
            ward_data = json.load(f)

        bulk_info = []
        for ward_id, ward_info in ward_data.items():
            province_obj = NProvince.objects.filter(code=ward_info.get('parent_code', '')).first()
            bulk_info.append(NWard(
                id=ward_info.get('uuid', ''),
                province=province_obj,
                province_code=province_obj.code,
                code=ward_info.get('code', ''),
                slug=ward_info.get('slug', ''),
                wtype=ward_info.get('type', ''),
                name=ward_info.get('name', ''),
                fullname=ward_info.get('name_with_type', ''),
                path=ward_info.get('path', ''),
                fullpath=ward_info.get('path_with_type', ''),
            ))
        NWard.objects.all().delete()
        NWard.objects.bulk_create(bulk_info)
        print('Done :))')
        return True


def update_loan_product():
    for obj in EquipmentLoan.objects.all():
        product_loan_data = []
        for item in obj.equipment_loan_items.all():
            product_loan_data.append(item.loan_product_data)
        obj.product_loan_data = product_loan_data
        obj.save(update_fields=['product_loan_data'])

    for obj in EquipmentReturn.objects.all():
        product_return_data = []
        for item in obj.equipment_return_items.all():
            product_return_data.append(item.return_product_data)
        obj.product_return_data = product_return_data
        obj.save(update_fields=['product_return_data'])

    print('Done :))')
    return True


def update_user_username(user_id, username, tenant_code):
    user_obj = User.objects.filter(id=user_id).first()
    if user_obj:
        user_obj.username = username
        user_obj.username_auth = username + '-' + tenant_code
        user_obj.save(update_fields=['username', 'username_auth'])
    print('update_user_username done.')
    return True


def create_template_print_default():
    for company in Company.objects.all():
        ConfigDefaultData(company).create_print_template_default(company)
    print('Done Create print template default !!')


def delete_opp_quotation_sale_order(company_id):
    opportunity = Opportunity.objects.filter(company_id=company_id)
    quotation = Quotation.objects.filter(company_id=company_id)
    sale_order = SaleOrder.objects.filter(company_id=company_id)
    if opportunity:
        opportunity.delete()
    if quotation:
        quotation.delete()
    if sale_order:
        sale_order.delete()
    print('delete_opp_quotation_sale_order done.')
    return True


def update_product_for_ecovn(company_code):
    code_list = ['TB.GG02', 'TB.GG10', 'TB.PCS500DX', 'TB.PCS500DXT', 'TB.PCS400T', 'TB.PCS400G', 'TB.BLADEXT',
                 'E.GSODIGESTER.100',
                 'E.DIY.100', 'E.ECOBALL', 'NVL.BOS.1000', 'DD.BOS.1000', 'DD.BOS.500', 'DD.BOS.250', 'E.GSOGEL.1000',
                 'E.GSOGEL.250', 'E.AQUA.100', 'CP.ECOFERT.1L', 'CP.ECOFERT.5L', 'CP.ECOI.M.1L', 'CP.ECOINS.1L',
                 'CP.ECOINS.5L',
                 'PK.350.MIDDLEAIRCOVER', 'PK.350.BLDC', 'PK.350.MAINPCB', 'PK.350.FANMOTOR', 'PK.350.DOORASSY',
                 'PK.350.FILTERCAP',
                 'PK.350.SUCTIONPUMP', 'PK.350.RECAPTACLE', 'PK.350.UPPERCOVERASSY', 'PK.350.COUPLINGLOWER',
                 'PK.350.PARTSFOR RECEPTACLE (2)', 'PK.350.DOORSENSOR', 'PK.350.TOPCOVER', 'PK.350.FILTER',
                 'PK.400.CHANELPCB',
                 'PK.400.MAINPCB', 'PK.400.FANMOTOR', 'PK.400S.DOORASSY', 'PK.400W.DOORASSY', 'PK.400G.DOORASSY',
                 'PK.400.RECEPTACLE', 'PK.400.COUPLINGLOWWER', 'PK.400.PARTSFORRECEPTACLE (2)',
                 'PK.400.PARTSFORRECEPTACLE (1)',
                 'PK.400.DOORLATCH', 'PK.400.DISPLAYPCB', 'PK.400.POWERCABLE', 'PK.400.FILTERPACKING',
                 'PK.400W.FILTERCOVER',
                 'PK.400S.FILTERCOVER', 'PK.400G.FILTERCOVER', 'PK.400.SCUPPER', 'PK.400.UPPERCOVER',
                 'PK.400.HEATERSENSOR',
                 'PK.400.BIMETAL', 'PK.400.WATERTRAY', 'PK.400.GEARBOX', 'PK400.FILTERASSY', 'PK.400.HEATERASSY',
                 'PK.500.HEATERHARMESS.H', 'PK.500.HEATERHARMESS.B', 'PK.500.MAINPCB', 'PK.500.FANMOTOR',
                 'PK.500.DOORASSY',
                 'PK.500.FILTERCAP', 'PK.500.RECEPTACLE', 'PK.500.COUPLINGLOWER', 'PK.500.PARTSFORRECEPTACLE(2)',
                 'PK.500.PARTSFORRECEPTACLE (1)', 'PK.500.DISPLAYPCB', 'PK.500.FILTERCOVER', 'PK.500.HEATERSENSOR',
                 'PK.500.BIMETAL', 'PK.500.WATERTRAY', 'PK.500.UPPERCOVER', 'PK.500.STEAMCOVER', 'PK.500.HINGECOVER',
                 'PK.500.FILTER', 'PK.500.DOORLATCHASSY', 'PK.500.BLOWINGFAN', 'PK.500.GREARBOX',
                 'PK.500.HEATINGPLATEASSY',
                 'PK.BLADEX.STORAGE', 'PK.GG02.CHECKSENSOR', 'PK.GG02.BLADE-SIDE', 'PK.GG02.INPUTLIDSEAL',
                 'PK.GG02.FILTER',
                 'PK.GG02.BLADE-CENTER', 'PK.GG02.MAINMOTOR', 'PK.GG02.CHAIN', 'PK.GG02.MAINPCB', 'PK.GG02.FANMOTOR',
                 'PK.GG02.DISPLAYPCBASSY', 'PK.GG02.HEATINGSENSOR', 'PK.GG02.SCOOP', 'PK.GGO2.HEATING ELEMENT',
                 'PK.GG02.HEAT HOLDING MATERIAL_ SET', 'PK.GG02.PCBMICOMCHIP', 'PK.GG02.MOTORPLASTICGEAR',
                 'PK.GG500.SEALOUTPUT',
                 'PK.GG500.SEALINPUT', 'PK.GG500.TANKSENSOR', 'PK.GG500.OILSENSOR', 'PK.GG500.HUMIDITYSENSOR',
                 'PK.GG500.FANMOTOR',
                 'PK.GG500.UVLAMP', 'PK.GG30.TANKSENSOR', 'PK.GG30.OILSENSOR', 'PK.GG30.HUMIDITYSENSOR',
                 'PK.GG30.FANMOTOR',
                 'PK.GG30N.UVLAMP', 'PK.GG30.SEALOUTPUT', 'PK.GG10-GG30.TOUCHSREENMAGNET', 'PK.GG30.CENTERMIXINGBLADE',
                 'PK.GG30.OFFLOADDOORHANDLE', 'PK.GG10.TANKSENSOR', 'PK.GG10.OILSENSOR', 'PK.GG10.HUMIDITYSENSOR',
                 'PK.GG10.FANMOTOR', 'PK.GG10.UVLAMP', 'PK.GG10.SEALOUTPUT']
    sale_uom_list = ['UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM005', 'UOM005', 'UOM008',
                     'UOM007',
                     'UOM007', 'UOM007', 'UOM007', 'UOM007', 'UOM007', 'UOM005', 'UOM007', 'UOM007', 'UOM007', 'UOM007',
                     'UOM007',
                     'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                     'UOM001',
                     'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                     'UOM001',
                     'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                     'UOM001',
                     'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                     'UOM001',
                     'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                     'UOM001',
                     'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                     'UOM001',
                     'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                     'UOM006',
                     'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                     'UOM001',
                     'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                     'UOM001',
                     'UOM001', 'UOM001']
    sale_tax_list = ['VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8',
                     'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_0', 'VAT_0', 'VAT_10', 'VAT_10', 'VAT_8',
                     'VAT_8', 'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8',
                     'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8',
                     'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8',
                     'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8',
                     'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8',
                     'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8',
                     'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8',
                     'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8',
                     'VAT_8',
                     'VAT_8', 'VAT_8', 'VAT_8']
    inventory_uom_list = ['UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM005', 'UOM005',
                          'UOM008', 'UOM007',
                          'UOM007', 'UOM007', 'UOM007', 'UOM007', 'UOM007', 'UOM005', 'UOM007', 'UOM007', 'UOM007',
                          'UOM007', 'UOM007',
                          'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                          'UOM001', 'UOM001',
                          'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                          'UOM001', 'UOM001',
                          'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                          'UOM001', 'UOM001',
                          'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                          'UOM001', 'UOM001',
                          'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                          'UOM001', 'UOM001',
                          'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                          'UOM001', 'UOM001',
                          'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                          'UOM001', 'UOM006',
                          'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                          'UOM001', 'UOM001',
                          'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                          'UOM001', 'UOM001',
                          'UOM001', 'UOM001']
    valuation_method_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0]
    purchase_uom_list = ['UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM005', 'UOM005',
                         'UOM008', 'UOM001', 'UOM007',
                         'UOM007', 'UOM007', 'UOM007', 'UOM007', 'UOM005', 'UOM007', 'UOM007', 'UOM007', 'UOM007',
                         'UOM007', 'UOM001',
                         'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                         'UOM001', 'UOM001',
                         'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                         'UOM001', 'UOM001',
                         'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                         'UOM001', 'UOM001',
                         'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                         'UOM001', 'UOM001',
                         'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                         'UOM001', 'UOM001',
                         'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                         'UOM001', 'UOM001',
                         'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                         'UOM006', 'UOM001',
                         'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                         'UOM001', 'UOM001',
                         'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001', 'UOM001',
                         'UOM001', 'UOM001',
                         'UOM001']
    purchase_tax_list = ['VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_8',
                         'VAT_8', 'VAT_8', 'VAT_8', 'VAT_8', 'VAT_10', 'VAT_0', 'VAT_0', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10', 'VAT_10',
                         'VAT_10', 'VAT_10']
    supplied_by_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(len(code_list)):
        product_obj = Product.objects.filter(company__code=company_code, code=code_list[i]).first()
        if product_obj:
            product_obj.product_choice = [0, 1, 2]
            # sale
            sale_uom_obj = UnitOfMeasure.objects.filter(company__code=company_code, code=sale_uom_list[i]).first()
            product_obj.sale_default_uom = sale_uom_obj
            product_obj.sale_default_uom_data = {
                'id': str(sale_uom_obj.id),
                'code': sale_uom_obj.code,
                'title': sale_uom_obj.title,
            } if sale_uom_obj else {}
            sale_tax_obj = Tax.objects.filter(company__code=company_code, code=sale_tax_list[i]).first()
            product_obj.sale_tax = sale_tax_obj
            product_obj.sale_tax_data = {
                'id': str(sale_tax_obj.id),
                'code': sale_tax_obj.code,
                'title': sale_tax_obj.title,
                'rate': sale_tax_obj.rate,
            } if sale_tax_obj else {}
            # inventory
            inventory_uom_obj = UnitOfMeasure.objects.filter(company__code=company_code,
                                                             code=inventory_uom_list[i]).first()
            product_obj.inventory_uom = inventory_uom_obj
            product_obj.inventory_uom_data = {
                'id': str(inventory_uom_obj.id),
                'code': inventory_uom_obj.code,
                'title': inventory_uom_obj.title,
            } if inventory_uom_obj else {}
            product_obj.valuation_method = valuation_method_list[i]
            # purchase
            purchase_uom_obj = UnitOfMeasure.objects.filter(company__code=company_code,
                                                            code=purchase_uom_list[i]).first()
            product_obj.purchase_default_uom = sale_uom_obj
            product_obj.purchase_default_uom_data = {
                'id': str(purchase_uom_obj.id),
                'code': purchase_uom_obj.code,
                'title': purchase_uom_obj.title,
            } if purchase_uom_obj else {}
            purchase_tax_obj = Tax.objects.filter(company__code=company_code, code=purchase_tax_list[i]).first()
            product_obj.purchase_tax = purchase_tax_obj
            product_obj.purchase_tax_data = {
                'id': str(purchase_tax_obj.id),
                'code': purchase_tax_obj.code,
                'title': purchase_tax_obj.title,
                'rate': purchase_tax_obj.rate,
            } if purchase_tax_obj else {}
            product_obj.supplied_by = supplied_by_list[i]
            product_obj.save(update_fields=[
                'product_choice',
                # sale
                'sale_default_uom',
                'sale_default_uom_data',
                'sale_tax',
                'sale_tax_data',
                # inventory
                'inventory_uom',
                'inventory_uom_data',
                'valuation_method',
                # purchase
                'purchase_default_uom',
                'purchase_default_uom_data',
                'purchase_tax',
                'purchase_tax_data',
                'supplied_by',
            ])
        else:
            print(f'{i}. Missing {code_list[i]}')

    print('Done :))')
    return True


def update_sale_lease_order_delivery_sub():
    for delivery_sub in OrderDeliverySub.objects.all():
        delivery_sub.sale_order_id = delivery_sub.sale_order_data.get('id', None)
        delivery_sub.lease_order_id = delivery_sub.lease_order_data.get('id', None)
        delivery_sub.save(update_fields=['sale_order_id', 'lease_order_id'], skip_check_period=True)
        if delivery_sub.sale_order:
            for deli_product in delivery_sub.delivery_product_delivery_sub.all():
                if deli_product.product:
                    so_prod = deli_product.product.sale_order_product_product.filter(
                        sale_order_id=delivery_sub.sale_order_id
                    ).first()
                    if so_prod:
                        deli_product.product_description = so_prod.product_description
                        deli_product.save(update_fields=['product_description'], for_goods_return=True)
    print('update_sale_lease_order_delivery_sub done.')
    return True


def update_employee_inherit_id_payment_plan():
    for payment_plan in PaymentPlan.objects.all():
        if payment_plan.sale_order:
            payment_plan.employee_inherit_id = payment_plan.sale_order.employee_inherit_id
        if payment_plan.purchase_order:
            payment_plan.employee_inherit_id = payment_plan.purchase_order.employee_inherit_id
        payment_plan.save(update_fields=['employee_inherit_id'])
    print('update_employee_inherit_id_payment_plan done.')
    return True


def update_quotation_products_data(quotation_id):
    quotation = Quotation.objects.filter(id=quotation_id).first()
    if quotation:
        quotation_products_data = [
            {
                "product_id": "4fc6cf2d-2fb8-4ec5-b64e-7b49213d8849",
                "product_title": "Máy tính để bàn HP Slim Desktop Core i7-12700 | 8GB | 512GB | Intel UHD | Win11 | Đen",
                "product_code": "HPI.DES.6K7B3PA",
                "product_data": {
                    "id": "4fc6cf2d-2fb8-4ec5-b64e-7b49213d8849",
                    "code": "HPI.DES.6K7B3PA",
                    "title": "Máy tính để bàn HP Slim Desktop Core i7-12700 | 8GB | 512GB | Intel UHD | Win11 | Đen",
                    "description": "Máy tính để bàn đồng bộ HP Slim Desktop S01-pF2024d 6K7B3PA (Core i7-12700 | 8GB | 512GB | Intel UHD | Win11 | Đen)",
                    "product_id": "4fc6cf2d-2fb8-4ec5-b64e-7b49213d8849",
                    "product_data": {
                        "id": "4fc6cf2d-2fb8-4ec5-b64e-7b49213d8849",
                        "title": "Máy tính để bàn HP Slim Desktop Core i7-12700 | 8GB | 512GB | Intel UHD | Win11 | Đen",
                        "code": "HPI.DES.6K7B3PA"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "bc6d7184-6942-42ad-97f0-5937bbcdcfde",
                            "title": "Desktop",
                            "code": "DES"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "469a0812-9d37-44c0-a170-a19342b3ec8b",
                            "title": "Bộ",
                            "code": "UOM006",
                            "ratio": 1,
                            "rounding": 1,
                            "is_referenced_unit": False
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "469a0812-9d37-44c0-a170-a19342b3ec8b",
                            "title": "Bộ",
                            "code": "UOM006",
                            "ratio": 1,
                            "rounding": 1,
                            "is_referenced_unit": False
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "469a0812-9d37-44c0-a170-a19342b3ec8b",
                                "title": "Bộ",
                                "code": "UOM006",
                                "ratio": 1,
                                "rounding": 1,
                                "is_referenced_unit": False
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {
                            "id": "469a0812-9d37-44c0-a170-a19342b3ec8b",
                            "title": "Bộ",
                            "code": "UOM006",
                            "ratio": 1,
                            "rounding": 1,
                            "is_referenced_unit": False
                        }
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": False,
                        "is_so_using": False
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "469a0812-9d37-44c0-a170-a19342b3ec8b",
                "product_uom_title": "Bộ",
                "product_uom_code": "UOM006",
                "uom_data": {
                    "id": "469a0812-9d37-44c0-a170-a19342b3ec8b",
                    "title": "Bộ",
                    "code": "UOM006",
                    "ratio": 1,
                    "rounding": 1,
                    "is_referenced_unit": False
                },
                "product_quantity": 1,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 1284000,
                "product_description": "Máy tính để bàn đồng bộ HP Slim Desktop S01-pF2024d 6K7B3PA (Core i7-12700 | 8GB | 512GB | Intel UHD | Win11 | Đen)",
                "product_unit_price": 16050000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 16050000,
                "product_subtotal_price_after_tax": 17334000,
                "order": 1,
                "is_group": False
            },
            {
                "product_id": "801bc8f2-6c2e-443a-8f7b-3c67dd17d8ca",
                "product_title": "Card mạng 2 cổng cho máy tính để bàn",
                "product_code": "GIG.CRD.82546-2RJ45",
                "product_data": {
                    "id": "801bc8f2-6c2e-443a-8f7b-3c67dd17d8ca",
                    "code": "GIG.CRD.82546-2RJ45",
                    "title": "Card mạng 2 cổng cho máy tính để bàn",
                    "description": "Card mạng LAN 2 cổng PCI ra Dual 2 Port Gigabit Ethernet intel 82546 cho máy tính để bàn",
                    "product_id": "801bc8f2-6c2e-443a-8f7b-3c67dd17d8ca",
                    "product_data": {
                        "id": "801bc8f2-6c2e-443a-8f7b-3c67dd17d8ca",
                        "title": "Card mạng 2 cổng cho máy tính để bàn",
                        "code": "GIG.CRD.82546-2RJ45"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "65e98dfd-8ecd-4c7a-b5d6-891fecc57538",
                            "title": "Card",
                            "code": "CRD"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "title": "Cái",
                                "code": "UOM001",
                                "ratio": 1,
                                "rounding": 4,
                                "is_referenced_unit": True
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": False,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "title": "Cái",
                    "code": "UOM001",
                    "ratio": 1,
                    "rounding": 4,
                    "is_referenced_unit": True
                },
                "product_quantity": 1,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 160000,
                "product_description": "Card mạng LAN 2 cổng PCI ra Dual 2 Port Gigabit Ethernet intel 82546 cho máy tính để bàn",
                "product_unit_price": 2000000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 2000000,
                "product_subtotal_price_after_tax": 2160000,
                "order": 2,
                "is_group": False
            },
            {
                "product_id": "f8a79232-a258-4a20-927a-8453ba377449",
                "product_title": "Thanh đấu nối patch panel CAT6 24 port",
                "product_code": "CSC.CAB.760237040/9",
                "product_data": {
                    "id": "f8a79232-a258-4a20-927a-8453ba377449",
                    "code": "CSC.CAB.760237040/9",
                    "title": "Thanh đấu nối patch panel CAT6 24 port",
                    "description": "Thanh đấu nối Patch Panel 24 cổng CAT6 Commscope",
                    "product_id": "f8a79232-a258-4a20-927a-8453ba377449",
                    "product_data": {
                        "id": "f8a79232-a258-4a20-927a-8453ba377449",
                        "title": "Thanh đấu nối patch panel CAT6 24 port",
                        "code": "CSC.CAB.760237040/9"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "title": "Cáp, dây dẫn",
                            "code": "CAB"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "title": "Cái",
                                "code": "UOM001",
                                "ratio": 1,
                                "rounding": 4,
                                "is_referenced_unit": True
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": True,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 1000000
                },
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "title": "Cái",
                    "code": "UOM001",
                    "ratio": 1,
                    "rounding": 4,
                    "is_referenced_unit": True
                },
                "product_quantity": 3,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 1428000,
                "product_description": "Thanh đấu nối Patch Panel 24 cổng CAT6 Commscope",
                "product_unit_price": 5950000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 17850000,
                "product_subtotal_price_after_tax": 19278000,
                "order": 3,
                "is_group": False
            },
            {
                "product_id": "215268d7-7dae-415d-ace8-c323d445a9b3",
                "product_title": "Ổ cắm mạng 1 port CAT6 Commscope",
                "product_code": "CSC.CAB.1375055-1",
                "product_data": {
                    "id": "215268d7-7dae-415d-ace8-c323d445a9b3",
                    "code": "CSC.CAB.1375055-1",
                    "title": "Ổ cắm mạng 1 port CAT6 Commscope",
                    "description": "Ổ cắm mạng 1 port CAT6 Commscope (bao gồm Box, Face, Module)",
                    "product_id": "215268d7-7dae-415d-ace8-c323d445a9b3",
                    "product_data": {
                        "id": "215268d7-7dae-415d-ace8-c323d445a9b3",
                        "title": "Ổ cắm mạng 1 port CAT6 Commscope",
                        "code": "CSC.CAB.1375055-1"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "title": "Cáp, dây dẫn",
                            "code": "CAB"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "title": "Cái",
                                "code": "UOM001",
                                "ratio": 1,
                                "rounding": 4,
                                "is_referenced_unit": True
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": False,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "title": "Cái",
                    "code": "UOM001",
                    "ratio": 1,
                    "rounding": 4,
                    "is_referenced_unit": True
                },
                "product_quantity": 32,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 819200,
                "product_description": "Ổ cắm mạng 1 port CAT6 Commscope (bao gồm Box, Face, Module)",
                "product_unit_price": 320000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 10240000,
                "product_subtotal_price_after_tax": 11059200,
                "order": 4,
                "is_group": False
            },
            {
                "product_id": "2ca23b24-58d2-44fa-ac6a-1f8ae442272a",
                "product_title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 3.0 mét",
                "product_code": "CSC.CAB.NPC06UVDB-RD010F",
                "product_data": {
                    "id": "2ca23b24-58d2-44fa-ac6a-1f8ae442272a",
                    "code": "CSC.CAB.NPC06UVDB-RD010F",
                    "title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 3.0 mét",
                    "description": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 3.0 mét",
                    "product_id": "2ca23b24-58d2-44fa-ac6a-1f8ae442272a",
                    "product_data": {
                        "id": "2ca23b24-58d2-44fa-ac6a-1f8ae442272a",
                        "title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 3.0 mét",
                        "code": "CSC.CAB.NPC06UVDB-RD010F"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "title": "Cáp, dây dẫn",
                            "code": "CAB"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "title": "Cái",
                                "code": "UOM001",
                                "ratio": 1,
                                "rounding": 4,
                                "is_referenced_unit": True
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": False,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "6357dffe-05ad-458e-a11b-1b8a9f2bb686",
                "product_uom_title": "Sợi",
                "product_uom_code": "UOM007",
                "uom_data": {
                    "id": "6357dffe-05ad-458e-a11b-1b8a9f2bb686",
                    "code": "UOM007",
                    "title": "Sợi",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": False
                    },
                    "ratio": 1,
                    "is_default": False
                },
                "product_quantity": 32,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 512000,
                "product_description": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 3.0 mét",
                "product_unit_price": 200000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 6400000,
                "product_subtotal_price_after_tax": 6912000,
                "order": 5,
                "is_group": False
            },
            {
                "product_id": "6a691684-3b73-4cfe-ac97-629cb673add3",
                "product_title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 1.5 mét",
                "product_code": "CSC.CAB.NPC06UVDB-BL005F",
                "product_data": {
                    "id": "6a691684-3b73-4cfe-ac97-629cb673add3",
                    "code": "CSC.CAB.NPC06UVDB-BL005F",
                    "title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 1.5 mét",
                    "description": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 1.5 mét",
                    "product_id": "6a691684-3b73-4cfe-ac97-629cb673add3",
                    "product_data": {
                        "id": "6a691684-3b73-4cfe-ac97-629cb673add3",
                        "title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 1.5 mét",
                        "code": "CSC.CAB.NPC06UVDB-BL005F"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "title": "Cáp, dây dẫn",
                            "code": "CAB"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "title": "Cái",
                                "code": "UOM001",
                                "ratio": 1,
                                "rounding": 4,
                                "is_referenced_unit": True
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": True,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "6357dffe-05ad-458e-a11b-1b8a9f2bb686",
                "product_uom_title": "Sợi",
                "product_uom_code": "UOM007",
                "uom_data": {
                    "id": "6357dffe-05ad-458e-a11b-1b8a9f2bb686",
                    "code": "UOM007",
                    "title": "Sợi",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": False
                    },
                    "ratio": 1,
                    "is_default": False
                },
                "product_quantity": 32,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 435200,
                "product_description": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 1.5 mét",
                "product_unit_price": 170000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 5440000,
                "product_subtotal_price_after_tax": 5875200,
                "order": 6,
                "is_group": False
            },
            {
                "product_id": "f37e8d58-b736-46e6-920f-145db8acc801",
                "product_title": "Dây cáp mạng CommScope CAT6 UTP",
                "product_code": "CSC.CAB.1427254-6",
                "product_data": {
                    "id": "f37e8d58-b736-46e6-920f-145db8acc801",
                    "code": "CSC.CAB.1427254-6",
                    "title": "Dây cáp mạng CommScope CAT6 UTP",
                    "description": "Dây cáp mạng CommScope CAT6 4 pair, 23AWG UTP, 305m/cuộn",
                    "product_id": "f37e8d58-b736-46e6-920f-145db8acc801",
                    "product_data": {
                        "id": "f37e8d58-b736-46e6-920f-145db8acc801",
                        "title": "Dây cáp mạng CommScope CAT6 UTP",
                        "code": "CSC.CAB.1427254-6"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "title": "Cáp, dây dẫn",
                            "code": "CAB"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "title": "Cái",
                                "code": "UOM001",
                                "ratio": 1,
                                "rounding": 4,
                                "is_referenced_unit": True
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": True,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 3200000
                },
                "unit_of_measure_id": "997f93a7-90fa-4373-aab3-d4f9df9bf5d6",
                "product_uom_title": "Thùng",
                "product_uom_code": "UOM008",
                "uom_data": {
                    "id": "997f93a7-90fa-4373-aab3-d4f9df9bf5d6",
                    "code": "UOM008",
                    "title": "Thùng",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": False
                    },
                    "ratio": 1,
                    "is_default": False
                },
                "product_quantity": 3,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 1689600,
                "product_description": "Dây cáp mạng CommScope CAT6 4 pair, 23AWG UTP, 305m/cuộn",
                "product_unit_price": 7040000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 21120000,
                "product_subtotal_price_after_tax": 22809600,
                "order": 7,
                "is_group": False
            },
            {
                "product_id": "ca9c4386-f800-43d1-9ac7-134045ef5368",
                "product_title": "Lắp đặt hệ thống cáp",
                "product_code": "HQG.DVU.LDHTC",
                "product_data": {
                    "id": "ca9c4386-f800-43d1-9ac7-134045ef5368",
                    "code": "HQG.DVU.LDHTC",
                    "title": "Lắp đặt hệ thống cáp",
                    "description": "Lắp đặt hệ thống cáp CAT6 (Kéo rải dây trong ống, nẹp. Lắp đặt đế nổi và đấu nối Outlet, Pacth Panel)\nInstalling CAT6 cable system (Pulling wires in pipes, clamps. Installing surface base and connecting Outlet, Pacth Panel)",
                    "product_id": "ca9c4386-f800-43d1-9ac7-134045ef5368",
                    "product_data": {
                        "id": "ca9c4386-f800-43d1-9ac7-134045ef5368",
                        "title": "Lắp đặt hệ thống cáp",
                        "code": "HQG.DVU.LDHTC"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "d968c963-de27-4531-9a32-d2bdedae2639",
                                "title": "Dịch vụ",
                                "code": "service",
                                "is_goods": False,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": True
                            }
                        ],
                        "product_category": {
                            "id": "30ff647d-96fb-405c-8b82-b8798bbfc640",
                            "title": "Dịch vụ",
                            "code": "SVC"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "ad0bc9c4-6322-4a7b-bdc5-127995b073d3",
                            "title": "Node",
                            "code": "UOM009",
                            "ratio": 1,
                            "rounding": 1,
                            "is_referenced_unit": False
                        },
                        "tax_code": {
                            "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                            "title": "VAT-8",
                            "code": "VAT_8",
                            "rate": 8
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {},
                        "tax": {}
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "ad0bc9c4-6322-4a7b-bdc5-127995b073d3",
                                "title": "Node",
                                "code": "UOM009",
                                "ratio": 1,
                                "rounding": 1,
                                "is_referenced_unit": False
                            }
                        }
                    ],
                    "product_choice": [
                        0
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {}
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": True,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "ad0bc9c4-6322-4a7b-bdc5-127995b073d3",
                "product_uom_title": "Node",
                "product_uom_code": "UOM009",
                "uom_data": {
                    "id": "ad0bc9c4-6322-4a7b-bdc5-127995b073d3",
                    "title": "Node",
                    "code": "UOM009",
                    "ratio": 1,
                    "rounding": 1,
                    "is_referenced_unit": False
                },
                "product_quantity": 32,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "title": "VAT-8",
                    "code": "VAT_8",
                    "rate": 8
                },
                "product_tax_amount": 2534400,
                "product_description": "Lắp đặt hệ thống cáp CAT6 (Kéo rải dây trong ống, nẹp. Lắp đặt đế nổi và đấu nối Outlet, Pacth Panel)\nInstalling CAT6 cable system (Pulling wires in pipes, clamps. Installing surface base and connecting Outlet, Pacth Panel)",
                "product_unit_price": 990000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 31680000,
                "product_subtotal_price_after_tax": 34214400,
                "order": 8,
                "is_group": False
            },
            {
                "product_id": "be7a9c41-7f65-4e62-a8d7-9e9225e07cae",
                "product_title": "Đấu nối hệ thống cáp",
                "product_code": "HQG.DVU.DNHTC",
                "product_data": {
                    "id": "be7a9c41-7f65-4e62-a8d7-9e9225e07cae",
                    "code": "HQG.DVU.DNHTC",
                    "title": "Đấu nối hệ thống cáp",
                    "description": "Đấu nối Outlet. Lắp đặt, đấu nối Patch panel. Đo test hệ thống cáp.",
                    "product_id": "be7a9c41-7f65-4e62-a8d7-9e9225e07cae",
                    "product_data": {
                        "id": "be7a9c41-7f65-4e62-a8d7-9e9225e07cae",
                        "title": "Đấu nối hệ thống cáp",
                        "code": "HQG.DVU.DNHTC"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "d968c963-de27-4531-9a32-d2bdedae2639",
                                "title": "Dịch vụ",
                                "code": "service",
                                "is_goods": False,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": True
                            }
                        ],
                        "product_category": {
                            "id": "30ff647d-96fb-405c-8b82-b8798bbfc640",
                            "title": "Dịch vụ",
                            "code": "SVC"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                            "title": "Gói",
                            "code": "UOM005",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": False
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                            "title": "Gói",
                            "code": "UOM005",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": False
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                                "title": "Gói",
                                "code": "UOM005",
                                "ratio": 1,
                                "rounding": 4,
                                "is_referenced_unit": False
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {}
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": False,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "c69027e7-3036-4f49-9ffc-006df8255259",
                "product_uom_title": "Gói",
                "product_uom_code": "UOM005",
                "uom_data": {
                    "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                    "title": "Gói",
                    "code": "UOM005",
                    "ratio": 1,
                    "rounding": 4,
                    "is_referenced_unit": False
                },
                "product_quantity": 1,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 880000,
                "product_description": "Đấu nối Outlet. Lắp đặt, đấu nối Patch panel. Đo test hệ thống cáp.",
                "product_unit_price": 11000000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 11000000,
                "product_subtotal_price_after_tax": 11880000,
                "order": 9,
                "is_group": False
            },
            {
                "product_id": "4b62347f-32ec-42a0-b631-4db7ae80e587",
                "product_title": "Vật tư thi công hạ tầng cáp",
                "product_code": "HQG.VTU.VTHTC",
                "product_data": {
                    "id": "4b62347f-32ec-42a0-b631-4db7ae80e587",
                    "code": "HQG.VTU.VTHTC",
                    "title": "Vật tư thi công hạ tầng cáp",
                    "description": "Vặt tư thi công (Ống ruột gà, nẹp tường, nẹp sàn phi 20, 25, 32…)",
                    "product_id": "4b62347f-32ec-42a0-b631-4db7ae80e587",
                    "product_data": {
                        "id": "4b62347f-32ec-42a0-b631-4db7ae80e587",
                        "title": "Vật tư thi công hạ tầng cáp",
                        "code": "HQG.VTU.VTHTC"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "4f73880c-7d2c-47e5-97a3-52ff91cd555b",
                            "title": "Vật tư",
                            "code": "VTU"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "title": "Cái",
                                "code": "UOM001",
                                "ratio": 1,
                                "rounding": 4,
                                "is_referenced_unit": True
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": False,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "c69027e7-3036-4f49-9ffc-006df8255259",
                "product_uom_title": "Gói",
                "product_uom_code": "UOM005",
                "uom_data": {
                    "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                    "code": "UOM005",
                    "title": "Gói",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": False
                    },
                    "ratio": 1,
                    "is_default": True
                },
                "product_quantity": 1,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 1584000,
                "product_description": "Vặt tư thi công (Ống ruột gà, nẹp tường, nẹp sàn phi 20, 25, 32…)",
                "product_unit_price": 19800000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 19800000,
                "product_subtotal_price_after_tax": 21384000,
                "order": 10,
                "is_group": False
            },
            {
                "product_id": "dcdf245e-f067-4705-b51f-4a0ddf379dd7",
                "product_title": "Vật tư phụ thi công hạ tầng cáp",
                "product_code": "HQG.VTU.VTPHTC",
                "product_data": {
                    "id": "dcdf245e-f067-4705-b51f-4a0ddf379dd7",
                    "code": "HQG.VTU.VTPHTC",
                    "title": "Vật tư phụ thi công hạ tầng cáp",
                    "description": "Vật tư tiêu hao, thang, dây đai, ống  lồng, dây rút, Plugboot, nhãn dán chuyên dụng...",
                    "product_id": "dcdf245e-f067-4705-b51f-4a0ddf379dd7",
                    "product_data": {
                        "id": "dcdf245e-f067-4705-b51f-4a0ddf379dd7",
                        "title": "Vật tư phụ thi công hạ tầng cáp",
                        "code": "HQG.VTU.VTPHTC"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "4f73880c-7d2c-47e5-97a3-52ff91cd555b",
                            "title": "Vật tư",
                            "code": "VTU"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "title": "VAT-10",
                            "code": "VAT_10",
                            "rate": 10
                        }
                    },
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_status": 1,
                            "price_type": 0,
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "title": "Cái",
                                "code": "UOM001",
                                "ratio": 1,
                                "rounding": 4,
                                "is_referenced_unit": True
                            }
                        }
                    ],
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "title": "Cái",
                            "code": "UOM001",
                            "ratio": 1,
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": False,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "c69027e7-3036-4f49-9ffc-006df8255259",
                "product_uom_title": "Gói",
                "product_uom_code": "UOM005",
                "uom_data": {
                    "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                    "code": "UOM005",
                    "title": "Gói",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": False
                    },
                    "ratio": 1,
                    "is_default": True
                },
                "product_quantity": 1,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 880000,
                "product_description": "Vật tư tiêu hao, thang, dây đai, ống  lồng, dây rút, Plugboot, nhãn dán chuyên dụng...",
                "product_unit_price": 11000000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 11000000,
                "product_subtotal_price_after_tax": 11880000,
                "order": 11,
                "is_group": False
            },
            {
                "product_id": "a415bbbc-772e-41e1-9b51-b16f6a59d02f",
                "product_title": "Đầu đọc vân tay ZK9500",
                "product_code": "ZKT.NVI.ZK9500",
                "product_data": {
                    "id": "a415bbbc-772e-41e1-9b51-b16f6a59d02f",
                    "code": "ZKT.NVI.ZK9500",
                    "title": "Đầu đọc vân tay ZK9500",
                    "description": "Đầu đọc vân tay dùng cho hệ thống kiểm soát ra vào, hệ thống ký điện tử",
                    "product_id": "a415bbbc-772e-41e1-9b51-b16f6a59d02f",
                    "product_data": {
                        "id": "a415bbbc-772e-41e1-9b51-b16f6a59d02f",
                        "title": "Đầu đọc vân tay ZK9500",
                        "code": "ZKT.NVI.ZK9500"
                    },
                    "general_information": {
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "title": "Hàng hóa",
                                "code": "goods",
                                "is_goods": True,
                                "is_finished_goods": False,
                                "is_material": False,
                                "is_tool": False,
                                "is_service": False
                            }
                        ],
                        "product_category": {
                            "id": "76e129af-6dc4-4ce4-a53a-2fb500c98317",
                            "title": "TB Ngoại vi",
                            "code": "NVI"
                        },
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "title": "Đơn vị",
                            "code": "Unit"
                        },
                        "general_traceability_method": 0
                    },
                    "sale_information": {
                        "default_uom": {},
                        "tax_code": {},
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "title": "Đồng Việt Nam",
                            "code": ""
                        },
                        "length": None,
                        "width": None,
                        "height": None
                    },
                    "purchase_information": {
                        "uom": {},
                        "tax": {}
                    },
                    "price_list": [],
                    "product_choice": [],
                    "supplied_by": 0,
                    "inventory_information": {
                        "uom": {}
                    },
                    "general_traceability_method": 0,
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_finished": False,
                        "is_so_using": True
                    },
                    "bom_data": {},
                    "standard_price": 0
                },
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "title": "Cái",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": True
                    },
                    "ratio": 1,
                    "is_default": True
                },
                "product_quantity": 55,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "title": "VAT-8",
                    "rate": 8,
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 9504000,
                "product_description": "Đầu đọc vân tay dùng cho hệ thống kiểm soát ra vào, hệ thống ký điện tử",
                "product_unit_price": 2160000,
                "product_discount_value": 0,
                "product_discount_amount": 0,
                "product_discount_amount_total": 0,
                "product_subtotal_price": 118800000,
                "product_subtotal_price_after_tax": 128304000,
                "order": 12,
                "is_group": False
            }
        ]
        quotation.quotation_products_data = quotation_products_data
        quotation.save(update_fields=['quotation_products_data'])
    print('update_quotation_products_data done.')
    return True


def update_quotation_costs_data(quotation_id):
    quotation = Quotation.objects.filter(id=quotation_id).first()
    if quotation:
        quotation_costs_data = [
            {
                "product_id": "4fc6cf2d-2fb8-4ec5-b64e-7b49213d8849",
                "product_title": "Máy tính để bàn HP Slim Desktop Core i7-12700 | 8GB | 512GB | Intel UHD | Win11 | Đen",
                "product_code": "HPI.DES.6K7B3PA",
                "product_data": {
                    "id": "4fc6cf2d-2fb8-4ec5-b64e-7b49213d8849",
                    "code": "HPI.DES.6K7B3PA",
                    "title": "Máy tính để bàn HP Slim Desktop Core i7-12700 | 8GB | 512GB | Intel UHD | Win11 | Đen",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "code": "UOM001",
                                "ratio": 1,
                                "title": "Cái",
                                "rounding": 4,
                                "is_referenced_unit": True
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "4fc6cf2d-2fb8-4ec5-b64e-7b49213d8849",
                    "description": "Máy tính để bàn đồng bộ HP Slim Desktop S01-pF2024d 6K7B3PA (Core i7-12700 | 8GB | 512GB | Intel UHD | Win11 | Đen)",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "4fc6cf2d-2fb8-4ec5-b64e-7b49213d8849",
                        "code": "HPI.DES.6K7B3PA",
                        "title": "Máy tính để bàn HP Slim Desktop Core i7-12700 | 8GB | 512GB | Intel UHD | Win11 | Đen"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "bc6d7184-6942-42ad-97f0-5937bbcdcfde",
                            "code": "DES",
                            "title": "Desktop"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "469a0812-9d37-44c0-a170-a19342b3ec8b",
                "product_uom_title": "Bộ",
                "product_uom_code": "UOM006",
                "uom_data": {
                    "id": "469a0812-9d37-44c0-a170-a19342b3ec8b",
                    "code": "UOM006",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": False
                    },
                    "ratio": 1,
                    "title": "Bộ",
                    "is_default": False
                },
                "product_quantity": 1,
                "tax_id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                "product_tax_title": "VAT-10",
                "product_tax_value": 10,
                "tax_data": {
                    "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                    "code": "VAT_10",
                    "rate": 10,
                    "title": "VAT-10"
                },
                "product_tax_amount": 1400000,
                "product_cost_price": 14000000,
                "product_subtotal_price": 14000000,
                "product_subtotal_price_after_tax": 15400000,
                "order": 1
            },
            {
                "product_id": "801bc8f2-6c2e-443a-8f7b-3c67dd17d8ca",
                "product_title": "Card mạng 2 cổng cho máy tính để bàn",
                "product_code": "GIG.CRD.82546-2RJ45",
                "product_data": {
                    "id": "801bc8f2-6c2e-443a-8f7b-3c67dd17d8ca",
                    "code": "GIG.CRD.82546-2RJ45",
                    "title": "Card mạng 2 cổng cho máy tính để bàn",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "code": "UOM001",
                                "ratio": 1,
                                "title": "Cái",
                                "rounding": 4,
                                "is_referenced_unit": True
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "801bc8f2-6c2e-443a-8f7b-3c67dd17d8ca",
                    "description": "Card mạng LAN 2 cổng PCI ra Dual 2 Port Gigabit Ethernet intel 82546 cho máy tính để bàn",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "801bc8f2-6c2e-443a-8f7b-3c67dd17d8ca",
                        "code": "GIG.CRD.82546-2RJ45",
                        "title": "Card mạng 2 cổng cho máy tính để bàn"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "65e98dfd-8ecd-4c7a-b5d6-891fecc57538",
                            "code": "CRD",
                            "title": "Card"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "ratio": 1,
                    "title": "Cái",
                    "rounding": 4,
                    "is_referenced_unit": True
                },
                "product_quantity": 1,
                "tax_id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                "product_tax_title": "VAT-10",
                "product_tax_value": 10,
                "tax_data": {
                    "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                    "code": "VAT_10",
                    "rate": 10,
                    "title": "VAT-10"
                },
                "product_tax_amount": 100000,
                "product_cost_price": 1000000,
                "product_subtotal_price": 1000000,
                "product_subtotal_price_after_tax": 1100000,
                "order": 2
            },
            {
                "product_id": "f8a79232-a258-4a20-927a-8453ba377449",
                "product_title": "Thanh đấu nối patch panel CAT6 24 port",
                "product_code": "CSC.CAB.760237040/9",
                "product_data": {
                    "id": "f8a79232-a258-4a20-927a-8453ba377449",
                    "code": "CSC.CAB.760237040/9",
                    "title": "Thanh đấu nối patch panel CAT6 24 port",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "code": "UOM001",
                                "ratio": 1,
                                "title": "Cái",
                                "rounding": 4,
                                "is_referenced_unit": True
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "f8a79232-a258-4a20-927a-8453ba377449",
                    "description": "Thanh đấu nối Patch Panel 24 cổng CAT6 Commscope",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "f8a79232-a258-4a20-927a-8453ba377449",
                        "code": "CSC.CAB.760237040/9",
                        "title": "Thanh đấu nối patch panel CAT6 24 port"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "standard_price": 1000000,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "code": "CAB",
                            "title": "Cáp, dây dẫn"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "ratio": 1,
                    "title": "Cái",
                    "rounding": 4,
                    "is_referenced_unit": True
                },
                "product_quantity": 3,
                "tax_id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                "product_tax_title": "VAT-10",
                "product_tax_value": 10,
                "tax_data": {
                    "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                    "code": "VAT_10",
                    "rate": 10,
                    "title": "VAT-10"
                },
                "product_tax_amount": 892650,
                "product_cost_price": 2975500,
                "product_subtotal_price": 8926500,
                "product_subtotal_price_after_tax": 9819150,
                "order": 3
            },
            {
                "product_id": "215268d7-7dae-415d-ace8-c323d445a9b3",
                "product_title": "Ổ cắm mạng 1 port CAT6 Commscope",
                "product_code": "CSC.CAB.1375055-1",
                "product_data": {
                    "id": "215268d7-7dae-415d-ace8-c323d445a9b3",
                    "code": "CSC.CAB.1375055-1",
                    "title": "Ổ cắm mạng 1 port CAT6 Commscope",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "code": "UOM001",
                                "ratio": 1,
                                "title": "Cái",
                                "rounding": 4,
                                "is_referenced_unit": True
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "215268d7-7dae-415d-ace8-c323d445a9b3",
                    "description": "Ổ cắm mạng 1 port CAT6 Commscope (bao gồm Box, Face, Module)",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "215268d7-7dae-415d-ace8-c323d445a9b3",
                        "code": "CSC.CAB.1375055-1",
                        "title": "Ổ cắm mạng 1 port CAT6 Commscope"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "code": "CAB",
                            "title": "Cáp, dây dẫn"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "ratio": 1,
                    "title": "Cái",
                    "rounding": 4,
                    "is_referenced_unit": True
                },
                "product_quantity": 32,
                "tax_id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                "product_tax_title": "VAT-10",
                "product_tax_value": 10,
                "tax_data": {
                    "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                    "code": "VAT_10",
                    "rate": 10,
                    "title": "VAT-10"
                },
                "product_tax_amount": 510400,
                "product_cost_price": 159500,
                "product_subtotal_price": 5104000,
                "product_subtotal_price_after_tax": 5614400,
                "order": 4
            },
            {
                "product_id": "2ca23b24-58d2-44fa-ac6a-1f8ae442272a",
                "product_title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 3.0 mét",
                "product_code": "CSC.CAB.NPC06UVDB-RD010F",
                "product_data": {
                    "id": "2ca23b24-58d2-44fa-ac6a-1f8ae442272a",
                    "code": "CSC.CAB.NPC06UVDB-RD010F",
                    "title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 3.0 mét",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "code": "UOM001",
                                "ratio": 1,
                                "title": "Cái",
                                "rounding": 4,
                                "is_referenced_unit": True
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "2ca23b24-58d2-44fa-ac6a-1f8ae442272a",
                    "description": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 3.0 mét",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "2ca23b24-58d2-44fa-ac6a-1f8ae442272a",
                        "code": "CSC.CAB.NPC06UVDB-RD010F",
                        "title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 3.0 mét"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "code": "CAB",
                            "title": "Cáp, dây dẫn"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "ratio": 1,
                    "title": "Cái",
                    "rounding": 4,
                    "is_referenced_unit": True
                },
                "product_quantity": 32,
                "tax_id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                "product_tax_title": "VAT-10",
                "product_tax_value": 10,
                "tax_data": {
                    "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                    "code": "VAT_10",
                    "rate": 10,
                    "title": "VAT-10"
                },
                "product_tax_amount": 313600,
                "product_cost_price": 98000,
                "product_subtotal_price": 3136000,
                "product_subtotal_price_after_tax": 3449600,
                "order": 5
            },
            {
                "product_id": "6a691684-3b73-4cfe-ac97-629cb673add3",
                "product_title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 1.5 mét",
                "product_code": "CSC.CAB.NPC06UVDB-BL005F",
                "product_data": {
                    "id": "6a691684-3b73-4cfe-ac97-629cb673add3",
                    "code": "CSC.CAB.NPC06UVDB-BL005F",
                    "title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 1.5 mét",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "code": "UOM001",
                                "ratio": 1,
                                "title": "Cái",
                                "rounding": 4,
                                "is_referenced_unit": True
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "6a691684-3b73-4cfe-ac97-629cb673add3",
                    "description": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 1.5 mét",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "6a691684-3b73-4cfe-ac97-629cb673add3",
                        "code": "CSC.CAB.NPC06UVDB-BL005F",
                        "title": "Cáp nhảy-Patch cord COMMSCOPE CAT6 UTP 1.5 mét"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "code": "CAB",
                            "title": "Cáp, dây dẫn"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "ratio": 1,
                    "title": "Cái",
                    "rounding": 4,
                    "is_referenced_unit": True
                },
                "product_quantity": 32,
                "tax_id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                "product_tax_title": "VAT-10",
                "product_tax_value": 10,
                "tax_data": {
                    "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                    "code": "VAT_10",
                    "rate": 10,
                    "title": "VAT-10"
                },
                "product_tax_amount": 264000,
                "product_cost_price": 82500,
                "product_subtotal_price": 2640000,
                "product_subtotal_price_after_tax": 2904000,
                "order": 6
            },
            {
                "product_id": "f37e8d58-b736-46e6-920f-145db8acc801",
                "product_title": "Dây cáp mạng CommScope CAT6 UTP",
                "product_code": "CSC.CAB.1427254-6",
                "product_data": {
                    "id": "f37e8d58-b736-46e6-920f-145db8acc801",
                    "code": "CSC.CAB.1427254-6",
                    "title": "Dây cáp mạng CommScope CAT6 UTP",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "code": "UOM001",
                                "ratio": 1,
                                "title": "Cái",
                                "rounding": 4,
                                "is_referenced_unit": True
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "f37e8d58-b736-46e6-920f-145db8acc801",
                    "description": "Dây cáp mạng CommScope CAT6 4 pair, 23AWG UTP, 305m/cuộn",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "f37e8d58-b736-46e6-920f-145db8acc801",
                        "code": "CSC.CAB.1427254-6",
                        "title": "Dây cáp mạng CommScope CAT6 UTP"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "standard_price": 3200000,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "b6a87e98-5479-4b90-9c34-05f41eab853b",
                            "code": "CAB",
                            "title": "Cáp, dây dẫn"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "ratio": 1,
                    "title": "Cái",
                    "rounding": 4,
                    "is_referenced_unit": True
                },
                "product_quantity": 3,
                "tax_id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                "product_tax_title": "VAT-10",
                "product_tax_value": 10,
                "tax_data": {
                    "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                    "code": "VAT_10",
                    "rate": 10,
                    "title": "VAT-10"
                },
                "product_tax_amount": 1056000,
                "product_cost_price": 3520000,
                "product_subtotal_price": 10560000,
                "product_subtotal_price_after_tax": 11616000,
                "order": 7
            },
            {
                "product_id": "ca9c4386-f800-43d1-9ac7-134045ef5368",
                "product_title": "Lắp đặt hệ thống cáp",
                "product_code": "HQG.DVU.LDHTC",
                "product_data": {
                    "id": "ca9c4386-f800-43d1-9ac7-134045ef5368",
                    "code": "HQG.DVU.LDHTC",
                    "title": "Lắp đặt hệ thống cáp",
                    "bom_data": {},
                    "price_list": [],
                    "product_id": "ca9c4386-f800-43d1-9ac7-134045ef5368",
                    "description": "Lắp đặt ống, nẹp. Kéo rải dây trong. Lắp đặt đế nổi.",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "ca9c4386-f800-43d1-9ac7-134045ef5368",
                        "code": "HQG.DVU.LDHTC",
                        "title": "Lắp đặt hệ thống cáp"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {},
                        "default_uom": {},
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "d968c963-de27-4531-9a32-d2bdedae2639",
                                "code": "service",
                                "title": "Dịch vụ",
                                "is_tool": False,
                                "is_goods": False,
                                "is_service": True,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "30ff647d-96fb-405c-8b82-b8798bbfc640",
                            "code": "SVC",
                            "title": "Dịch vụ"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {},
                        "uom": {}
                    },
                    "inventory_information": {
                        "uom": {}
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "ad0bc9c4-6322-4a7b-bdc5-127995b073d3",
                "product_uom_title": "Node",
                "product_uom_code": "UOM009",
                "uom_data": {
                    "id": "ad0bc9c4-6322-4a7b-bdc5-127995b073d3",
                    "code": "UOM009",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": False
                    },
                    "ratio": 1,
                    "title": "Node",
                    "is_default": False
                },
                "product_quantity": 32,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "rate": 8,
                    "title": "VAT-8",
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 1267200,
                "product_cost_price": 495000,
                "product_subtotal_price": 15840000,
                "product_subtotal_price_after_tax": 17107200,
                "order": 8
            },
            {
                "product_id": "be7a9c41-7f65-4e62-a8d7-9e9225e07cae",
                "product_title": "Đấu nối hệ thống cáp",
                "product_code": "HQG.DVU.DNHTC",
                "product_data": {
                    "id": "be7a9c41-7f65-4e62-a8d7-9e9225e07cae",
                    "code": "HQG.DVU.DNHTC",
                    "title": "Đấu nối hệ thống cáp",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                                "code": "UOM005",
                                "ratio": 1,
                                "title": "Gói",
                                "rounding": 4,
                                "is_referenced_unit": False
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "be7a9c41-7f65-4e62-a8d7-9e9225e07cae",
                    "description": "Đấu nối Outlet. Lắp đặt, đấu nối Patch panel. Đo test hệ thống cáp.",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "be7a9c41-7f65-4e62-a8d7-9e9225e07cae",
                        "code": "HQG.DVU.DNHTC",
                        "title": "Đấu nối hệ thống cáp"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        2
                    ],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                            "code": "UOM005",
                            "ratio": 1,
                            "title": "Gói",
                            "rounding": 4,
                            "is_referenced_unit": False
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "d968c963-de27-4531-9a32-d2bdedae2639",
                                "code": "service",
                                "title": "Dịch vụ",
                                "is_tool": False,
                                "is_goods": False,
                                "is_service": True,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "30ff647d-96fb-405c-8b82-b8798bbfc640",
                            "code": "SVC",
                            "title": "Dịch vụ"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                            "code": "UOM005",
                            "ratio": 1,
                            "title": "Gói",
                            "rounding": 4,
                            "is_referenced_unit": False
                        }
                    },
                    "inventory_information": {
                        "uom": {}
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "c69027e7-3036-4f49-9ffc-006df8255259",
                "product_uom_title": "Gói",
                "product_uom_code": "UOM005",
                "uom_data": {
                    "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                    "code": "UOM005",
                    "ratio": 1,
                    "title": "Gói",
                    "rounding": 4,
                    "is_referenced_unit": False
                },
                "product_quantity": 1,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "rate": 8,
                    "title": "VAT-8",
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 440000,
                "product_cost_price": 5500000,
                "product_subtotal_price": 5500000,
                "product_subtotal_price_after_tax": 5940000,
                "order": 9
            },
            {
                "product_id": "4b62347f-32ec-42a0-b631-4db7ae80e587",
                "product_title": "Vật tư thi công hạ tầng cáp",
                "product_code": "HQG.VTU.VTHTC",
                "product_data": {
                    "id": "4b62347f-32ec-42a0-b631-4db7ae80e587",
                    "code": "HQG.VTU.VTHTC",
                    "title": "Vật tư thi công hạ tầng cáp",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "code": "UOM001",
                                "ratio": 1,
                                "title": "Cái",
                                "rounding": 4,
                                "is_referenced_unit": True
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "4b62347f-32ec-42a0-b631-4db7ae80e587",
                    "description": "Vặt tư thi công (Ống ruột gà, nẹp tường, nẹp sàn phi 20, 25, 32…)",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "4b62347f-32ec-42a0-b631-4db7ae80e587",
                        "code": "HQG.VTU.VTHTC",
                        "title": "Vật tư thi công hạ tầng cáp"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "4f73880c-7d2c-47e5-97a3-52ff91cd555b",
                            "code": "VTU",
                            "title": "Vật tư"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "c69027e7-3036-4f49-9ffc-006df8255259",
                "product_uom_title": "Gói",
                "product_uom_code": "UOM005",
                "uom_data": {
                    "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                    "code": "UOM005",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": False
                    },
                    "ratio": 1,
                    "title": "Gói",
                    "is_default": True
                },
                "product_quantity": 1,
                "tax_id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                "product_tax_title": "VAT-10",
                "product_tax_value": 10,
                "tax_data": {
                    "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                    "code": "VAT_10",
                    "rate": 10,
                    "title": "VAT-10"
                },
                "product_tax_amount": 990000,
                "product_cost_price": 9900000,
                "product_subtotal_price": 9900000,
                "product_subtotal_price_after_tax": 10890000,
                "order": 10
            },
            {
                "product_id": "dcdf245e-f067-4705-b51f-4a0ddf379dd7",
                "product_title": "Vật tư phụ thi công hạ tầng cáp",
                "product_code": "HQG.VTU.VTPHTC",
                "product_data": {
                    "id": "dcdf245e-f067-4705-b51f-4a0ddf379dd7",
                    "code": "HQG.VTU.VTPHTC",
                    "title": "Vật tư phụ thi công hạ tầng cáp",
                    "bom_data": {},
                    "price_list": [
                        {
                            "id": "0635c95c-9914-482e-be89-1325efc38dd6",
                            "uom": {
                                "id": "02d31f81-313c-4be7-8839-f6088011afba",
                                "code": "UOM001",
                                "ratio": 1,
                                "title": "Cái",
                                "rounding": 4,
                                "is_referenced_unit": True
                            },
                            "title": "General Price List",
                            "value": 0,
                            "is_default": True,
                            "price_type": 0,
                            "price_status": 1
                        }
                    ],
                    "product_id": "dcdf245e-f067-4705-b51f-4a0ddf379dd7",
                    "description": "Vật tư tiêu hao, thang, dây đai, ống  lồng, dây rút, Plugboot, nhãn dán chuyên dụng...",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "dcdf245e-f067-4705-b51f-4a0ddf379dd7",
                        "code": "HQG.VTU.VTPHTC",
                        "title": "Vật tư phụ thi công hạ tầng cáp"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": False,
                        "is_so_finished": False
                    },
                    "product_choice": [
                        0,
                        1,
                        2
                    ],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "default_uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "4f73880c-7d2c-47e5-97a3-52ff91cd555b",
                            "code": "VTU",
                            "title": "Vật tư"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {
                            "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                            "code": "VAT_10",
                            "rate": 10,
                            "title": "VAT-10"
                        },
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "inventory_information": {
                        "uom": {
                            "id": "02d31f81-313c-4be7-8839-f6088011afba",
                            "code": "UOM001",
                            "ratio": 1,
                            "title": "Cái",
                            "rounding": 4,
                            "is_referenced_unit": True
                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "c69027e7-3036-4f49-9ffc-006df8255259",
                "product_uom_title": "Gói",
                "product_uom_code": "UOM005",
                "uom_data": {
                    "id": "c69027e7-3036-4f49-9ffc-006df8255259",
                    "code": "UOM005",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": False
                    },
                    "ratio": 1,
                    "title": "Gói",
                    "is_default": True
                },
                "product_quantity": 1,
                "tax_id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                "product_tax_title": "VAT-10",
                "product_tax_value": 10,
                "tax_data": {
                    "id": "4c751034-fd6a-4ad1-9bf0-b7a448f3cc45",
                    "code": "VAT_10",
                    "rate": 10,
                    "title": "VAT-10"
                },
                "product_tax_amount": 550000,
                "product_cost_price": 5500000,
                "product_subtotal_price": 5500000,
                "product_subtotal_price_after_tax": 6050000,
                "order": 11
            },
            {
                "product_id": "a415bbbc-772e-41e1-9b51-b16f6a59d02f",
                "product_title": "Đầu đọc vân tay ZK9500",
                "product_code": "ZKT.NVI.ZK9500",
                "product_data": {
                    "id": "a415bbbc-772e-41e1-9b51-b16f6a59d02f",
                    "code": "ZKT.NVI.ZK9500",
                    "title": "Đầu đọc vân tay ZK9500",
                    "bom_data": {

                    },
                    "price_list": [

                    ],
                    "product_id": "a415bbbc-772e-41e1-9b51-b16f6a59d02f",
                    "description": "Đầu đọc vân tay dùng cho hệ thống kiểm soát ra vào, hệ thống ký điện tử",
                    "supplied_by": 0,
                    "product_data": {
                        "id": "a415bbbc-772e-41e1-9b51-b16f6a59d02f",
                        "code": "ZKT.NVI.ZK9500",
                        "title": "Đầu đọc vân tay ZK9500"
                    },
                    "bom_check_data": {
                        "is_bom": False,
                        "is_bom_opp": False,
                        "is_so_using": True,
                        "is_so_finished": False
                    },
                    "product_choice": [

                    ],
                    "standard_price": 0,
                    "sale_information": {
                        "width": None,
                        "height": None,
                        "length": None,
                        "tax_code": {

                        },
                        "default_uom": {

                        },
                        "currency_using": {
                            "id": "5fd2a6fb-8bee-4084-bba1-50100bf798cf",
                            "code": "",
                            "title": "Đồng Việt Nam"
                        }
                    },
                    "general_information": {
                        "uom_group": {
                            "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                            "code": "Unit",
                            "title": "Đơn vị"
                        },
                        "product_type": [
                            {
                                "id": "82af8bdb-5ad2-4608-8db4-9ddc1f6639c3",
                                "code": "goods",
                                "title": "Hàng hóa",
                                "is_tool": False,
                                "is_goods": True,
                                "is_service": False,
                                "is_material": False,
                                "is_finished_goods": False
                            }
                        ],
                        "product_category": {
                            "id": "76e129af-6dc4-4ce4-a53a-2fb500c98317",
                            "code": "NVI",
                            "title": "TB Ngoại vi"
                        },
                        "general_traceability_method": 0
                    },
                    "purchase_information": {
                        "tax": {

                        },
                        "uom": {

                        }
                    },
                    "inventory_information": {
                        "uom": {

                        }
                    },
                    "general_traceability_method": 0
                },
                "supplied_by": 0,
                "unit_of_measure_id": "02d31f81-313c-4be7-8839-f6088011afba",
                "product_uom_title": "Cái",
                "product_uom_code": "UOM001",
                "uom_data": {
                    "id": "02d31f81-313c-4be7-8839-f6088011afba",
                    "code": "UOM001",
                    "group": {
                        "id": "b1efa35c-86da-403e-9c76-239b6aa0863a",
                        "code": "Unit",
                        "title": "Đơn vị",
                        "is_referenced_unit": True
                    },
                    "ratio": 1,
                    "title": "Cái",
                    "is_default": True
                },
                "product_quantity": 55,
                "tax_id": "eed95d45-e432-4180-aa22-d04197872bfc",
                "product_tax_title": "VAT-8",
                "product_tax_value": 8,
                "tax_data": {
                    "id": "eed95d45-e432-4180-aa22-d04197872bfc",
                    "code": "VAT_8",
                    "rate": 8,
                    "title": "VAT-8",
                    "category": {
                        "id": "369a4195-5473-405f-9f81-2bb252c62afd",
                        "title": "Thuế GTGT"
                    },
                    "tax_type": 2,
                    "is_default": True
                },
                "product_tax_amount": 0,
                "product_cost_price": 0,
                "product_subtotal_price": 0,
                "product_subtotal_price_after_tax": 0,
                "order": 12
            }
        ]
        quotation.quotation_costs_data = quotation_costs_data
        quotation.save(update_fields=['quotation_costs_data'])
    print('update_quotation_costs_data done.')
    return True


def update_invoice_payment_sale_order():
    sale_order = SaleOrder.objects.filter(id="f9106f94-aa0d-4a10-8f53-0e59cef388f5").first()
    if sale_order:
        sale_order.payment_term_id = "eb1fedc1-11ba-4b23-aa1d-d9cd7eedf627"
        sale_order.payment_term_data = {
            "id": "eb1fedc1-11ba-4b23-aa1d-d9cd7eedf627",
            "title": "Thanh toán 30-70",
            "code": "TT3070",
            "apply_for": 0,
            "term": [
                {
                    "id": "78d2d7cd-12e1-4414-b8b9-1887f1bde15f",
                    "value": "30",
                    "unit_type": 0,
                    "day_type": 2,
                    "no_of_days": "0",
                    "after": 6,
                    "order": 1,
                    "title": "Đợt 1"
                },
                {
                    "id": "3a00e5fa-2b99-4c0f-b72e-78c5cd7fcb7a",
                    "value": "Cân bằng",
                    "unit_type": 2,
                    "day_type": 2,
                    "no_of_days": "0",
                    "after": 2,
                    "order": 2,
                    "title": "Đợt 2"
                }
            ]
        }
        sale_order.sale_order_payment_stage = [
            {
                "order": 1,
                "term_id": "78d2d7cd-12e1-4414-b8b9-1887f1bde15f",
                "term_data": {
                    "id": "78d2d7cd-12e1-4414-b8b9-1887f1bde15f",
                    "value": "30",
                    "unit_type": 0,
                    "day_type": 2,
                    "no_of_days": "0",
                    "after": 6,
                    "order": 1,
                    "title": "Đợt 1"
                },
                "remark": "Thanh toán khi ký hợp đồng - 31/07 - 30% (Tạm ứng)",
                "date": "2025-07-31 00:00:00",
                "ratio": 30,
                "invoice": None,
                "is_ar_invoice": False,
                "invoice_data": {

                },
                "value_before_tax": 12500000.1,
                "reconcile_data": [

                ],
                "value_total": 12500000.1,
                "due_date": "2025-07-31 00:00:00"
            },
            {
                "order": 2,
                "term_id": "3a00e5fa-2b99-4c0f-b72e-78c5cd7fcb7a",
                "term_data": {
                    "id": "3a00e5fa-2b99-4c0f-b72e-78c5cd7fcb7a",
                    "value": "70",
                    "unit_type": 0,
                    "day_type": 2,
                    "no_of_days": "0",
                    "after": 2,
                    "order": 2,
                    "title": "Đợt 2"
                },
                "remark": "Thanh toán 14 ngày kể từ ngày nhận máy - 04/08 - 70%",
                "date": "2025-08-04 00:00:00",
                "ratio": 70,
                "invoice": 1,
                "is_ar_invoice": True,
                "invoice_data": {
                    "order": 1,
                    "remark": "Xuất hóa đơn 1 lần (ngày tạo 04/08)",
                    "date": "2025-08-04",
                    "term_data": [
                        {
                            "id": "78d2d7cd-12e1-4414-b8b9-1887f1bde15f",
                            "value": "30",
                            "unit_type": 0,
                            "day_type": 2,
                            "no_of_days": "0",
                            "after": 6,
                            "order": 1,
                            "title": "Đợt 1"
                        },
                        {
                            "id": "3a00e5fa-2b99-4c0f-b72e-78c5cd7fcb7a",
                            "value": "70",
                            "unit_type": 0,
                            "day_type": 2,
                            "no_of_days": "0",
                            "after": 2,
                            "order": 2,
                            "title": "Đợt 2"
                        }
                    ],
                    "ratio": 100,
                    "tax_id": "30d575f1-b2fc-4f93-8b4e-af9e4d79cd11",
                    "tax_data": {
                        "id": "30d575f1-b2fc-4f93-8b4e-af9e4d79cd11",
                        "code": "VAT_8",
                        "rate": 8,
                        "title": "VAT-8"
                    },
                    "total": 45000000.36,
                    "balance": 45000000.36
                },
                "value_before_tax": 29166666.9,
                "value_reconcile": 12500000.1,
                "reconcile_data": [
                    {
                        "order": 1,
                        "term_id": "78d2d7cd-12e1-4414-b8b9-1887f1bde15f",
                        "term_data": {
                            "id": "78d2d7cd-12e1-4414-b8b9-1887f1bde15f",
                            "value": "30",
                            "unit_type": 0,
                            "day_type": 2,
                            "no_of_days": "0",
                            "after": 6,
                            "order": 1,
                            "title": "Đợt 1"
                        },
                        "remark": "Thanh toán khi ký hợp đồng - 31/07 - 30% (Tạm ứng)",
                        "date": "2025-07-31 00:00:00",
                        "ratio": 30,
                        "invoice": None,
                        "is_ar_invoice": False,
                        "invoice_data": {

                        },
                        "value_before_tax": 12500000.1,
                        "reconcile_data": [

                        ],
                        "value_total": 12500000.1,
                        "due_date": "2025-07-31 00:00:00"
                    }
                ],
                "tax_id": "30d575f1-b2fc-4f93-8b4e-af9e4d79cd11",
                "tax_data": {
                    "id": "30d575f1-b2fc-4f93-8b4e-af9e4d79cd11",
                    "code": "VAT_8",
                    "rate": 8,
                    "title": "VAT-8"
                },
                "value_tax": 3333333.36,
                "value_total": 32500000.259999998,
                "due_date": "2025-08-18 00:00:00"
            }
        ]
        sale_order.sale_order_invoice = [
            {
                "order": 1,
                "remark": "Xuất hóa đơn 1 lần (ngày tạo 04/08)",
                "date": "2025-08-04",
                "term_data": [
                    {
                        "id": "78d2d7cd-12e1-4414-b8b9-1887f1bde15f",
                        "value": "30",
                        "unit_type": 0,
                        "day_type": 2,
                        "no_of_days": "0",
                        "after": 6,
                        "order": 1,
                        "title": "Đợt 1"
                    },
                    {
                        "id": "3a00e5fa-2b99-4c0f-b72e-78c5cd7fcb7a",
                        "value": "70",
                        "unit_type": 0,
                        "day_type": 2,
                        "no_of_days": "0",
                        "after": 2,
                        "order": 2,
                        "title": "Đợt 2"
                    }
                ],
                "ratio": 100,
                "tax_id": "30d575f1-b2fc-4f93-8b4e-af9e4d79cd11",
                "tax_data": {
                    "id": "30d575f1-b2fc-4f93-8b4e-af9e4d79cd11",
                    "code": "VAT_8",
                    "rate": 8,
                    "title": "VAT-8"
                },
                "total": 45000000.36,
                "balance": 0
            }
        ]
        sale_order.save(
            update_fields=['payment_term_id', 'payment_term_data', 'sale_order_payment_stage', 'sale_order_invoice'])
        sale_order.sale_order_payment_stage_sale_order.all().delete()
        SaleOrderPaymentStage.objects.bulk_create(
            [SaleOrderPaymentStage(
                sale_order=sale_order,
                tenant_id=sale_order.tenant_id,
                company_id=sale_order.company_id,
                **sale_order_payment_stage,
            ) for sale_order_payment_stage in sale_order.sale_order_payment_stage]
        )
        sale_order.sale_order_invoice_sale_order.all().delete()
        SaleOrderInvoice.objects.bulk_create(
            [SaleOrderInvoice(
                sale_order=sale_order,
                tenant_id=sale_order.tenant_id,
                company_id=sale_order.company_id,
                **sale_order_invoice,
            ) for sale_order_invoice in sale_order.sale_order_invoice]
        )
    print('update_invoice_payment_sale_order done.')
    return True


def update_purchase_request_data():
    for pr_obj in PurchaseRequest.objects.all():
        supplier_obj = pr_obj.supplier
        pr_obj.supplier_data = {
            'id': str(supplier_obj.id),
            'name': supplier_obj.name,
            'code': supplier_obj.code,
            'tax_code': supplier_obj.tax_code,
        } if supplier_obj else {}

        contact_obj = pr_obj.contact
        pr_obj.contact_data = {
            'id': str(contact_obj.id),
            'code': contact_obj.code,
            'fullname': contact_obj.fullname,
        } if contact_obj else {}

        sale_order_obj = pr_obj.sale_order
        pr_obj.sale_order_data = {
            'id': str(sale_order_obj.id),
            'code': sale_order_obj.code,
            'title': sale_order_obj.title,
        } if sale_order_obj else {}

        distribution_plan_obj = pr_obj.distribution_plan
        pr_obj.distribution_plan_data = {
            'id': str(distribution_plan_obj.id),
            'code': distribution_plan_obj.code,
            'title': distribution_plan_obj.title,
        } if distribution_plan_obj else {}

        pr_obj.save(update_fields=['supplier_data', 'contact_data', 'sale_order_data', 'distribution_plan_data'])

        for item in pr_obj.purchase_request.all():
            product_obj = item.product
            item.product_data = {
                'id': str(product_obj.id),
                'code': product_obj.code,
                'title': product_obj.title,
                'description': product_obj.description,
            } if product_obj else {}

            uom_obj = item.uom
            item.uom_data = {
                'id': str(uom_obj.id),
                'code': uom_obj.code,
                'title': uom_obj.title,
                'group_id': str(uom_obj.group_id)
            } if uom_obj else {}

            tax_obj = item.tax
            item.tax_data = {
                'id': str(tax_obj.id),
                'code': tax_obj.code,
                'title': tax_obj.title,
                'rate': tax_obj.rate,
            } if tax_obj else {}

            item.save(update_fields=['product_data', 'uom_data', 'tax_data'])
        print(f'Done for {pr_obj.code} - {pr_obj.company.title}')
    print('Done :))')


def delete_folders():
    Folder.objects.all().delete()
    print('delete_folders done.')
    return True


def rerun_convert_ap_cost_for_payment():
    # 1. Reset toàn bộ AP sum_converted_value về 0
    for ap_item in AdvancePaymentCost.objects.all():
        ap_item.sum_converted_value = 0
        ap_item.save(update_fields=['sum_converted_value'])

    # 2. Gom toàn bộ giá trị convert theo AP ID
    ap_convert_map = {}
    for payment in Payment.objects.filter(system_status=3).order_by('date_approved'):
        print(f"Converting {payment.code}")
        for item in payment.payment.all():
            for child in item.ap_cost_converted_list:
                ap_id = child.get('ap_cost_converted_id')
                value = child.get('value_converted')
                if ap_id and value:
                    if ap_id in ap_convert_map:
                        ap_convert_map[ap_id] += float(value)
                    else:
                        ap_convert_map[ap_id] = float(value)

    # 3. Kiểm tra hợp lệ và cập nhật
    for ap_id, total_convert in ap_convert_map.items():
        ap_item = AdvancePaymentCost.objects.filter(id=ap_id).first()
        if not ap_item:
            raise ValueError(f"AdvancePaymentCost (ID {ap_id}) not found")

        available = (ap_item.expense_after_tax_price +
                     ap_item.sum_return_value -
                     ap_item.sum_converted_value)

        if available < total_convert:
            continue
            # raise ValueError(
            #     f"Cannot convert advance payment (ID {ap_id}). "
            #     f"Available: {available}, Requested: {total_convert}"
            # )

        ap_item.sum_converted_value += total_convert
        ap_item.save(update_fields=['sum_converted_value'])

    return True


def make_sure_payroll_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).payroll_config()
    print('Make sure payroll config is done!')


def make_system_payroll_component():
    data_list = [
        {
            'title': 'Họ và Tên',
            'name': 'Employee name',
            'code': 'employee_name',
            'type': 1,
        },
        {
            'title': 'Mã NV',
            'name': 'Employee code',
            'code': 'employee_code',
            'type': 1,
        },
        {
            'title': 'Phòng ban',
            'name': 'Department',
            'code': 'employee_group',
            'type': 1,
        },
        {
            'title': 'Chức vụ',
            'name': 'Employee role',
            'code': 'employee_role',
            'type': 1,
        },
        {
            'title': 'Lương cơ bản',
            'name': 'Salary',
            'code': 'employee_salary',
            'type': 0,
        },
        {
            'title': 'Lương đóng bảo hiểm',
            'name': 'Insurance salary',
            'code': 'insurance_salary',
            'type': 0,
        },
        {
            'title': 'Thuế TNCN',
            'name': 'Income Tax',
            'code': 'income_tax',
            'type': 0,
        },
        {
            'title': 'BHXH doanh nghiệp',
            'name': 'Company social insurance',
            'code': 'company_social_insurance',
            'type': 0,
        },
        {
            'title': 'BHYT doanh nghiệp',
            'name': 'Company health insurance',
            'code': 'company_health_insurance',
            'type': 0,
        },
        {
            'title': 'BHTN doanh nghiệp',
            'name': 'Company unemployment insurance',
            'code': 'company_unemployment_insurance',
            'type': 0,
        },
        {
            'title': 'BHCĐ doanh nghiệp',
            'name': 'Company union insurance',
            'code': 'company_union_insurance',
            'type': 0,
        },
        {
            'title': 'BHXH',
            'name': 'Social insurance',
            'code': 'employee_social_insurance',
            'type': 0,
        },
        {
            'title': 'BHYT',
            'name': 'Health insurance',
            'code': 'employee_health_insurance',
            'type': 0,
        },
        {
            'title': 'BHTN',
            'name': 'Unemployment insurance',
            'code': 'employee_unemployment_insurance',
            'type': 0,
        },
        {
            'title': 'BHCĐ',
            'name': 'Union insurance',
            'code': 'employee_union_insurance',
            'type': 0,
        },
        {
            'title': 'Giảm trừ bản thân',
            'name': 'Personal deduction',
            'code': 'employee_personal_deduction',
            'type': 0,
        },
        {
            'title': 'Giảm trừ phụ thuộc',
            'name': 'Dependant deduction',
            'code': 'employee_dependant_deduction',
            'type': 0,
        },
        {
            'title': 'Phần trăm hưởng lương',
            'name': 'Salary ratio',
            'code': 'employee_salary_ratio',
            'type': 0,
        },
        {
            'title': 'Hệ số',
            'name': 'salary coefficient',
            'code': 'employee_salary_coefficient',
            'type': 0,
        },
        {
            'title': 'Bậc lương',
            'name': 'Salary level',
            'code': 'salary_level',
            'type': 0,
        },
        {
            'title': 'Số giờ tăng ca',
            'name': 'Overtime hours',
            'code': 'employee_overtime_hours',
            'type': 0,
        },
        {
            'title': 'Số giờ tăng ca trong tuần',
            'name': 'Overtime weekly hours',
            'code': 'employee_overtime_weekly_hours',
            'type': 0,
        },
        {
            'title': 'Số giờ tăng ca ngày lễ',
            'name': 'Overtime holiday hours',
            'code': 'employee_overtime_holiday_hours',
            'type': 0,
        },
        {
            'title': 'Số ngày công chuẩn',
            'name': 'Shift standard work',
            'code': 'shift_standard_work',
            'type': 0,
        },
        {
            'title': 'Số ngày công thực tế',
            'name': 'Actual work',
            'code': 'actual_work',
            'type': 0,
        },
        {
            'title': 'Tạm ứng',
            'name': 'Advance',
            'code': 'advance_salary',
            'type': 0,
        },
    ]
    create_bulk_lst = []
    company_obj_list = Company.objects.all()
    for company_obj in company_obj_list:
        for item in data_list:
            create_bulk_lst.append(AttributeComponent(
                component_title=item['title'],
                component_name=item['name'],
                component_code=item['code'],
                component_type=item['type'],
                component_mandatory=True,
                company=company_obj
            ))
    AttributeComponent.objects.all().delete()
    AttributeComponent.objects.bulk_create(create_bulk_lst)
    print('Completed create system payroll attribute')


def set_module_id_folder():
    module_ids = []
    for key, value in MODULE_MAPPING.items():
        if 'module_id' in value:
            module_ids.append(value['module_id'])
    folder_objs = Folder.objects.filter(id__in=module_ids)
    if folder_objs:
        for folder_obj in folder_objs:
            folder_obj.module_id = folder_obj.id
            folder_obj.save(update_fields=['module_id'])
    print('set_module_id_folder done.')
    return True


def recycle_is_delete(app_model, id_list):
    model_app = DisperseModel(app_model=app_model).get_model()
    if model_app and hasattr(model_app, 'objects'):
        for obj in model_app.objects.filter(id__in=id_list, is_delete=True):
            obj.is_delete = False
            obj.save(update_fields=['is_delete'])
    print('recycle_is_delete done.')
    return True


def update_delivery_product_offset_data_default():
    for delivery_product in OrderDeliveryProduct.objects.all():
        if delivery_product.offset_data == {}:
            delivery_product.offset_data = []
            delivery_product.save(**{
                    'for_goods_recovery': True,
                    'update_fields': ['offset_data']
                })
    print('update_delivery_product_offset_data_default done.')
    return True


def sync_dimension_value():
    for dimension_config in DimensionSyncConfig.objects.all():
        DimensionUtils.sync_old_data(dimension_config=dimension_config)
    print('sync_dimension_value done.')
    return True


def make_sure_default_dimension():
    for obj in Company.objects.all():
        SaleDefaultData(obj).create_dimension()
    print('make_sure_default_dimension done.')


def map_gr_to_ap(company_id):
    for ap in APInvoice.objects.filter(company_id=company_id):
        po = ap.purchase_order_mapped
        for gr in GoodsReceipt.objects.filter(purchase_order=po):
            APInvoiceGoodsReceipt.objects.create(
                ap_invoice=ap,
                goods_receipt_mapped=gr,
                goods_receipt_mapped_data={
                    'id': str(gr.id),
                    'code': gr.code,
                    'title': gr.title,
                }
            )
    print('Done :))')
    return True

