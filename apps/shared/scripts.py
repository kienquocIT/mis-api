from datetime import date, datetime

from django.utils import timezone

from apps.masterdata.saledata.models.periods import Periods
from apps.core.company.models import Company, CompanyFunctionNumber
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
    ProductWareHouse, ProductWareHouseLot, ProductWareHouseSerial,
)
from . import MediaForceAPI

from .extends.signals import SaleDefaultData, ConfigDefaultData
from .permissions.util import PermissionController
from ..core.hr.models import (
    Employee, Role, EmployeePermission, PlanEmployeeApp, PlanEmployee, RolePermission,
    PlanRole, PlanRoleApp,
)
from ..eoffice.leave.leave_util import leave_available_map_employee
from ..eoffice.leave.models import LeaveAvailable
from ..masterdata.saledata.serializers import PaymentTermListSerializer
from ..sales.acceptance.models import FinalAcceptanceIndicator
from ..sales.delivery.models import DeliveryConfig, OrderDeliverySub
from ..sales.delivery.serializers.delivery import DeliProductInformationHandle, DeliProductWarehouseHandle
from ..sales.inventory.models import InventoryAdjustmentItem, GoodsReceiptRequestProduct, GoodsReceipt, \
    GoodsReceiptWarehouse, GoodsReturn
from ..sales.inventory.models import GReturnProductInformationHandle
from ..sales.inventory.utils import GRFinishHandler
from ..sales.opportunity.models import (
    Opportunity, OpportunityConfigStage, OpportunityStage, OpportunityCallLog,
    OpportunitySaleTeamMember, OpportunityDocument, OpportunityMeeting,
)
from ..sales.opportunity.serializers import CommonOpportunityUpdate
from ..sales.purchasing.models import PurchaseRequestProduct, PurchaseRequest, PurchaseOrderProduct, \
    PurchaseOrderRequestProduct, PurchaseOrder, PurchaseOrderPaymentStage
from ..sales.purchasing.utils import POFinishHandler
from ..sales.quotation.models import QuotationIndicatorConfig, Quotation, QuotationIndicator, QuotationAppConfig
from ..sales.report.models import ReportRevenue, ReportPipeline, ReportInventorySub, ReportCashflow, \
    ReportInventoryProductWarehouse, LatestSub
from ..sales.revenue_plan.models import RevenuePlanGroupEmployee
from ..sales.saleorder.models import SaleOrderIndicatorConfig, SaleOrderProduct, SaleOrder, SaleOrderIndicator, \
    SaleOrderAppConfig, SaleOrderPaymentStage
from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer
from ..sales.saleorder.utils import SOFinishHandler
from ..sales.task.models import OpportunityTaskStatus


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


def update_employee_inherit_quotation_sale_order():
    for quotation in Quotation.objects.all():
        if quotation.sale_person:
            quotation.employee_inherit = quotation.sale_person
            quotation.save(update_fields=['employee_inherit'])
    for sale_order in SaleOrder.objects.all():
        if sale_order.sale_person:
            sale_order.employee_inherit = sale_order.sale_person
            sale_order.save(update_fields=['employee_inherit'])
    print('Update done.')


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


def update_code_quotation_sale_order_indicator_config():
    for indicator in QuotationIndicatorConfig.objects.filter(company__isnull=False):
        indicator.code = "IN000" + str(indicator.order)
        indicator.tenant_id = indicator.company.tenant_id
        indicator.save(update_fields=['code', 'tenant_id'])
    for indicator in SaleOrderIndicatorConfig.objects.filter(company__isnull=False):
        indicator.code = "IN000" + str(indicator.order)
        indicator.tenant_id = indicator.company.tenant_id
        indicator.save(update_fields=['code', 'tenant_id'])
    print('update_code_quotation_sale_order_indicator_config done.')


def update_code_quotation_sale_order_indicator():
    for indicator in QuotationIndicator.objects.filter(indicator__isnull=False):
        indicator.code = indicator.indicator.code
        indicator.tenant_id = indicator.indicator.tenant_id
        indicator.company_id = indicator.indicator.company_id
        indicator.save(update_fields=['code', 'tenant_id', 'company_id'])
    for indicator in SaleOrderIndicator.objects.filter(quotation_indicator__isnull=False):
        indicator.code = indicator.quotation_indicator.code
        indicator.tenant_id = indicator.quotation_indicator.tenant_id
        indicator.company_id = indicator.quotation_indicator.company_id
        indicator.save(update_fields=['code', 'tenant_id', 'company_id'])
    print('update_code_quotation_sale_order_indicator done.')


