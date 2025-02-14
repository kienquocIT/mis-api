from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from apps.masterdata.saledata.models.periods import Periods
from apps.core.company.models import Company, CompanyFunctionNumber, CompanyBankAccount
from apps.masterdata.saledata.models.product import (
    ProductType, Product, ExpensePrice, ProductCategory, UnitOfMeasure,
    Expense,
)
from apps.masterdata.saledata.models.price import (
    TaxCategory, Currency, Price, UnitOfMeasureGroup, Tax, ProductPriceList, PriceListCurrency,
)
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import AccountType, Account, AccountCreditCards, AccountActivity

from apps.core.base.models import (
    PlanApplication, ApplicationProperty, Application, SubscriptionPlan, City, Currency as BaseCurrency
)
from apps.core.tenant.models import Tenant, TenantPlan
from apps.sales.cashoutflow.models import (
    AdvancePayment, AdvancePaymentCost,
    ReturnAdvance, ReturnAdvanceCost,
    Payment, PaymentCost
)
from apps.core.workflow.models import WorkflowConfigOfApp, Workflow, Runtime, RuntimeStage, RuntimeAssignee, RuntimeLog
from apps.masterdata.saledata.models import (
    ConditionLocation, FormulaCondition, ShippingCondition, Shipping,
    ProductWareHouse, ProductWareHouseLot, ProductWareHouseSerial, SubPeriods, DocumentType,
)
from misapi.asgi import application
from . import MediaForceAPI, DisperseModel

from .extends.signals import SaleDefaultData, ConfigDefaultData
from .permissions.util import PermissionController
from ..accounting.accountingsettings.models import ChartOfAccounts, DefaultAccountDefinition
from ..core.attachments.models import Folder
from ..core.hr.models import (
    Employee, Role, EmployeePermission, PlanEmployeeApp, PlanEmployee, RolePermission,
    PlanRole, PlanRoleApp,
)
from ..core.mailer.models import MailTemplateSystem
from ..eoffice.leave.leave_util import leave_available_map_employee
from ..eoffice.leave.models import LeaveAvailable, WorkingYearConfig, WorkingHolidayConfig
from ..eoffice.meeting.models import MeetingSchedule
from ..hrm.employeeinfo.models import EmployeeHRNotMapEmployeeHRM
from ..masterdata.promotion.models import Promotion
from ..masterdata.saledata.models.product_warehouse import ProductWareHouseLotTransaction
from ..masterdata.saledata.serializers import PaymentTermListSerializer
from ..sales.acceptance.models import FinalAcceptanceIndicator
from ..sales.arinvoice.models import ARInvoice
from ..sales.delivery.models import DeliveryConfig, OrderDeliverySub, OrderDeliveryProduct
from ..sales.delivery.utils import DeliFinishHandler, DeliHandler
from ..sales.delivery.serializers.delivery import OrderDeliverySubUpdateSerializer
from ..sales.distributionplan.models import DistributionPlan
from ..sales.financialcashflow.models import CashInflow
from ..sales.financialcashflow.views import CashInflowList
from ..sales.inventory.models import InventoryAdjustmentItem, GoodsReceiptRequestProduct, GoodsReceipt, \
    GoodsReceiptWarehouse, GoodsReturn, GoodsIssue, GoodsTransfer, GoodsReturnSubSerializerForNonPicking, \
    GoodsReturnProductDetail, GoodsReceiptLot, InventoryAdjustment, GoodsDetail
from ..sales.inventory.serializers.goods_detail import GoodsDetailListSerializer
from ..sales.inventory.utils import GRFinishHandler, ReturnFinishHandler, GRHandler
from ..sales.lead.models import LeadHint, LeadStage, Lead
from ..sales.opportunity.models import (
    Opportunity, OpportunityConfigStage, OpportunityStage, OpportunityCallLog,
    OpportunitySaleTeamMember, OpportunityDocument, OpportunityMeeting, OpportunityEmail, OpportunityActivityLogs,
)
from ..sales.opportunity.serializers import CommonOpportunityUpdate
from ..sales.partnercenter.models import DataObject
from ..sales.project.models import Project, ProjectMapMember
from ..sales.purchasing.models import PurchaseRequestProduct, PurchaseRequest, PurchaseOrderProduct, \
    PurchaseOrderRequestProduct, PurchaseOrder, PurchaseOrderPaymentStage
from ..sales.purchasing.utils import POFinishHandler
from ..sales.quotation.models import QuotationIndicatorConfig, Quotation, QuotationIndicator, QuotationAppConfig
from ..sales.quotation.serializers import QuotationListSerializer
from ..sales.quotation.utils.logical_finish import QuotationFinishHandler
from ..sales.reconciliation.models import Reconciliation, ReconciliationItem
from ..sales.report.inventory_log import ReportInvCommonFunc
from ..sales.report.models import ReportRevenue, ReportPipeline, ReportStockLog, ReportCashflow, \
    ReportInventoryCost, ReportInventoryCostLatestLog, ReportStock, BalanceInitialization
from ..sales.report.serializers import BalanceInitializationCreateSerializer
from ..sales.revenue_plan.models import RevenuePlanGroupEmployee
from ..sales.saleorder.models import SaleOrderIndicatorConfig, SaleOrderProduct, SaleOrder, SaleOrderIndicator, \
    SaleOrderAppConfig, SaleOrderPaymentStage
from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer
from ..sales.saleorder.utils import SOFinishHandler
from ..sales.task.models import OpportunityTaskStatus, OpportunityTask
from ..sales.production.models import BOM


def update_sale_default_data_old_company():
    for company_obj in Company.objects.all():
        SaleDefaultData(company_obj=company_obj)()


def delete_all_product_type():
    for product_type_obj in ProductType.objects.all():
        product_type_obj.delete()


def delete_all_tax_category():
    for tax_category_obj in TaxCategory.objects.all():
        tax_category_obj.delete()


def delete_all_currency():
    for currency_obj in Currency.objects.all():
        currency_obj.delete()


def delete_all_price():
    for price_obj in Price.objects.all():
        price_obj.delete()


def delete_all_product():
    for product_obj in Product.objects.all():
        product_obj.delete()


def delete_wrong_contact():
    try:
        obj = Contact.objects.get(id='44dfcf1c06924e348819df692a11206a')
        obj.delete()
    except Contact.DoesNotExist:
        pass


def delete_all_account_types():
    try:
        AccountType.objects.filter(company_id='560bcfd8bfdb4f48b8d258c5f9e66320').delete()
        return True
    except AccountType.DoesNotExist:
        return False


def create_default_account_types():
    account_types_data = [
        {'title': 'Customer', 'code': 'AT001', 'is_default': 1, 'account_type_order': 0},
        {'title': 'Supplier', 'code': 'AT002', 'is_default': 1, 'account_type_order': 1},
        {'title': 'Partner', 'code': 'AT003', 'is_default': 1, 'account_type_order': 2},
        {'title': 'Competitor', 'code': 'AT004', 'is_default': 1, 'account_type_order': 3}
    ]
    bulk_info = []
    for item in account_types_data:
        bulk_info.append(
            AccountType(
                title=item['title'],
                code=item['code'],
                is_default=1,
                account_type_order=item['account_type_order'],
                tenant_id='a86a8871520945fc8e3c44179e2d70d9',
                company_id='560bcfd8bfdb4f48b8d258c5f9e66320'
            )
        )
    if len(bulk_info) > 0:
        AccountType.objects.bulk_create(bulk_info)
    return True


def delete_data_old():
    delete_wrong_contact()
    delete_all_product_type()
    delete_all_tax_category()
    delete_all_currency()
    delete_all_price()
    delete_all_product()


