from apps.masterdata.saledata.models.periods import Periods
from apps.core.company.models import Company, CompanyFunctionNumber
from apps.masterdata.saledata.models.product import (
    ProductType, Product, UnitOfMeasure
)
from apps.masterdata.saledata.models.price import (
    UnitOfMeasureGroup, Tax, TaxCategory, Currency
)
from apps.masterdata.saledata.models.accounts import (
    Account, AccountCreditCards, AccountActivity, AccountContacts
)
from apps.core.base.models import (
    PlanApplication, ApplicationProperty, Application, SubscriptionPlan
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

from .extends.signals import ConfigDefaultData
from .permissions.util import PermissionController
from ..core.account.models import User
from ..core.attachments.models import Folder
from ..core.hr.models import (
    Employee, Role, EmployeePermission, RolePermission,
)
from ..core.mailer.models import MailTemplateSystem
from ..core.provisioning.utils import TenantController
from ..eoffice.leave.leave_util import leave_available_map_employee
from ..eoffice.leave.models import LeaveAvailable, WorkingYearConfig, WorkingHolidayConfig, LeaveRequest
from ..hrm.employeeinfo.models import EmployeeHRNotMapEmployeeHRM
from ..masterdata.promotion.models import Promotion
from ..masterdata.saledata.models.product_warehouse import ProductWareHouseLotTransaction
from ..sales.arinvoice.models import ARInvoice, ARInvoiceItems, ARInvoiceDelivery
from ..sales.arinvoice.utils.logical_finish import ARInvoiceFinishHandler
from ..sales.delivery.models import DeliveryConfig, OrderDeliverySub, OrderDeliveryProduct, OrderPickingProduct
from ..sales.delivery.models.delivery import OrderDeliverySerial, OrderDeliveryProductWarehouse
from ..sales.delivery.utils import DeliFinishHandler
from ..sales.financialcashflow.models import CashInflow, CashOutflow
from ..sales.financialcashflow.utils.logical_finish_cif import CashInFlowFinishHandler
from ..sales.financialcashflow.utils.logical_finish_cof import CashOutFlowFinishHandler
from ..sales.inventory.models import (
    InventoryAdjustmentItem, GoodsReceipt, GoodsReceiptWarehouse, GoodsReturn, GoodsDetail, GoodsReceiptRequestProduct
)
from ..sales.inventory.utils import GRFinishHandler, ReturnFinishHandler
from ..sales.lead.models import Lead
from ..sales.opportunity.models import (
    Opportunity, OpportunityConfigStage, OpportunitySaleTeamMember, OpportunityMeeting, OpportunityActivityLogs,
)
from ..sales.partnercenter.models import DataObject
from ..sales.paymentplan.models import PaymentPlan
from ..sales.project.models import Project, ProjectMapMember
from ..sales.purchasing.models import (
    PurchaseRequestProduct, PurchaseOrderRequestProduct, PurchaseOrder,
)
from ..sales.purchasing.utils import POFinishHandler
from ..sales.quotation.models import QuotationIndicatorConfig, Quotation
from ..sales.quotation.serializers import QuotationListSerializer
from ..sales.report.models import ReportCashflow
from ..sales.report.scripts import InventoryReportRun
from ..sales.report.utils import IRForGoodsReceiptHandler
from ..sales.revenue_plan.models import RevenuePlanGroupEmployee
from ..sales.saleorder.models import SaleOrderIndicatorConfig, SaleOrder, SaleOrderIndicator
from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer
from ..sales.saleorder.utils import SOFinishHandler
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
    if run_type == 0:  # run report revenue, customer, product
        ReportRevenue.objects.all().delete()
        ReportCustomer.objects.all().delete()
        ReportProduct.objects.all().delete()
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


def reset_and_run_product_info(company_id):
    # reset
    update_fields = ['stock_amount', 'wait_delivery_amount', 'wait_receipt_amount', 'available_amount']
    for product in Product.objects.filter(company_id=company_id):
        product.stock_amount = 0
        product.wait_delivery_amount = 0
        product.wait_receipt_amount = 0
        product.available_amount = 0
        product.save(update_fields=update_fields)
    # set input, output, return
    # input
    for po in PurchaseOrder.objects.filter(system_status=3, company_id=company_id):
        POFinishHandler.push_product_info(instance=po)
    for gr in GoodsReceipt.objects.filter(system_status=3, company_id=company_id):
        GRFinishHandler.push_product_info(instance=gr)
    for gd in GoodsDetail.objects.filter(company_id=company_id):
        gd.push_product_info(instance=gd)
    # output
    for so in SaleOrder.objects.filter(system_status=3, company_id=company_id):
        SOFinishHandler.push_product_info(instance=so)
    for deli_sub in OrderDeliverySub.objects.filter(system_status=3, company_id=company_id):
        DeliFinishHandler.push_product_info(instance=deli_sub)
    # return
    for return_obj in GoodsReturn.objects.filter(system_status=3, company_id=company_id):
        ReturnFinishHandler.push_product_info(instance=return_obj)
    print('reset_and_run_product_info done.')
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
    print('Available list has created', avai_lst)


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
                    doc_obj.save(update_fields=['system_status'])
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
            count +=1
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
        company_count+=1
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
                if data['condition_property']['title'] == 'SaleOrder.status':
                    data['condition_property']['title'] = 'SaleOrder Status'
                elif data['condition_property']['title'] == 'Competitor.Win':
                    data['condition_property']['title'] = 'Competitor Win'
                elif data['condition_property']['title'] == 'SaleOrder.Delivery.Status':
                    data['condition_property']['title'] = 'SaleOrder Delivery Status'
                elif data['condition_property']['title'] == 'Quotation.confirm':
                    data['condition_property']['title'] = 'Quotation Status'
                elif data['condition_property']['title'] == 'Product.Line.Detail':
                    data['condition_property']['title'] = 'Product Line Detail'

                if data['condition_property']['title'] in ['SaleOrder.Delivery.Status', 'SaleOrder Delivery Status']:
                    data['comparison_operator'] = '='
            item.save(update_fields=['condition_datas'])
        print('Done :))')
        return True

    @classmethod
    def update_opp_current_stage(cls):
        for obj in Opportunity.objects.all():
            if obj.check_config_auto_update_stage():
                obj.win_rate, opp_stage_obj = obj.update_stage(obj=obj)
                obj.current_stage = opp_stage_obj.stage
                obj.current_stage_data = {
                    'id': str(obj.current_stage.id),
                    'indicator': obj.current_stage.indicator,
                    'win_rate': obj.current_stage.win_rate
                } if obj.current_stage else {}
                obj.save(update_fields=['win_rate', 'current_stage', 'current_stage_data'])
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


def update_serial_status():
    for pw_serial in ProductWareHouseSerial.objects.filter(is_delete=True):
        pw_serial.serial_status = 1
        pw_serial.save(update_fields=['serial_status'])
    print('update_serial_status done.')


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
                        objs.append(Tax(tenant=company_obj.tenant, company=company_obj, category=vat_tax_category, **item))

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
        if not DocumentType.objects.filter(company = company_obj, tenant = company_obj.tenant, code='BDT001').exists():
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
                "agency": None,
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
    # for ar_invoice in ARInvoice.objects.filter(system_status=3):
    #     ARInvoiceFinishHandler.push_to_payment_plan(instance=ar_invoice)
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


def delete_employee_user():
    employee_objs = Employee.objects.filter(id__in=[
        "b9b84dce-0e37-4f53-85bd-52d0f6db82b3",
        "d64c5a60-bbc5-44c7-a145-4806bb760985",
        "3836328d-429d-4508-a509-60f52999a303"
    ], company_id="0248237b-cb6b-46b1-82ad-9282115a0624")
    if employee_objs:
        employee_objs.delete()
    user_obj = User.objects.filter(id="837f0d6c-9e7c-481d-8ca5-e056c99da188").first()
    if user_obj:
        user_obj.delete()
    print('delete_employee_user done')


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
        "69284eac-b80e-48e4-92a2-6f5f0536d419",
    ])
    if workflows_delete:
        workflows_delete.delete()
    workflow_config_opp = WorkflowConfigOfApp.objects.filter(id="e5706d30-50f3-413f-9a30-312fae49a307").first()
    if workflow_config_opp:
        workflow_config_opp.delete()
    print("hong_quang_delete_workflow done.")
    return True


def hong_quang_delete_sales():
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