def update_record_report_revenue():
    ReportRevenue.objects.all().delete()
    bulk_info = []
    for so in SaleOrder.objects.filter(system_status__in=[2, 3], employee_inherit__isnull=False):
        revenue_obj = so.sale_order_indicator_sale_order.filter(code='IN0001').first()
        gross_profit_obj = so.sale_order_indicator_sale_order.filter(code='IN0003').first()
        net_income_obj = so.sale_order_indicator_sale_order.filter(code='IN0006').first()
        bulk_info.append(ReportRevenue(
            tenant_id=so.tenant_id,
            company_id=so.company_id,
            sale_order_id=so.id,
            employee_created_id=so.employee_created_id,
            employee_inherit_id=so.employee_inherit_id,
            group_inherit_id=so.employee_inherit.group_id,
            date_approved=so.date_approved,
            revenue=revenue_obj.indicator_value if revenue_obj else 0,
            gross_profit=gross_profit_obj.indicator_value if gross_profit_obj else 0,
            net_income=net_income_obj.indicator_value if net_income_obj else 0,
        ))
    ReportRevenue.objects.bulk_create(bulk_info)
    print('update_record_report_revenue done.')


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


def update_date_approved_sales_apps():
    for quotation in Quotation.objects.filter(system_status__in=[2, 3]):
        quotation.date_approved = quotation.date_created
        quotation.save(update_fields=['date_approved'])
    for so in SaleOrder.objects.filter(system_status__in=[2, 3]):
        so.date_approved = so.date_created
        so.save(update_fields=['date_approved'])
    for po in PurchaseOrder.objects.filter(system_status__in=[2, 3]):
        po.date_approved = po.date_created
        po.save(update_fields=['date_approved'])
    for gr in GoodsReceipt.objects.filter(system_status__in=[2, 3]):
        gr.date_approved = gr.date_created
        gr.save(update_fields=['date_approved'])
    print('update_date_approved_sales_apps done.')