def delete_data_shipping():
    ConditionLocation.objects.all().delete()
    FormulaCondition.objects.all().delete()
    ShippingCondition.objects.all().delete()
    Shipping.objects.all().delete()
    return True


def update_account_annual_revenue():
    Account.objects.all().update(annual_revenue=1)
    return True


def update_account_total_employees():
    Account.objects.all().update(total_employees=1)
    return True


def update_account_shipping_address():
    Account.objects.all().update(shipping_address=[])
    return True


def update_account_billing_address():
    Account.objects.all().update(billing_address=[])
    return True


def delete_all_ap():
    AdvancePayment.objects.all().delete()
    AdvancePaymentCost.objects.all().delete()
    return True


def delete_all_payment():
    Payment.objects.all().delete()
    PaymentCost.objects.all().delete()
    return True


def delete_all_return():
    ReturnAdvance.objects.all().delete()
    ReturnAdvanceCost.objects.all().delete()
    return True


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


def make_sure_opportunity_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).opportunity_config()
    print('Make sure opportunity is done!')


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


def update_data_application_property():
    app_property = ApplicationProperty.objects.get(id='b5aa8550-7fc5-4cb8-a952-b6904b2599e5')
    app_property.stage_compare_data = {
        '=': [
            {
                'id': 0,
                'value': None,
            }
        ],
        '?': [
            {
                'id': 0,
                'value': None,
            }
        ]
    }
    app_property.save()
    print('Update Done!')


def make_sure_sale_order_indicator_config():
    SaleOrderIndicatorConfig.objects.all().delete()
    for obj in Company.objects.all():
        ConfigDefaultData(obj).sale_order_indicator_config()
    print('Make sure sale order indicator config is done!')


def update_stage_for_opportunity():
    opp = Opportunity.objects.filter(stage=None)
    bulk_data = []
    for obj in opp:
        stage = OpportunityConfigStage.objects.get(company_id=obj.company_id, indicator='Qualification')
        bulk_data.append(OpportunityStage(opportunity=obj, stage=stage, is_current=True))
    OpportunityStage.objects.bulk_create(bulk_data)
    print('!Done')


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


def update_fk_expense_price():
    expense_price = ExpensePrice.objects.select_related('expense_general').all()
    for item in expense_price:
        item.expense = item.expense_general.expense
        item.save()
    print('!Done')


def update_fk_expense_price_expense_general():
    expense_price = ExpensePrice.objects.select_related('expense_general').all()
    for item in expense_price:
        item.expense_general = None
        item.save()
    print('!Done')


def edit_uom_group_field_to_default():
    UnitOfMeasureGroup.objects.filter(title='Labor').update(is_default=1)
    UnitOfMeasureGroup.objects.filter(title='Nhân công').update(is_default=1)
    for item in UnitOfMeasure.objects.filter(rounding=0):
        item.rounding = 4
        item.save()
    return True


def delete_all_opportunity_call_log():
    OpportunityCallLog.objects.all().delete()
    return True


def make_sure_task_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).task_config()
    print('Make sure Task config is done!')


def update_win_rate_delivery_stage():
    opps = Opportunity.objects.all()
    for opp in opps:
        for stage in opp.stage.all():
            if stage.indicator == 'Delivery':
                opp.win_rate = 100
                opp.save()

    OpportunityConfigStage.objects.filter(indicator='Delivery').update(win_rate=100)
    print('Done!')


def update_plan_application_quotation():
    PlanApplication.objects.filter(
        application_id="eeab5d9e-54c6-4e85-af75-477b740d7523"
    ).delete()
    Application.objects.filter(id="eeab5d9e-54c6-4e85-af75-477b740d7523").delete()
    print("update done.")
    return True


def update_data_product_inventory(product):
    if len(product.inventory_information) != 0:
        if isinstance(product.inventory_information['uom'], str):
            obj_currency = UnitOfMeasure.objects.get(id=product.inventory_information['uom'])
            product.inventory_information['uom'] = {
                'id': obj_currency.id,
                'code': obj_currency.code,
                'title': obj_currency.title,
                'abbreviation': obj_currency.abbreviation
            }
            product.inventory_uom_id = product.inventory_information['uom']
        else:
            product.inventory_uom_id = product.inventory_information[
                'uom']['id'] if 'uom' in product.inventory_information and product.inventory_information[
                'uom'] is not None else None
        product.inventory_level_min = product.inventory_information['inventory_level_min']
        product.inventory_level_max = product.inventory_information['inventory_level_max']
        return True
    return False


def update_data_product_sale(product):
    if len(product.sale_information) != 0:
        if isinstance(product.sale_information['default_uom'], str):
            obj_uom = UnitOfMeasure.objects.get(id=product.sale_information['default_uom'])
            product.sale_information['default_uom'] = {
                'id': obj_uom.id,
                'code': obj_uom.code,
                'title': obj_uom.title
            }
            product.default_uom_id = obj_uom.id
        else:
            product.default_uom_id = product.sale_information[
                'default_uom']['id'] if 'default_uom' in product.sale_information and product.sale_information[
                'default_uom'] is not None else None

        if isinstance(product.sale_information['tax_code'], str):
            obj_tax = Tax.objects.get(id=product.sale_information['tax_code'])
            product.sale_information['tax_code'] = {
                'id': obj_tax.id,
                'code': obj_tax.code,
                'title': obj_tax.title
            }
            product.tax_code_id = obj_tax.id
        else:
            product.tax_code_id = product.sale_information[
                'tax_code']['id'] if 'tax_code' in product.sale_information and product.sale_information[
                'tax_code'] is not None else None

        if isinstance(product.sale_information['currency_using'], str):
            obj_currency = Currency.objects.get(id=product.sale_information['currency_using'])
            product.sale_information['currency_using'] = {
                'id': obj_currency.id,
                'code': obj_currency.code,
                'title': obj_currency.title
            }
            product.currency_using_id = product.sale_information['currency_using']
        else:
            product.currency_using_id = product.sale_information[
                'currency_using']['id'] if 'currency_using' in product.sale_information and \
                                           product.sale_information['currency_using'] is not None else None

        product.length = product.sale_information['length'] if 'length' in product.sale_information else None
        product.width = product.sale_information['width'] if 'width' in product.sale_information else None
        product.height = product.sale_information['height'] if 'height' in product.sale_information else None
        return True
    return False


def update_data_product():
    Product.objects.filter(
        company_id__in=['5e56aa92c9e044779ac744883ac7e901', '5052f1d6c1f1409f96e586e048f19319']
    ).delete()
    products = Product.objects.all()
    for product in products:

        if isinstance(product.general_information['product_type'], str):
            obj_product_type = ProductType.objects.get(id=product.general_information['product_type'])
            product.general_information['product_type'] = {
                'id': obj_product_type.id,
                'code': obj_product_type.code,
                'title': obj_product_type.title
            }
            product.product_type_id = obj_product_type.id
        else:
            product.product_type_id = product.general_information['product_type']['id']

        if isinstance(product.general_information['product_category'], str):
            obj_product_category = ProductCategory.objects.get(id=product.general_information['product_category'])
            product.general_information['product_category'] = {
                'id': obj_product_category.id,
                'code': obj_product_category.code,
                'title': obj_product_category.title
            }
            product.product_category_id = obj_product_category.id
        else:
            product.product_category_id = product.general_information['product_category']['id']

        if isinstance(product.general_information['uom_group'], str):
            obj_uom_group = ProductCategory.objects.get(id=product.general_information['uom_group'])
            product.general_information['uom_group'] = {
                'id': obj_uom_group.id,
                'code': obj_uom_group.code,
                'title': obj_uom_group.title
            }
            product.uom_group_id = obj_uom_group.id
        else:
            product.uom_group_id = product.general_information['uom_group']['id']
        is_sale = update_data_product_sale(product)
        is_inventory = update_data_product_inventory(product)
        list_option = []
        if is_sale:
            list_option.append(0)
        if is_inventory:
            list_option.append(1)
        product.product_choice = list_option
        product.save()

    print('Done !')


