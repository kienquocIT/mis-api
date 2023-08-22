from apps.core.company.models import Company
from apps.masterdata.saledata.models.product import ProductType, Product, ExpensePrice, ProductCategory, UnitOfMeasure
from apps.masterdata.saledata.models.price import TaxCategory, Currency, Price, UnitOfMeasureGroup, Tax, \
    PriceListCurrency
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import AccountType, Account

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
from ..core.hr.models import Employee, Role
from ..sales.delivery.models import OrderDelivery, OrderDeliverySub, OrderPicking, OrderPickingSub
from ..sales.opportunity.models import Opportunity, OpportunityConfigStage, OpportunityStage, OpportunityCallLog
from ..sales.purchasing.models import PurchaseRequestProduct
from ..sales.quotation.models import QuotationIndicatorConfig, Quotation
from ..sales.saleorder.models import SaleOrderIndicatorConfig, SaleOrderProduct, SaleOrder
from ..sales.task.models import OpportunityTaskStatus, OpportunityTaskConfig


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


def delete_delivery_picking():
    # delete delivery
    order_delivery = OrderDelivery.objects.all()
    order_delivery.update(sub=None)
    OrderDeliverySub.objects.all().delete()
    order_delivery.delete()

    # delete picking
    order_picking = OrderPicking.objects.all()
    order_picking.update(sub=None)
    OrderPickingSub.objects.all().delete()
    order_picking.delete()

    # reset warehouse
    ProductWareHouse.objects.all().update(sold_amount=0, picked_ready=0)
    print("delete done.")


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