def update_company_setting():
    vnd_currency = BaseCurrency.objects.filter(code='VND').first()
    for company_obj in Company.objects.all():
        if vnd_currency:
            company_obj.definition_inventory_valuation = 0
            company_obj.default_inventory_value_method = 0
            company_obj.cost_per_warehouse = False
            company_obj.cost_per_lot_batch = False
            company_obj.primary_currency_id = str(vnd_currency.id)
            company_obj.save(update_fields=[
                'definition_inventory_valuation',
                'default_inventory_value_method',
                'cost_per_warehouse',
                'cost_per_lot_batch',
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


def update_final_acceptance_indicator():
    for ind in FinalAcceptanceIndicator.objects.all():
        if ind.sale_order_indicator:
            ind.indicator_id = ind.sale_order_indicator.quotation_indicator_id
            ind.save(update_fields=['indicator_id'])
    print('update_final_acceptance_indicator done.')


def update_payment_cost():
    for item in PaymentCost.objects.all():
        item.opportunity_mapped = item.payment.opportunity_mapped
        item.quotation_mapped = item.payment.quotation_mapped
        item.sale_order_mapped = item.payment.sale_order_mapped
        item.save()
    print('update done')


def update_tenant_quotation_so_config():
    for quo_config in QuotationAppConfig.objects.all():
        if quo_config.company:
            quo_config.tenant = quo_config.company.tenant
            quo_config.save(update_fields=['tenant'])
    for so_config in SaleOrderAppConfig.objects.all():
        if so_config.company:
            so_config.tenant = so_config.company.tenant
            so_config.save(update_fields=['tenant'])
    print('update_tenant_quotation_so_config done.')


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


def create_report_pipeline_by_opp():
    for opp in Opportunity.objects.all():
        ReportPipeline.push_from_opp(
            tenant_id=opp.tenant_id,
            company_id=opp.company_id,
            opportunity_id=opp.id,
            employee_inherit_id=opp.employee_inherit_id,
        )
    print('create_report_pipeline_by_opp done.')
    return True


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


def update_date_approved():
    for item in ReportRevenue.objects.all():
        if item.date_approved is None:
            item.date_approved = item.date_created
            item.save(update_fields=['date_approved'])
    for item in ReportCustomer.objects.all():
        if item.date_approved is None:
            item.date_approved = item.date_created
            item.save(update_fields=['date_approved'])
    for item in ReportProduct.objects.all():
        if item.date_approved is None:
            item.date_approved = item.date_created
            item.save(update_fields=['date_approved'])
    print('Done!')


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
        for sale_order in SaleOrder.objects.filter(system_status__in=[2, 3]):
            SOFinishHandler.push_to_report_revenue(sale_order)
            SOFinishHandler.push_to_report_product(sale_order)
            SOFinishHandler.push_to_report_customer(sale_order)
    if run_type == 1:  # run report cashflow
        ReportCashflow.objects.all().delete()
        for sale_order in SaleOrder.objects.filter(system_status__in=[2, 3]):
            SOFinishHandler.push_to_report_cashflow(sale_order)
        for purchase_order in PurchaseOrder.objects.filter(system_status__in=[2, 3]):
            POFinishHandler.push_to_report_cashflow(purchase_order)
    print('reset_and_run_reports_sale done.')


def update_indicators_quotation_so_model():
    for quotation in Quotation.objects.all():
        revenue_obj = quotation.quotation_indicator_quotation.filter(code='IN0001').first()
        gross_profit_obj = quotation.quotation_indicator_quotation.filter(code='IN0003').first()
        net_income_obj = quotation.quotation_indicator_quotation.filter(code='IN0006').first()
        quotation.indicator_revenue = revenue_obj.indicator_value if revenue_obj else 0
        quotation.indicator_gross_profit = gross_profit_obj.indicator_value if gross_profit_obj else 0
        quotation.indicator_net_income = net_income_obj.indicator_value if net_income_obj else 0
        quotation.save(update_fields=['indicator_revenue', 'indicator_gross_profit', 'indicator_net_income'])
    for so in SaleOrder.objects.all():
        revenue_obj = so.sale_order_indicator_sale_order.filter(code='IN0001').first()
        gross_profit_obj = so.sale_order_indicator_sale_order.filter(code='IN0003').first()
        net_income_obj = so.sale_order_indicator_sale_order.filter(code='IN0006').first()
        so.indicator_revenue = revenue_obj.indicator_value if revenue_obj else 0
        so.indicator_gross_profit = gross_profit_obj.indicator_value if gross_profit_obj else 0
        so.indicator_net_income = net_income_obj.indicator_value if net_income_obj else 0
        so.save(update_fields=['indicator_revenue', 'indicator_gross_profit', 'indicator_net_income'])
    print('update_indicators_quotation_so_model done.')


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


def reset_set_product_transaction_information():
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
    for po in PurchaseOrder.objects.filter(system_status__in=[2, 3]):
        PurchaseOrder.update_product_wait_receipt_amount(instance=po)
    for gr in GoodsReceipt.objects.filter(system_status__in=[2, 3]):
        GRFinishHandler.update_product_wait_receipt_amount(instance=gr)
    # output
    for so in SaleOrder.objects.filter(system_status__in=[2, 3]):
        SOFinishHandler.update_product_wait_delivery_amount(instance=so)
    for deli_sub in OrderDeliverySub.objects.all():
        DeliProductInformationHandle.main_handle(instance=deli_sub)
    # return
    for return_obj in GoodsReturn.objects.all():
        GReturnProductInformationHandle.main_handle(instance=return_obj)
    print('reset_set_product_transaction_information done.')


def reset_set_product_warehouse_stock():
    # reset
    update_fields = ['stock_amount', 'receipt_amount', 'sold_amount', 'picked_ready', 'used_amount']
    for product_wh in ProductWareHouse.objects.all():
        product_wh.stock_amount = 0
        product_wh.receipt_amount = 0
        product_wh.sold_amount = 0
        product_wh.picked_ready = 0
        product_wh.used_amount = 0
        product_wh.save(update_fields=update_fields)
    # input, output, provide
    # input
    for gr in GoodsReceipt.objects.filter(system_status__in=[2, 3]):
        GRFinishHandler.push_to_product_warehouse(instance=gr)
    # output
    for deli_sub in OrderDeliverySub.objects.all():
        DeliProductWarehouseHandle.main_handle(instance=deli_sub)
    print('reset_set_product_warehouse_stock done.')


def reset_opportunity_stage():
    for opp in Opportunity.objects.all():
        CommonOpportunityUpdate.update_opportunity_stage_for_list(opp)
    print('Done')


def update_report_inventory_sub_trans_title():
    for item in ReportInventorySub.objects.all():
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


def update_gr_for_lot_serial():
    for gr in GoodsReceipt.objects.filter(system_status__in=[2, 3]):
        for gr_lot in gr.goods_receipt_lot_goods_receipt.all():
            lot = ProductWareHouseLot.objects.filter(lot_number=gr_lot.lot_number).first()
            if lot:
                lot.goods_receipt = gr
                lot.save(update_fields=['goods_receipt'])
        for gr_serial in gr.goods_receipt_serial_goods_receipt.all():
            serial = ProductWareHouseSerial.objects.filter(serial_number=gr_serial.serial_number).first()
            if serial:
                serial.goods_receipt = gr
                serial.save(update_fields=['goods_receipt'])
    print('update_gr_for_lot_serial done.')


def get_latest_trans(log, period_mapped, sub_period_order):
    # để tránh TH lấy hết records lên thì sẽ lấy ưu tiên theo thứ tự:
    # 1: lấy records tháng này
    # 2: lấy records các tháng trước (trong năm)
    # 3: lấy records các năm trước
    subs = ReportInventorySub.objects.filter(
        product_id=log.product_id, warehouse_id=log.warehouse_id,
        report_inventory__period_mapped=period_mapped,
        report_inventory__sub_period_order=sub_period_order,
        date_created__lt=log.date_created
    )
    if subs.count() == 0:
        subs = ReportInventorySub.objects.filter(
            product_id=log.product_id, warehouse_id=log.warehouse_id,
            report_inventory__period_mapped=period_mapped,
            report_inventory__sub_period_order__lt=sub_period_order,
            date_created__lt=log.date_created
        )
        if subs.count() == 0:
            subs = ReportInventorySub.objects.filter(
                product_id=log.product_id, warehouse_id=log.warehouse_id,
                report_inventory__period_mapped__fiscal_year__lt=period_mapped.fiscal_year,
                date_created__lt=log.date_created
            )
    latest_trans = subs.latest('date_created') if subs.count() > 0 else None
    return latest_trans


def run_inventory_report():
    for log in ReportInventorySub.objects.all().order_by('date_created'):
        period_mapped = log.report_inventory.period_mapped
        sub_period_order = log.report_inventory.sub_period_order
        latest_trans = get_latest_trans(log, period_mapped, sub_period_order)
        if latest_trans:
            latest_value_list = {
                'quantity': latest_trans.current_quantity,
                'cost': latest_trans.current_cost,
                'value': latest_trans.current_value
            }
        else:
            latest_value_list = {
                'quantity': log.quantity,
                'cost': log.cost,
                'value': log.value
            }

        sub_period_obj = period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if sub_period_obj:
            inventory_cost_data_item = ReportInventoryProductWarehouse.objects.filter(
                tenant_id=period_mapped.tenant_id,
                company_id=period_mapped.company_id,
                product=log.product,
                warehouse=log.warehouse,
                period_mapped=period_mapped,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj
            ).first()
            if not inventory_cost_data_item:
                ReportInventoryProductWarehouse.objects.create(
                    tenant_id=period_mapped.tenant_id,
                    company_id=period_mapped.company_id,
                    product=log.product,
                    warehouse=log.warehouse,
                    period_mapped=period_mapped,
                    sub_period_order=sub_period_order,
                    sub_period=period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                    opening_balance_quantity=latest_value_list['quantity'],
                    opening_balance_cost=latest_value_list['cost'],
                    opening_balance_value=latest_value_list['value'],
                    ending_balance_quantity=log.current_quantity,
                    ending_balance_cost=log.current_cost,
                    ending_balance_value=log.current_value,
                )
            else:
                inventory_cost_data_item.ending_balance_quantity = log.current_quantity
                inventory_cost_data_item.ending_balance_cost = log.current_cost
                inventory_cost_data_item.ending_balance_value = log.current_value
                inventory_cost_data_item.save(update_fields=[
                    'ending_balance_quantity', 'ending_balance_cost', 'ending_balance_value'
                ])

            latest_log_obj = LatestSub.objects.filter(
                product=log.product, warehouse=log.warehouse
            ).first()
            if latest_log_obj:
                latest_log_obj.latest_log = log
                latest_log_obj.save(update_fields=['latest_log'])
            else:
                LatestSub.objects.create(
                    product=log.product, warehouse=log.warehouse, latest_log=log
                )
    print('Done')
    return True