def make_full_plan():
    TenantPlan.objects.all().delete()
    plan_objs = SubscriptionPlan.objects.all()
    for tenant in Tenant.objects.all():
        for plan in plan_objs:
            TenantPlan.objects.create(tenant=tenant, plan=plan, is_limited=False)
    print('Make full plan is successfully!')


def update_data_sale_order_product():
    objs = SaleOrderProduct.objects.all()
    for obj in objs:
        obj.remain_for_purchase_request = obj.product_quantity
        obj.save()
    print('Done!')


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


def update_data_product_of_purchase_request():
    for pr_product in PurchaseRequestProduct.objects.all():
        pr_product.remain_for_purchase_order = pr_product.quantity
        pr_product.save()
    print('Update Done!')


def make_sure_function_process_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).process_function_config()
    print('Make sure function process config is done!')


def make_sure_process_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).process_config()
    print('Make sure process config is done!')


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


def update_data_shipping():
    for obj in Shipping.objects.all():
        conditions = obj.formula_condition
        list_condition = []
        for condition in conditions:
            list_location = []
            for location in condition['location']:
                loc = City.objects.get(id=location)
                list_location.append(
                    {
                        'id': location,
                        'title': loc.title
                    }
                )
            list_condition.append(
                {
                    'location': list_location,
                    'formula': condition['formula']
                }
            )
        obj.formula_condition = list_condition
        obj.save()
    print('Done')


def update_employee_inherit_opportunity():
    opps = Opportunity.objects.all()
    for opp in opps:
        opp.employee_inherit = opp.sale_person
        opp.save()
    print('!Done')


def update_uom_group_uom_reference():
    for uom in UnitOfMeasure.objects.filter(is_referenced_unit=True):
        uom.group.uom_reference = uom
        uom.group.save(update_fields=['uom_reference'])
    print('update done.')


def update_product_size_for_inventory():
    for obj in Product.objects.all():
        if 1 in obj.product_choice:
            obj.height = 10
            obj.length = 10
            obj.width = 10
            obj.volume = {
                "id": "68305048-03e2-4936-8f4b-f876fcc6b14e",
                "title": "volume",
                "value": 1000.0,
                "measure": "cm³"
            }
            obj.weight = {
                "id": "4db94461-ba4b-4d5e-b9b1-1481ea38591d",
                "title": "weight",
                "value": 10.0,
                "measure": "gram"

            }
            obj.save()
        else:
            obj.height = None
            obj.length = None
            obj.width = None
            obj.volume = {}
            obj.weight = {}
            obj.save()
        return True


def delete_old_m2m_data_price_list_product():
    today = date.today()
    ProductPriceList.objects.filter(date_created__lt=today).delete()
    return True


def update_currency_price_list():
    prices = Price.objects.all()
    bulk_data = []
    for price in prices:
        for currency in price.currency:
            obj = PriceListCurrency(
                currency_id=currency,
                price=price
            )
            bulk_data.append(obj)

    PriceListCurrency.objects.bulk_create(bulk_data)
    print('Update Done')


def update_employee_created_purchase_request():
    PurchaseRequest.objects.all().update(employee_created='c559833d-ccb8-40dc-a7bb-84ef047beb36')
    print('Update Done')


def update_opportunity_contact_role_datas():
    opps = Opportunity.objects.all()

    for opp in opps:
        list_data = []
        for data in opp.opportunity_contact_role_datas:
            obj_contact = Contact.objects.get(id=data['contact']['id'])
            list_data.append(
                {
                    'type_customer': data['type_customer'],
                    'role': data['role'],
                    'job_title': data['job_title'],
                    'contact': {
                        'id': str(obj_contact.id),
                        'fullname': obj_contact.fullname,
                    }
                }
            )
        opp.opportunity_contact_role_datas = list_data
        opp.save()

    print('Update Done')


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


def clear_data_expense():
    Expense.objects.all().delete()
    print('Delete Done')


def update_employee_inherit_return_advance():
    objs = ReturnAdvance.objects.all()
    for advance_return in objs:
        advance_return.employee_inherit = advance_return.creator
        advance_return.employee_created = advance_return.creator
        advance_return.save()
    print('Update done')


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


def make_sure_function_purchase_request_config():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).purchase_request_config()
    print('Make sure function purchase_request_config is done!')


def update_sale_person_opportunity():
    opps = Opportunity.objects.filter(sale_person=None)
    for opp in opps:
        opp.sale_person_id = 'c559833dccb840dca7bb84ef047beb36'
        opp.employee_inherit_id = 'c559833dccb840dca7bb84ef047beb36'
        opp.employee_created_id = 'c559833dccb840dca7bb84ef047beb36'
        opp.save(update_fields=['sale_person_id', 'employee_inherit_id', 'employee_created_id'])
    print('Update Done!')


def update_tenant_for_sub_table_opp():
    members = OpportunitySaleTeamMember.objects.all()
    for member in members:
        member.company = member.opportunity.company
        member.tenant = member.opportunity.tenant
        member.save()
    print('Update Done!')


def update_tenant_for_sub_table_inventory_adjustment():
    objs = InventoryAdjustmentItem.objects.all()
    for obj in objs:
        obj.company = obj.inventory_adjustment_mapped.company
        obj.tenant = obj.inventory_adjustment_mapped.tenant
        obj.save()
    print('Update Done!')


def update_quantity_remain_pr_product():
    for pr_product in PurchaseRequestProduct.objects.all():
        pr_product.remain_for_purchase_order = pr_product.quantity
        pr_product.save(update_fields=['remain_for_purchase_order'])
    print('update done.')


def update_tenant_for_sub_table_purchase_request():
    objs = PurchaseRequestProduct.objects.all()
    for obj in objs:
        obj.company = obj.purchase_request.company
        obj.tenant = obj.purchase_request.tenant
        obj.save()
    print('Update Done!')


def update_employee_inherit_and_created_return_advance():
    objs = ReturnAdvance.objects.all()
    for obj in objs:
        obj.employee_inherit = obj.beneficiary
        obj.employee_created = obj.creator
        obj.save()
    print('Update Done!')


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


def update_backup_data_purchase_request():
    for pr in PurchaseRequest.objects.all():
        data = []

        for item in pr.purchase_request_product_datas:
            product_obj = Product.objects.get(id=item['product']['id'])
            data_product = {
                'id': str(product_obj.id),
                'title': product_obj.title,
                'code': product_obj.code,
                'uom_group': str(product_obj.general_uom_group_id),
            }

            tax_obj = Tax.objects.get(id=item['tax']['id'])
            data_tax = {
                'id': str(tax_obj.id),
                'title': tax_obj.title,
                'rate': tax_obj.rate,
            }
            data.append(
                {
                    'tax': data_tax,
                    'product': data_product,
                    'uom': item['uom'],
                    'description': item['description'],
                    'unit_price': item['unit_price'],
                    'sale_order_product': item['sale_order_product'],
                    'quantity': item['quantity'],
                    'sub_total_price': item['unit_price'] * item['quantity'],
                }
            )

        pr.purchase_request_product_datas = data
        pr.save(update_fields=['purchase_request_product_datas'])
    print('Update Done !')


def update_title_opportunity_document():
    for item in OpportunityDocument.objects.all():
        item.title = item.subject
        item.tenant = item.opportunity.tenant
        item.company = item.opportunity.company
        item.save(update_fields=['title', 'tenant', 'company'])
    print('Update Done !')


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


