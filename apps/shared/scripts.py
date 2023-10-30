from datetime import date
from apps.core.company.models import Company
from apps.masterdata.saledata.models.product import (
    ProductType, Product, ExpensePrice, ProductCategory, UnitOfMeasure,
    Expense,
)
from apps.masterdata.saledata.models.price import (
    TaxCategory, Currency, Price, UnitOfMeasureGroup, Tax, ProductPriceList, PriceListCurrency,
)
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import AccountType, Account, AccountCreditCards

from apps.core.base.models import PlanApplication, ApplicationProperty, Application, SubscriptionPlan, City
from apps.core.tenant.models import Tenant, TenantPlan
from apps.sales.cashoutflow.models import (
    AdvancePayment, AdvancePaymentCost,
    ReturnAdvance, ReturnAdvanceCost,
    Payment, PaymentCost, PaymentCostItems, PaymentCostItemsDetail, PaymentQuotation, PaymentSaleOrder,
)
from apps.core.workflow.models import WorkflowConfigOfApp, Workflow, Runtime, RuntimeStage, RuntimeAssignee, RuntimeLog
from apps.masterdata.saledata.models import (
    ConditionLocation, FormulaCondition, ShippingCondition, Shipping,
    ProductWareHouse,
)
from . import MediaForceAPI

from .extends.signals import SaleDefaultData, ConfigDefaultData
from .permissions.util import PermissionController
from ..core.hr.models import (
    Employee, Role, EmployeePermission, PlanEmployeeApp, PlanEmployee, RolePermission,
    PlanRole, PlanRoleApp,
)
from ..sales.inventory.models import InventoryAdjustmentItem, GoodsReceiptRequestProduct, GoodsReceipt, \
    GoodsReceiptWarehouse
from ..sales.opportunity.models import (
    Opportunity, OpportunityConfigStage, OpportunityStage, OpportunityCallLog,
    OpportunitySaleTeamMember, OpportunityDocument,
)
from ..sales.purchasing.models import PurchaseRequestProduct, PurchaseRequest, PurchaseOrderProduct, \
    PurchaseOrderRequestProduct, PurchaseOrder
from ..sales.quotation.models import QuotationIndicatorConfig, Quotation
from ..sales.saleorder.models import SaleOrderIndicatorConfig, SaleOrderProduct, SaleOrder


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
    PaymentCostItems.objects.all().delete()
    PaymentCostItemsDetail.objects.all().delete()
    PaymentSaleOrder.objects.all().delete()
    PaymentQuotation.objects.all().delete()
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


def delete_old_m2m_data_price_list_product():
    today = date.today()
    ProductPriceList.objects.filter(date_created__lt=today).delete()
    return True


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


def leave_available_create():
    for obj in Company.objects.all():
        ConfigDefaultData(obj).leave_available_setup()
    print('create leave available list successfully')


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


# BEGIN PRODUCT TRANSACTION INFORMATION
def update_product_stock_amount(product_id):
    product = Product.objects.filter(id=product_id).first()
    if product:
        product_stock_amount = 0
        for product_warehouse in product.product_warehouse_product.all():
            product_stock_amount += product_warehouse.stock_amount
        product.stock_amount = product_stock_amount
        product.available_amount = (product.stock_amount - product.wait_delivery_amount + product.wait_receipt_amount)
        product.save(update_fields=['available_amount', 'stock_amount'])
    print('update product stock amount done.')


def update_product_wait_delivery_amount(product_id):
    product = Product.objects.filter(id=product_id).first()
    if product:
        product_ordered_quantity = 0
        for product_ordered in product.sale_order_product_product.filter(
            sale_order__system_status__in=[2, 3]
        ):
            if product_ordered.product:
                uom_product_inventory = product_ordered.product.inventory_uom
                uom_product_so = product_ordered.unit_of_measure
                final_ratio = 1
                if uom_product_inventory and uom_product_so:
                    final_ratio = uom_product_so.ratio / uom_product_inventory.ratio
                product_ordered_quantity += product_ordered.product_quantity * final_ratio
        product.wait_delivery_amount = product_ordered_quantity
        product.available_amount = (product.stock_amount - product.wait_delivery_amount + product.wait_receipt_amount)
        product.save(update_fields=['wait_delivery_amount', 'available_amount'])
    print('update_product_wait_delivery_amount done.')


