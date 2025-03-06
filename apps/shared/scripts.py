from apps.masterdata.saledata.models.periods import Periods
from apps.core.company.models import Company
from apps.masterdata.saledata.models.product import (
    ProductType, Product, UnitOfMeasure
)
from apps.masterdata.saledata.models.price import (
    UnitOfMeasureGroup
)
from apps.masterdata.saledata.models.accounts import (
    Account, AccountCreditCards, AccountActivity
)
from apps.core.base.models import (
    PlanApplication, ApplicationProperty, Application, SubscriptionPlan
)
from apps.core.tenant.models import Tenant, TenantPlan
from apps.sales.cashoutflow.models import (
    AdvancePaymentCost, PaymentCost
)
from apps.core.workflow.models import (
    WorkflowConfigOfApp, Workflow, Runtime, RuntimeStage, RuntimeAssignee, RuntimeLog
)
from apps.masterdata.saledata.models import (
    ProductWareHouse, ProductWareHouseLot, ProductWareHouseSerial, DocumentType,
    FixedAssetClassificationGroup, FixedAssetClassification,
)
from . import MediaForceAPI, DisperseModel

from .extends.signals import ConfigDefaultData
from .permissions.util import PermissionController
from ..core.attachments.models import Folder
from ..core.hr.models import (
    Employee, Role, EmployeePermission, RolePermission,
)
from ..core.mailer.models import MailTemplateSystem
from ..eoffice.leave.leave_util import leave_available_map_employee
from ..eoffice.leave.models import LeaveAvailable, WorkingYearConfig, WorkingHolidayConfig
from ..hrm.employeeinfo.models import EmployeeHRNotMapEmployeeHRM
from ..masterdata.promotion.models import Promotion
from ..masterdata.saledata.models.product_warehouse import ProductWareHouseLotTransaction
from ..sales.arinvoice.models import ARInvoice, ARInvoiceItems, ARInvoiceDelivery
from ..sales.delivery.models import DeliveryConfig, OrderDeliverySub, OrderDeliveryProduct
from ..sales.delivery.utils import DeliFinishHandler
from ..sales.inventory.models import (
    InventoryAdjustmentItem, GoodsReceipt, GoodsReceiptWarehouse, GoodsReturn
)
from ..sales.inventory.utils import GRFinishHandler, ReturnFinishHandler
from ..sales.lead.models import Lead
from ..sales.opportunity.models import (
    Opportunity, OpportunityConfigStage, OpportunitySaleTeamMember, OpportunityMeeting, OpportunityActivityLogs,
)
from ..sales.partnercenter.models import DataObject
from ..sales.project.models import Project, ProjectMapMember
from ..sales.purchasing.models import (
    PurchaseRequestProduct, PurchaseOrderRequestProduct, PurchaseOrder,
)
from ..sales.purchasing.utils import POFinishHandler
from ..sales.quotation.models import QuotationIndicatorConfig, Quotation
from ..sales.quotation.serializers import QuotationListSerializer
from ..sales.report.models import ReportCashflow
from ..sales.revenue_plan.models import RevenuePlanGroupEmployee
from ..sales.saleorder.models import SaleOrderIndicatorConfig, SaleOrder
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
    runtime = Runtime.objects.filter(doc_id=doc_id)
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