def update_company_setting():
    vnd_currency = BaseCurrency.objects.filter(code='VND').first()
    for company_obj in Company.objects.all():
        if vnd_currency:
            company_obj.definition_inventory_valuation = 0
            company_obj.default_inventory_value_method = 0
            company_obj.cost_per_warehouse = True
            company_obj.cost_per_lot = False
            company_obj.cost_per_project = False
            company_obj.primary_currency_id = str(vnd_currency.id)
            company_obj.save(update_fields=[
                'definition_inventory_valuation',
                'default_inventory_value_method',
                'cost_per_warehouse',
                'cost_per_lot',
                'cost_per_project',
                'primary_currency_id'
            ])
    return True


def create_company_function_number():
    company_function_number_data = [
        {
            'numbering_by': 0,
            'schema': None,
            'schema_text': None,
            'first_number': None,
            'last_number': None,
            'reset_frequency': None
        }
    ]
    company_list = Company.objects.all()
    bulk_create_data = []
    for company_obj in company_list:
        for function_index in range(10):
            for cf_item in company_function_number_data:
                bulk_create_data.append(
                    CompanyFunctionNumber(
                        company=company_obj,
                        function=function_index,
                        **cf_item
                    )
                )
    CompanyFunctionNumber.objects.all().delete()
    CompanyFunctionNumber.objects.bulk_create(bulk_create_data)
    return True


def delete_payment_return():
    for ap_cost_item in AdvancePaymentCost.objects.all():
        ap_cost_item.sum_converted_value = 0
        ap_cost_item.sum_return_value = 0
        ap_cost_item.save()
    PaymentCost.objects.all().delete()
    Payment.objects.all().delete()
    ReturnAdvanceCost.objects.all().delete()
    ReturnAdvance.objects.all().delete()
    return True


def update_product_general_price():
    for item in Product.objects.all():
        general_product_price = item.product_price_product.filter(price_list__is_default=True).first()
        if general_product_price:
            item.sale_price = general_product_price.price
            item.save()
    return True


def update_payment_cost():
    for item in PaymentCost.objects.all():
        item.opportunity = item.payment.opportunity
        item.quotation_mapped = item.payment.quotation_mapped
        item.sale_order_mapped = item.payment.sale_order_mapped
        item.save()
    print('update done')


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


def fool_data_for_revenue_dashboard():
    a = ReportRevenue.objects.get(sale_order_id='93d99efb0a774f9eb6bf65cc336b3719')
    a.date_approved = datetime(2023, 1, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='872e13cef5bb45bb926bf12f02f71c59')
    a.date_approved = datetime(2023, 2, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='a67b2165945c4b688a96deb723fe987d')
    a.date_approved = datetime(2023, 3, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='3cd1d6923a2b4ee88926c4ed1e989f53')
    a.date_approved = datetime(2023, 4, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='8fcdde7909294d0d8da9f2e9831da35a')
    a.date_approved = datetime(2023, 5, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='7255f876b3ba4a2286ad794a15f81529')
    a.date_approved = datetime(2023, 6, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='a2e1a7e6063845878395d155a5f9a46b')
    a.date_approved = datetime(2023, 7, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='0411b2d39e144b4d8857d2cff1f89421')
    a.date_approved = datetime(2023, 8, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='d2d1accca98148aa8b84749339b29eda')
    a.date_approved = datetime(2023, 12, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='bc5588ef0e0d4d50b638050ec1ac8d1c')
    a.date_approved = datetime(2023, 9, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='dec3a0d5ff70442094653fec759e40c5')
    a.date_approved = datetime(2023, 10, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='fe8ac8c8cd1e4b0c84501d4b14e6ed92')
    a.date_approved = datetime(2023, 12, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='235b1253d41d4a6085366980ddd3cdf5')
    a.date_approved = datetime(2023, 11, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='fa79eff12e154085969cf92a06a3c5be')
    a.date_approved = datetime(2023, 9, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='c8c47118ab1a41d6a3b94cef88b818af')
    a.date_approved = datetime(2023, 12, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='5f59d221a2754970bccd1e2eee739180')
    a.date_approved = datetime(2023, 10, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='1837ed70ebe94ace818299e80a77674f')
    a.date_approved = datetime(2023, 7, 1)
    a.save()
    a = ReportRevenue.objects.get(sale_order_id='26d3ea7512ad439b8e1216f614ae24e2')
    a.date_approved = datetime(1900, 5, 1)
    a.save()
    print('Update report data done!')
    b = Periods.objects.filter(code='P2023')
    if b.exists():
        obj = b.first()
        obj.start_date = datetime(2023, 1, 1)
        obj.fiscal_year = 2023
        obj.save()
        print('Update period data done!')


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


def update_price_list():
    bulk_info = []
    for item in Price.objects.all():
        for cr_id in item.currency:
            bulk_info.append(
                PriceListCurrency(price=item, currency_id=cr_id)
            )
    PriceListCurrency.objects.all().delete()
    PriceListCurrency.objects.bulk_create(bulk_info)
    print('Done')


def reset_and_run_product_info():
    # reset
    update_fields = ['stock_amount', 'wait_delivery_amount', 'wait_receipt_amount', 'available_amount']
    for product in Product.objects.all():
        product.stock_amount = 0
        product.wait_delivery_amount = 0
        product.wait_receipt_amount = 0
        product.available_amount = 0
        product.save(update_fields=update_fields)
    # set input, output, return
    # input
    for po in PurchaseOrder.objects.filter(system_status=3):
        POFinishHandler.push_product_info(instance=po)
    for gr in GoodsReceipt.objects.filter(system_status=3):
        GRFinishHandler.push_product_info(instance=gr)
    # output
    for so in SaleOrder.objects.filter(system_status=3):
        SOFinishHandler.push_product_info(instance=so)
    for deli_sub in OrderDeliverySub.objects.all():
        DeliFinishHandler.push_product_info(instance=deli_sub)
    # return
    for return_obj in GoodsReturn.objects.filter(system_status=3):
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


def reset_opportunity_stage():
    for opp in Opportunity.objects.all():
        CommonOpportunityUpdate.update_opportunity_stage_for_list(opp)
    print('Done')


def update_report_stock_sub_trans_title():
    for item in ReportStockLog.objects.all():
        if item.trans_code.startswith('D'):
            item.trans_title = 'Delivery'
            item.save(update_fields=['trans_title'])
        elif item.trans_code.startswith('GR'):
            item.trans_title = 'Goods receipt'
            item.save(update_fields=['trans_title'])
    print('Done')


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