def update_product_wait_receipt_amount(product_id):
    product = Product.objects.filter(id=product_id).first()
    if product:
        product_purchased_quantity = 0
        product_receipted_quantity = 0
        for product_purchased in product.purchase_order_product_product.filter(
                purchase_order__system_status__in=[2, 3]
        ):
            uom_product_inventory = product_purchased.product.inventory_uom
            uom_product_po = product_purchased.uom_order_actual
            if product_purchased.uom_order_request:
                uom_product_po = product_purchased.uom_order_request
            final_ratio = 1
            if uom_product_inventory and uom_product_po:
                final_ratio = uom_product_po.ratio / uom_product_inventory.ratio
            product_quantity_order_request_final = product_purchased.product_quantity_order_actual * final_ratio
            if product_purchased.purchase_order.purchase_requests.exists():
                product_quantity_order_request_final = product_purchased.product_quantity_order_request * final_ratio
            stock_final = product_purchased.stock * final_ratio
            product_purchased_quantity += product_quantity_order_request_final + stock_final
        for product_receipted in product.goods_receipt_product_product.filter(
                goods_receipt__system_status__in=[2, 3],
                goods_receipt__purchase_order__isnull=False,
        ):
            uom_product_inventory = product_receipted.product.inventory_uom
            uom_product_gr = product_receipted.uom
            final_ratio = 1
            if uom_product_inventory and uom_product_gr:
                final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
            product_receipted_quantity += product_receipted.quantity_import * final_ratio
        product.wait_receipt_amount = (product_purchased_quantity - product_receipted_quantity)
        product.available_amount = (product.stock_amount - product.wait_delivery_amount + product.wait_receipt_amount)
        product.save(update_fields=['wait_receipt_amount', 'available_amount'])
    print('update product wait_receipt_amount done.')


def update_product_warehouse_amounts():
    # update ProductWarehouse
    for product_warehouse in ProductWareHouse.objects.all():
        product_warehouse.receipt_amount = product_warehouse.stock_amount
        product_warehouse.stock_amount = product_warehouse.receipt_amount - product_warehouse.sold_amount
        product_warehouse.save(update_fields=['receipt_amount', 'stock_amount'])
    print('update product warehouse done.')


def update_product_transaction_information():
    for product in Product.objects.all():
        update_product_stock_amount(product_id=product.id)
        update_product_wait_delivery_amount(product_id=product.id)
        update_product_wait_receipt_amount(product_id=product.id)
        product.available_amount = (product.stock_amount - product.wait_delivery_amount + product.wait_receipt_amount)
        product.save(update_fields=['available_amount'])
    print('update_product_transaction_information done.')


def update_product_warehouse_receipt_amount():
    for product_warehouse in ProductWareHouse.objects.all():
        product_warehouse.receipt_amount = 0
        product_warehouse.sold_amount = 0
        product_warehouse.stock_amount = 0
        product_warehouse.save(update_fields=['receipt_amount', 'sold_amount', 'stock_amount'])
    for gr in GoodsReceipt.objects.filter(system_status__in=[2, 3]):
        for gr_warehouse in GoodsReceiptWarehouse.objects.filter(goods_receipt=gr):
            uom_product_inventory = gr_warehouse.goods_receipt_product.product.inventory_uom
            uom_product_gr = gr_warehouse.goods_receipt_product.uom
            if gr_warehouse.goods_receipt_request_product:  # Case has PR
                if gr_warehouse.goods_receipt_request_product.purchase_order_request_product:
                    pr_product = gr_warehouse.goods_receipt_request_product.purchase_order_request_product
                    if pr_product.is_stock is False:  # Case PR is Product
                        if pr_product.purchase_request_product:
                            uom_product_gr = pr_product.purchase_request_product.uom
                    else:  # Case PR is Stock
                        uom_product_gr = pr_product.uom_stock
            final_ratio = 1
            if uom_product_inventory and uom_product_gr:
                final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
            lot_data = []
            serial_data = []
            for lot in gr_warehouse.goods_receipt_lot_gr_warehouse.all():
                if lot.lot:
                    lot.lot.quantity_import += lot.quantity_import * final_ratio
                    lot.lot.save(update_fields=['quantity_import'])
                else:
                    lot_data.append({
                        'lot_number': lot.lot_number,
                        'quantity_import': lot.quantity_import * final_ratio,
                        'expire_date': lot.expire_date,
                        'manufacture_date': lot.manufacture_date,
                    })
            for serial in gr_warehouse.goods_receipt_serial_gr_warehouse.all():
                serial_data.append({
                    'vendor_serial_number': serial.vendor_serial_number,
                    'serial_number': serial.serial_number,
                    'expire_date': serial.expire_date,
                    'manufacture_date': serial.manufacture_date,
                    'warranty_start': serial.warranty_start,
                    'warranty_end': serial.warranty_end,
                })
            ProductWareHouse.push_from_receipt(
                tenant_id=gr.tenant_id,
                company_id=gr.company_id,
                product_id=gr_warehouse.goods_receipt_product.product_id,
                warehouse_id=gr_warehouse.warehouse_id,
                uom_id=uom_product_inventory.id,
                tax_id=gr_warehouse.goods_receipt_product.product.purchase_tax_id,
                amount=gr_warehouse.quantity_import * final_ratio,
                unit_price=gr_warehouse.goods_receipt_product.product_unit_price,
                lot_data=lot_data,
                serial_data=serial_data,
            )
    print('update product warehouse done.')