def update_goods_return_items_nt():
    data = [
        {
            'id': '26199d0c4ebb41199f13a5d215885c2f',
            'prd': 'b01be7a525624897bb2226403f32c808',
            'wh': 'bbac9cfcdf1b4ed497c9a57ac5c94f89',
            'uom': '08dacbd30deb479b8118702e800ca1e3'
        },
        {
            'id': '1dc2a55dbdfb47e4bad7509a9d9f9984',
            'prd': '567d869256f34fb5881513dae765e763',
            'wh': 'bbac9cfcdf1b4ed497c9a57ac5c94f89',
            'uom': '08dacbd30deb479b8118702e800ca1e3'
        },
        {
            'id': 'ff1cf130f20e4eccb12c7031195608ba',
            'prd': '52e45d5bd91e4c048b2d7a09ee4820dd',
            'wh': 'bbac9cfcdf1b4ed497c9a57ac5c94f89',
            'uom': '1366ad1e2ac64a959118701b8b68fb5c'
        },
        {
            'id': 'fd9169186424438087557a89efb037a5',
            'prd': '317352890a2b4ae29e2d0940bc1010ec',
            'wh': 'bbac9cfcdf1b4ed497c9a57ac5c94f89',
            'uom': '1366ad1e2ac64a959118701b8b68fb5c'
        }
    ]

    run_update_pw_uom_base(run_type=1, product_id="567d8692-56f3-4fb5-8815-13dae765e763")
    for item in data:
        obj = GoodsReturnProductDetail.objects.get(id=item.get('id'))
        obj.product_id = item.get('prd')
        obj.return_to_warehouse_id = item.get('wh')
        obj.uom_id = item.get('uom')
        obj.save(update_fields=['product_id', 'return_to_warehouse_id', 'uom_id'])

    GoodsReturn.objects.filter(id='b4a0f779-c326-4283-94b0-241c9438b9b6').delete()
    ProductWareHouse.objects.filter(id__in=[
        '9b5817285f13406f9c3399ab88bd8f2e',
        'efd096351225461ca247e22ff444aa68',
        'aac5e1c2498d4cbbb438e2aa2e3004c2'
    ]).delete()
    pro_wd_CHIVAS25 = ProductWareHouse.objects.filter(id='328ae65745644a66b90fb18e76dd2737').first()
    if pro_wd_CHIVAS25:
        pro_wd_CHIVAS25.stock_amount = 21
        pro_wd_CHIVAS25.receipt_amount = 39
        pro_wd_CHIVAS25.sold_amount = 17
        pro_wd_CHIVAS25.picked_ready = 0
        pro_wd_CHIVAS25.uom_id = '08dacbd3-0deb-479b-8118-702e800ca1e3'
        pro_wd_CHIVAS25.save(update_fields=['stock_amount', 'receipt_amount', 'sold_amount', 'picked_ready', 'uom_id'])

    # OKSS
    prd = Product.objects.filter(id='9e41fb1a75764ee885ee962217b7fc4f').first()
    if prd:
        prd.stock_amount = 1
        prd.available_amount = -7
        prd.save(update_fields=['stock_amount', 'available_amount'])
    # ROYAL24
    prd = Product.objects.filter(id='567d8692-56f3-4fb5-8815-13dae765e763').first()
    if prd:
        prd.stock_amount = 5
        prd.available_amount = 3
        prd.save(update_fields=['stock_amount', 'available_amount'])
    # CHIVAS25
    prd = Product.objects.filter(id='b01be7a5-2562-4897-bb22-26403f32c808').first()
    if prd:
        prd.stock_amount = 21
        prd.available_amount = 19
        prd.save(update_fields=['stock_amount', 'available_amount'])

    obj = GoodsReturnProductDetail.objects.get(id='ff1cf130f20e4eccb12c7031195608ba')
    obj.delivery_item_id = '46e392194101478186ade7416fbbea65'
    obj.save(update_fields=['delivery_item_id'])
    print('Done')


def load_hint():
    LeadHint.objects.all().delete()
    for opp in Opportunity.objects.all():
        LeadHint.objects.filter(opportunity=opp).delete()
        bulk_info = []
        for contact_role in opp.opportunity_contact_role_opportunity.all():
            contact = contact_role.contact
            bulk_info.append(
                LeadHint(
                    opportunity_id=opp.id,
                    contact_mobile=contact.mobile,
                    contact_phone=contact.phone,
                    contact_email=contact.email,
                    contact_id=str(contact.id)
                )
            )
        LeadHint.objects.bulk_create(bulk_info)
    print('Done')


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


def update_product_type_default_data():
    ProductType.objects.filter(title='Sản phẩm', is_default=1).update(
        code='goods', title='Hàng hóa', is_default=1, is_goods=1
    )
    ProductType.objects.filter(title='Bán thành phẩm', is_default=1).update(
        code='finished_goods', title='Thành phẩm', is_default=1, is_finished_goods=1
    )
    ProductType.objects.filter(title='Nguyên vật liệu', is_default=1).update(
        code='material', title='Nguyên vật liệu', is_default=1, is_material=1
    )
    ProductType.objects.filter(title='Dịch vụ', is_default=1).update(
        code='asset_tool', title='Tài sản - Công cụ dụng cụ', is_default=1, is_asset_tool=1
    )
    return True


def add_product_type_service():
    for company in Company.objects.all():
        if not ProductType.objects.filter(
            code='service',
            title='Dịch vụ',
            is_default=1,
            is_service=1,
            company=company,
            tenant=company.tenant
        ).exists():
            ProductType.objects.create(
                code='service',
                title='Dịch vụ',
                is_default=1,
                is_service=1,
                company=company,
                tenant=company.tenant
            )
    return True


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


def update_data_json_cash_outflow():
    for ap in AdvancePayment.objects.all():
        for item in ap.advance_payment.all():
            if item.expense_type:
                expense_type = item.expense_type
                item.expense_type_data = {
                    'id': str(expense_type.id),
                    'code': expense_type.code,
                    'title': expense_type.title
                }
            if item.expense_tax:
                expense_tax = item.expense_tax
                item.expense_tax_data = {
                    'id': str(expense_tax.id),
                    'code': expense_tax.code,
                    'title': expense_tax.title,
                    'rate': expense_tax.rate
                } if expense_tax else {}
            item.save(update_fields=['expense_type_data', 'expense_tax_data'])
    print('Done Advance Payment :))')
    for payment in Payment.objects.all():
        for item in payment.payment.all():
            if item.expense_type:
                expense_type = item.expense_type
                item.expense_type_data = {
                    'id': str(expense_type.id),
                    'code': expense_type.code,
                    'title': expense_type.title
                }
            if item.expense_tax:
                expense_tax = item.expense_tax
                item.expense_tax_data = {
                    'id': str(expense_tax.id),
                    'code': expense_tax.code,
                    'title': expense_tax.title,
                    'rate': expense_tax.rate
                } if expense_tax else {}
            item.save(update_fields=['expense_type_data', 'expense_tax_data'])
    print('Done Payment :))')
    for return_ap in ReturnAdvance.objects.all():
        for item in return_ap.return_advance.all():
            if item.expense_type:
                expense_type = item.expense_type
                item.expense_type_data = {
                    'id': str(expense_type.id),
                    'code': expense_type.code,
                    'title': expense_type.title
                }
            item.save(update_fields=['expense_type_data'])
    print('Done Return Payment :))')


def update_datetime_for_meeting_eoffice():
    for meeting in MeetingSchedule.objects.all():
        start_date = meeting.meeting_start_date
        start_time = meeting.meeting_start_time
        duration = meeting.meeting_duration
        if start_date and start_time and duration:
            meeting.meeting_start_datetime = datetime.combine(start_date, start_time)
            meeting.meeting_end_datetime = meeting.meeting_start_datetime + timedelta(minutes=duration)
        meeting.save(update_fields=['meeting_start_datetime', 'meeting_end_datetime'])
    print('Done :))')


def update_account_type_flag():
    for account in Account.objects.all():
        for item in account.account_account_types_mapped.all():
            if item.account_type.account_type_order == 0:
                account.is_customer_account = True
            elif item.account_type.account_type_order == 1:
                account.is_supplier_account = True
            elif item.account_type.account_type_order == 2:
                account.is_partner_account = True
            elif item.account_type.account_type_order == 3:
                account.is_competitor_account = True
            account.save(update_fields=[
                'is_customer_account', 'is_supplier_account', 'is_partner_account', 'is_competitor_account'
            ])
            print(f'--- Updated for {account.name} successfully!')
    print('Done :))')


def update_inventory_adjustment_item_json_data():
    for ia in InventoryAdjustment.objects.all():
        for item in ia.inventory_adjustment_item_mapped.all():
            item.product_mapped_data = {
                'id': str(item.product_mapped.id),
                'code': item.product_mapped.code,
                'title': item.product_mapped.title,
                'description': item.product_mapped.description,
                'general_traceability_method': item.product_mapped.general_traceability_method
            } if item.product_mapped else {}
            item.uom_mapped_data = {
                'id': str(item.uom_mapped.id),
                'code': item.uom_mapped.code,
                'title': item.uom_mapped.title,
                'ratio': item.uom_mapped.ratio
            } if item.uom_mapped else {}
            item.warehouse_mapped_data = {
                'id': str(item.warehouse_mapped.id),
                'code': item.warehouse_mapped.code,
                'title': item.warehouse_mapped.title
            } if item.warehouse_mapped else {}
            item.save(update_fields=['product_mapped_data', 'uom_mapped_data', 'warehouse_mapped_data'])
    print('Done :))')


def update_goods_issue_item_json_data():
    for gis in GoodsIssue.objects.all():
        for item in gis.goods_issue_product.all():
            item.product_data = {
                'id': str(item.product.id),
                'code': item.product.code,
                'title': item.product.title,
                'description': item.product.description,
                'general_traceability_method': item.product.general_traceability_method
            } if item.product else {}
            item.uom_data = {
                'id': str(item.uom.id),
                'code': item.uom.code,
                'title': item.uom.title
            } if item.uom else {}
            item.warehouse_data = {
                'id': str(item.warehouse.id),
                'code': item.warehouse.code,
                'title': item.warehouse.title
            } if item.warehouse else {}
            item.save(update_fields=['product_data', 'uom_data', 'warehouse_data'])
    print('Done :))')


def update_bom_title():
    for bom in BOM.objects.all():
        bom.title = f"BOM - {bom.product.title}"
        bom.save(update_fields=['title'])
    print('Done :))')


def update_BOM_json_data():
    for bom in BOM.objects.all():
        bom.product_data = {
            'id': str(bom.product.id),
            'code': bom.product.code,
            'title': bom.product.title
        } if bom.product else {}
        bom.opp_data = {
            'id': str(bom.opportunity.id),
            'code': bom.opportunity.code,
            'title': bom.opportunity.title,
            'sale_person': {
                'id': str(bom.opportunity.employee_inherit_id),
                'code': bom.opportunity.employee_inherit.code,
                'full_name': bom.opportunity.employee_inherit.get_full_name(2),
            } if bom.opportunity.employee_inherit else {}
        } if bom.opportunity else {}
        bom.save(update_fields=['product_data', 'opp_data'])

        for item in bom.bom_process_bom.all():
            item.uom_data = {
                'id': str(item.uom.id),
                'code': item.uom.code,
                'title': item.uom.title,
                'ratio': item.uom.ratio,
                'group_id': str(item.uom.group_id)
            } if item.uom else {}
            item.save(update_fields=['uom_data'])

        for item in bom.bom_summary_process_bom.all():
            item.labor_data = {
                'id': str(item.labor.id),
                'code': item.labor.code,
                'title': item.labor.title,
            } if item.labor else {}
            item.uom_data = {
                'id': str(item.uom.id),
                'code': item.uom.code,
                'title': item.uom.title,
                'ratio': item.uom.ratio,
                'group_id': str(item.uom.group_id)
            } if item.uom else {}
            item.save(update_fields=['labor_data', 'uom_data'])

        for item in bom.bom_material_component_bom.all():
            item.material_data = {
                'id': str(item.material.id),
                'code': item.material.code,
                'title': item.material.title
            } if item.material else {}
            item.uom_data = {
                'id': str(item.uom.id),
                'code': item.uom.code,
                'title': item.uom.title,
                'ratio': item.uom.ratio,
                'group_id': str(item.uom.group_id)
            } if item.uom else {}
            item.save(update_fields=['material_data', 'uom_data'])
            for replacement_item in item.bom_replacement_material_replace_for.all():
                replacement_item.material_data = {
                    'id': str(replacement_item.material.id),
                    'code': replacement_item.material.code,
                    'title': replacement_item.material.title
                } if replacement_item.material else {}
                replacement_item.uom_data = {
                    'id': str(replacement_item.uom.id),
                    'code': replacement_item.uom.code,
                    'title': replacement_item.uom.title,
                    'group_id': str(replacement_item.uom.group_id),
                } if replacement_item.uom else {}
                replacement_item.save(update_fields=['material_data', 'uom_data'])

        for item in bom.bom_tool_bom.all():
            item.tool_data = {
                'id': str(item.tool.id),
                'code': item.tool.code,
                'title': item.tool.title
            } if item.tool else {}
            item.uom_data = {
                'id': str(item.uom.id),
                'code': item.uom.code,
                'title': item.uom.title,
                'ratio': item.uom.ratio,
                'group_id': str(item.uom.group_id)
            } if item.uom else {}
            item.save(update_fields=['tool_data', 'uom_data'])

        print(f'Done {bom.title} :))')

    return True


def add_code_for_product_masterdata():
    for company in Company.objects.all():
        count = 1
        for item in ProductCategory.objects.filter(company=company):
            item.code = f"00{count}"
            item.save(update_fields=['code'])
            count += 1

        count = 1
        for item in UnitOfMeasureGroup.objects.filter(company=company):
            if item.is_default:
                item.code = "UG001"
                item.save(update_fields=['code'])
            else:
                item.code = f"00{count}"
                item.save(update_fields=['code'])
                count += 1
    print('Done :))')


def add_code_for_price_masterdata():
    for company in Company.objects.all():
        count = 1
        for item in TaxCategory.objects.filter(company=company):
            item.code = f"TC00{count}"
            item.save(update_fields=['code'])
            count += 1
    print('Done :))')


def update_difference_quantity_goods_issue():
    for gis in GoodsIssue.objects.all():
        for item in gis.goods_issue_product.all():
            po_item = item.production_order_item
            wo_item = item.work_order_item
            if po_item:
                item.remain_quantity = po_item.quantity - item.before_quantity
            if wo_item:
                item.remain_quantity = wo_item.quantity - item.before_quantity
            item.save(update_fields=['remain_quantity'])
    print('Done :))')


def update_valuation_method():
    for company in Company.objects.all():
        print(company.code)
        company.company_config.default_inventory_value_method = 1
        company.company_config.save(update_fields=['default_inventory_value_method'])
    for product in Product.objects.all():
        product.valuation_method = 1
        product.save(update_fields=['valuation_method'])
    print('Done :))')


def create_import_uom_group():
    for company in Company.objects.all():
        has_import_uom_group = UnitOfMeasureGroup.objects.filter(
            company=company,
            tenant=company.tenant,
            is_default=True,
            code='UG000',
        ).exists()
        if not has_import_uom_group:
            UnitOfMeasureGroup.objects.create(
                company=company,
                tenant=company.tenant,
                is_default=True,
                code='ImportGroup',
                title='Nhóm đơn vị cho import'
            )
            print(f"Added for {company.title} :))")
    print('Done')


def remove_wf_sys_template():
    MailTemplateSystem.objects.filter(system_code=6).delete()  # workflow
    print('remove_wf_sys_template done.')
    return True