# END PRODUCT TRANSACTION INFORMATION


# BEGIN INVENTORY
def update_po_request_product_for_gr_request_product():
    for gr_request_product in GoodsReceiptRequestProduct.objects.filter(is_stock=False):
        po_id = gr_request_product.goods_receipt.purchase_order_id
        for item in gr_request_product.purchase_request_product.purchase_order_request_request_product.all():
            if item.purchase_order_id == po_id:
                gr_request_product.purchase_order_request_product_id = item.id
                gr_request_product.save()
                break
    print('update_po_request_product_for_gr_request_product done.')
# END INVENTORY


# BEGIN PURCHASING
def update_is_all_ordered_pr():
    for pr in PurchaseRequest.objects.all():
        pr_product = pr.purchase_request.all()
        pr_product_done = pr.purchase_request.filter(remain_for_purchase_order=0)
        if pr_product.count() == pr_product_done.count():
            pr.purchase_status = 2
            pr.is_all_ordered = True
            pr.save(update_fields=['purchase_status', 'is_all_ordered'])
        else:
            pr.purchase_status = 1
            pr.save(update_fields=['purchase_status'])
    print('update_is_all_ordered_pr done.')


def restart_po_gr_remain_quantity():
    # Restart gr_remain_quantity
    for po_product in PurchaseOrderProduct.objects.filter(purchase_order__system_status__in=[2, 3]):
        po_product.gr_remain_quantity = po_product.product_quantity_order_actual
        po_product.gr_completed_quantity = 0
        po_product.save(update_fields=['gr_remain_quantity', 'gr_completed_quantity'])
    for po_pr_product in PurchaseOrderRequestProduct.objects.filter(purchase_order__system_status__in=[2, 3]):
        po_pr_product.gr_remain_quantity = po_pr_product.quantity_order
        po_pr_product.gr_completed_quantity = 0
        po_pr_product.save(update_fields=['gr_remain_quantity', 'gr_completed_quantity'])
    print('restart_po_gr_remain_quantity done.')


def update_gr_info_for_po():
    # update_gr_info_for_po
    for gr in GoodsReceipt.objects.filter(system_status__in=[2, 3]):
        for gr_po_product in gr.goods_receipt_product_goods_receipt.all():
            if gr_po_product.purchase_order_product:
                gr_po_product.purchase_order_product.gr_completed_quantity += gr_po_product.quantity_import
                gr_po_product.purchase_order_product.gr_completed_quantity = round(
                    gr_po_product.purchase_order_product.gr_completed_quantity,
                    2
                )
                gr_po_product.purchase_order_product.gr_remain_quantity -= gr_po_product.quantity_import
                gr_po_product.purchase_order_product.gr_remain_quantity = round(
                    gr_po_product.purchase_order_product.gr_remain_quantity,
                    2
                )
                gr_po_product.purchase_order_product.save(update_fields=[
                    'gr_completed_quantity',
                    'gr_remain_quantity'
                ])
        for gr_pr_product in gr.goods_receipt_request_product_goods_receipt.all():
            if gr_pr_product.purchase_order_request_product:
                gr_pr_product.purchase_order_request_product.gr_completed_quantity += gr_pr_product.quantity_import
                gr_pr_product.purchase_order_request_product.gr_completed_quantity = round(
                    gr_pr_product.purchase_order_request_product.gr_completed_quantity,
                    2
                )
                gr_pr_product.purchase_order_request_product.gr_remain_quantity -= gr_pr_product.quantity_import
                gr_pr_product.purchase_order_request_product.gr_remain_quantity = round(
                    gr_pr_product.purchase_order_request_product.gr_remain_quantity,
                    2
                )
                gr_pr_product.purchase_order_request_product.save(update_fields=[
                    'gr_completed_quantity',
                    'gr_remain_quantity'
                ])
    #
    for gr in GoodsReceipt.objects.filter(system_status__in=[2, 3]):
        if gr.purchase_order:
            po_product = gr.purchase_order.purchase_order_product_order.all()
            po_product_done = gr.purchase_order.purchase_order_product_order.filter(gr_remain_quantity=0)
            if po_product.count() == po_product_done.count():
                gr.purchase_order.receipt_status = 3
                gr.purchase_order.is_all_receipted = True
                gr.purchase_order.save(update_fields=['receipt_status', 'is_all_receipted'])
            else:
                gr.purchase_order.receipt_status = 2
                gr.purchase_order.save(update_fields=['receipt_status'])
    print('update_gr_info_for_po done.')
# END PURCHASING


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