def update_default_masterdata():
    # UOM Group
    UnitOfMeasureGroup.objects.filter(
        title__in=['Nhân công', 'nhân công', 'Nhan cong', 'nhan cong', 'Labor', 'labor']
    ).update(code='Labor', title='Nhân công', is_default=1)
    UnitOfMeasureGroup.objects.filter(
        title__in=['Kích thước', 'kích thước', 'Kich thuoc', 'kich thuoc', 'Size', 'size']
    ).update(code='Size', title='Kích thước', is_default=1)
    UnitOfMeasureGroup.objects.filter(
        title__in=['Thời gian', 'thời gian', 'Thoi gian', 'thoi gian', 'Time', 'time']
    ).update(code='Time', title='Thời gian', is_default=1)
    UnitOfMeasureGroup.objects.filter(
        title__in=['Đơn vị', 'đơn vị', 'Don vi', 'don vi', 'Unit', 'unit']
    ).update(code='Unit', title='Đơn vị', is_default=1)

    # UOM
    UnitOfMeasure.objects.filter(group__code='Labor').update(is_default=0)
    for item in UnitOfMeasure.objects.filter(group__code='Labor', group__is_default=1):
        if item.title.lower() in ['manhour', 'man hour']:
            item.code = 'Manhour'
            item.title = 'Man hour'
            item.is_referenced_unit = 1
            item.ratio = 1
            item.rounding = 4
            item.is_default = 1
            item.save()
        if item.title.lower() in ['manday', 'man day']:
            item.code = 'Manday'
            item.title = 'Man day'
            item.is_referenced_unit = 0
            item.ratio = 8
            item.rounding = 4
            item.is_default = 1
            item.save()
        if item.title.lower() in ['manmonth', 'man month']:
            item.code = 'Manmonth'
            item.title = 'Man month'
            item.is_referenced_unit = 0
            item.ratio = 176
            item.rounding = 4
            item.is_default = 1
            item.save()
    print('Done :))')


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


def update_activities_tenant_and_company():
    for item in OpportunityCallLog.objects.all():
        if item.opportunity:
            item.tenant = item.opportunity.tenant
            item.company = item.opportunity.company
            item.save(update_fields=['tenant', 'company'])
    for item in OpportunityEmail.objects.all():
        if item.opportunity:
            item.tenant = item.opportunity.tenant
            item.company = item.opportunity.company
            item.save(update_fields=['tenant', 'company'])
    for item in OpportunityMeeting.objects.all():
        if item.opportunity:
            item.tenant = item.opportunity.tenant
            item.company = item.opportunity.company
            item.save(update_fields=['tenant', 'company'])
    for item in OpportunityActivityLogs.objects.all():
        if item.opportunity:
            item.tenant = item.opportunity.tenant
            item.company = item.opportunity.company
            item.save(update_fields=['tenant', 'company'])
    print('Done :))')


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
    print('Done :))')
    return True


def update_lead_stage():
    lead_stage_data = [
        {
            'stage_title': 'Marketing Acquired Lead',
            'level': 1,
        },
        {
            'stage_title': 'Marketing Qualified Lead',
            'level': 2,
        },
        {
            'stage_title': 'Sales Accepted Lead',
            'level': 3,
        },
        {
            'stage_title': 'Sales Qualified Lead',
            'level': 4,
        },
    ]
    bulk_info = []
    for company in Company.objects.all():
        num_stage = LeadStage.objects.filter(company=company).count()
        if num_stage == 0:
            for stage in lead_stage_data:
                bulk_info.append(LeadStage(
                    tenant=company.tenant,
                    company=company,
                    **stage
                ))
    LeadStage.objects.bulk_create(bulk_info)
    print('Done :))')


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


def move_opp_mapped_2_opp():
    for company in Company.objects.all():
        for ap in AdvancePayment.objects.filter(company=company):
            if ap.opportunity_mapped:
                ap.opportunity = ap.opportunity_mapped
                ap.save(update_fields=['opportunity'])
            for item in ap.advance_payment.all():
                if item.opportunity_mapped:
                    item.opportunity = item.opportunity_mapped
                    item.save(update_fields=['opportunity'])

        for pm in Payment.objects.filter(company=company):
            if pm.opportunity_mapped:
                pm.opportunity = pm.opportunity_mapped
                pm.save(update_fields=['opportunity'])
            for item in pm.payment.all():
                if item.opportunity_mapped:
                    item.opportunity = item.opportunity_mapped
                    item.save(update_fields=['opportunity'])

        print(f"Done for {company.title}")
    print('Done :))')


def reset_remain_gr_for_po():
    for pr_product in PurchaseOrderRequestProduct.objects.filter(
            purchase_order_id="c9e2df0f-227d-4ee1-9b9e-6ba486724b02"
    ):
        pr_product.gr_remain_quantity = pr_product.quantity_order
        pr_product.save(update_fields=['gr_remain_quantity'])
    print("reset_remain_gr_for_po done.")
    return True


def recreate_balance_init_for_Saty():
    company = Company.objects.get(id='9cbe0e8e-7c57-424c-bb88-c19bf15937ce')
    Product.objects.filter(company_id='9cbe0e8e-7c57-424c-bb88-c19bf15937ce').update(valuation_method=0)
    data = [
        {
            'product_id': '07c71d46-e4aa-4417-9894-8b4287836a5c',
            'warehouse_id': 'd8eeeb4e-192e-4de1-8bb0-c41509f00fc1',
            'quantity': 56,
            'value': 8120000,
        },
        {
            'product_id': '5fa410b8-c08c-4f32-8365-79fd54ade96a',
            'warehouse_id': 'd8eeeb4e-192e-4de1-8bb0-c41509f00fc1',
            'quantity': 1727,
            'value': 117436000,
        },
        {
            'product_id': 'c1fb682a-a124-41df-b986-7882e5cd4675',
            'warehouse_id': 'd8eeeb4e-192e-4de1-8bb0-c41509f00fc1',
            'quantity': 13,
            'value': 884000,
        },
        {
            'product_id': '07ead28b-03c9-4e0b-a5b0-c7bf5255385c',
            'warehouse_id': 'd8eeeb4e-192e-4de1-8bb0-c41509f00fc1',
            'quantity': 280,
            'value': 19040000,
        },
        {
            'product_id': '398dfae8-8e3e-4d3d-a596-c05830dd9da6',
            'warehouse_id': 'd8eeeb4e-192e-4de1-8bb0-c41509f00fc1',
            'quantity': 10,
            'value': 680000,
        },
        {
            'product_id': 'd15611a3-5cca-440e-9694-526b82472be2',
            'warehouse_id': 'd8eeeb4e-192e-4de1-8bb0-c41509f00fc1',
            'quantity': 481,
            'value': 32708000,
        },
        {
            'product_id': 'd6a9fe75-5eff-4425-b92e-5cc7e6f7f6d1',
            'warehouse_id': 'd8eeeb4e-192e-4de1-8bb0-c41509f00fc1',
            'quantity': 124,
            'value': 5208000,
        },
        {
            'product_id': '0b720ac2-4aa6-4e84-a8c3-3125624c57fc',
            'warehouse_id': 'd8eeeb4e-192e-4de1-8bb0-c41509f00fc1',
            'quantity': 52,
            'value': 2184000,
        },
        {
            'product_id': '1314f17e-e661-4ab5-abf6-f3b11134d7ee',
            'warehouse_id': 'd8eeeb4e-192e-4de1-8bb0-c41509f00fc1',
            'quantity': 51,
            'value': 9052500,
        },
    ]
    for item in data:
        product_obj = Product.objects.get(id=item.get('product_id'))
        BalanceInitialization.objects.create(
            product=product_obj,
            warehouse_id=item.get('warehouse_id'),
            uom=product_obj.inventory_uom,
            quantity=item.get('quantity'),
            value=item.get('value'),
            data_lot=[],
            data_sn=[],
            tenant=company.tenant,
            company=company,
            employee_created_id='b442fe11-8675-443d-adb8-5cdbd048b7e7',
            employee_inherit_id='b442fe11-8675-443d-adb8-5cdbd048b7e7',
        )
        print(f"Created {product_obj.code} - {product_obj.title}")
    print('Done :_))')


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


def create_data_for_GR_WH_PRD():
    for item in GoodsReceiptRequestProduct.objects.all():
        if item.purchase_request_product:
            item.purchase_request_data = {
                'id': str(item.purchase_request_product.purchase_request_id),
                'code': item.purchase_request_product.purchase_request.code,
                'title': item.purchase_request_product.purchase_request.title
            }
            item.save(update_fields=['purchase_request_data'])
    print('Done :_)')


def update_data_for_GoodsReceiptLot():
    for item in GoodsReceiptLot.objects.all():
        lot_obj = ProductWareHouseLot.objects.filter(
            lot_number=item.lot_number,
            product_warehouse__product=item.goods_receipt_warehouse.goods_receipt_product.product
        ).first()
        item.lot = lot_obj
        item.save(update_fields=['lot'])
    print('Done :))')


def recreate_goods_detail_data():
    GoodsDetail.objects.all().delete()
    update_data_for_GoodsReceiptLot()
    for goods_receipt_obj in GoodsReceipt.objects.filter(system_status=3):
        GoodsReceipt.push_goods_receipt_data_to_goods_detail(goods_receipt_obj)
    print('Done :))')


def update_distribution_plan_end_date():
    def find_end_date(start_date, n):
        date = start_date + relativedelta(months=n)
        if date.day < start_date.day:
            date -= timedelta(days=date.day)
        return date

    for obj in DistributionPlan.objects.all():
        obj.end_date = find_end_date(obj.start_date, obj.no_of_month)
        obj.save(update_fields=['end_date'])
        print(f'Finish {obj.code}')

    print('Done :))')


def update_sale_activities():
    for item in OpportunityCallLog.objects.all():
        item.employee_inherit = item.opportunity.employee_inherit
        item.save(update_fields=['employee_inherit'])
    print('Done Call Log')
    for item in OpportunityMeeting.objects.all():
        item.employee_inherit = item.opportunity.employee_inherit
        item.save(update_fields=['employee_inherit'])
    print('Done Meeting')
    for item in OpportunityEmail.objects.all():
        item.employee_inherit = item.opportunity.employee_inherit
        item.save(update_fields=['employee_inherit'])
    print('Done Email')


def parse_quotation_data_so():
    for order in SaleOrder.objects.all():
        if order.quotation:
            quotation_data = QuotationListSerializer(order.quotation).data
            order.quotation_data = quotation_data
            order.save(update_fields=['quotation_data'])
    print('parse_quotation_data_so done.')
    return True


def update_lead_code():
    for company in Company.objects.all():
        Lead.objects.filter(company=company).update(system_status=0)
        for lead in Lead.objects.filter(company=company).order_by('date_created'):
            lead.system_status = 1
            lead.save(update_fields=['system_status', 'code'])
        print(f'Finished {company.title}')
    print('Done :))')


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


def mockup_data_company_bank_account(company_id):
    if company_id:
        CompanyBankAccount.objects.filter(company_id=company_id).delete()
        bulk_info = [
            CompanyBankAccount(
                company_id=company_id,
                country_id='bbf52b7b77ed4e8caf0a86ca00771d83',
                bank_name='Ngân hàng quân đội',
                bank_code='MBBANK',
                bank_account_name='NGUYEN DUONG HAI',
                bank_account_number='03112001',
                bic_swift_code='',
                is_default=True,
                is_active=True,
            ),
            CompanyBankAccount(
                company_id=company_id,
                country_id='bbf52b7b77ed4e8caf0a86ca00771d83',
                bank_name='Ngân hàng TMCP Đầu tư và Phát triển Việt Nam',
                bank_code='BIDV',
                bank_account_name='NGUYEN DUONG HAI',
                bank_account_number='19521464',
                bic_swift_code='',
                is_default=False,
                is_active=True,
            ),
            CompanyBankAccount(
                company_id=company_id,
                country_id='bbf52b7b77ed4e8caf0a86ca00771d83',
                bank_name='Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam',
                bank_code='AGRIBANK',
                bank_account_name='NGUYEN DUONG HAI',
                bank_account_number='18122024',
                bic_swift_code='',
                is_default=False,
                is_active=True,
            ),
        ]
        CompanyBankAccount.objects.bulk_create(bulk_info)
        print('Done :))')
    else:
        print('Company id :)) ???')
    return True


def update_AR_invoice_code():
    for company in Company.objects.all():
        ARInvoice.objects.filter(company=company).update(system_status=0)
        for ar in ARInvoice.objects.filter(company=company).order_by('date_created'):
            ar.system_status = 1
            ar.save(update_fields=['system_status', 'code'])
        print(f'Finished {company.title}')
    print('Done :))')


def update_end_date():
    for item in Periods.objects.all():
        item.end_date = item.start_date + relativedelta(months=12) - relativedelta(days=1)
        item.save(update_fields=['end_date'])
    print('Done')


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


def update_email_state_just_log():
    OpportunityEmail.objects.filter(just_log=False).update(send_success=True)
    print('Done :))')
    return True


def update_address_contact():
    for contact in Contact.objects.all():
        home_address_data = {
            'home_country': {
                'id': str(contact.home_country.id),
                'title': contact.home_country.title
            } if contact.home_country else {},
            'home_detail_address': contact.home_detail_address if contact.home_detail_address else '',
            'home_city': {
                'id': str(contact.home_city.id),
                'title': contact.home_city.title
            } if contact.home_city else {},
            'home_district': {
                'id': str(contact.home_district.id),
                'title': contact.home_district.title
            } if contact.home_district else {},
            'home_ward': {
                'id': str(contact.work_country.id),
                'title': contact.work_country.title
            } if contact.home_ward else {},
        }
        work_address_data = {
            'work_country': {
                'id': str(contact.work_country.id),
                'title': contact.work_country.title
            } if contact.work_country else {},
            'work_detail_address': contact.work_detail_address if contact.work_detail_address else '',
            'work_city': {
                'id': str(contact.work_city.id),
                'title': contact.work_city.title
            } if contact.work_city else {},
            'work_district': {
                'id': str(contact.work_district.id),
                'title': contact.work_district.title
            } if contact.work_district else {},
            'work_ward': {
                'id': str(contact.work_ward.id),
                'title': contact.work_ward.title
            } if contact.work_ward else {},
        }
        contact.home_address_data = home_address_data
        contact.work_address_data = work_address_data
        contact.save(update_fields=['home_address_data', 'work_address_data'])
    print('Done :))')


def update_employee_for_promotion():
    for company in Company.objects.all():
        admin = Employee.objects.filter(company=company, is_admin_company=True).first()
        Promotion.objects.filter(company=company).update(
            employee_inherit=admin, employee_created=admin, employee_modified=admin
        )
    print('Done update_employee_for_promotion !!')


def update_employee_revenue_plan():
    for item in RevenuePlanGroupEmployee.objects.all():
        item.employee_created = item.revenue_plan_mapped.employee_created
        item.employee_inherit = item.employee_mapped
        item.tenant = item.revenue_plan_mapped.tenant
        item.company = item.revenue_plan_mapped.company
        item.save(update_fields=['employee_created', 'employee_inherit', 'tenant', 'company'])
    print('Done :))')


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


def update_period_cfg():
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


def update_opp_stage_is_delete():
    OpportunityConfigStage.objects.filter(is_default=True).update(is_delete=False)
    return True


def update_asset_tool_type():
    ProductType.objects.filter(
        code='asset_tool', is_default=1, is_asset_tool=1
    ).update(title='Công cụ- Dụng cụ')
    print('Done :))')
    return True
