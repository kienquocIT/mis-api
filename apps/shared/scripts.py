from apps.core.company.models import Company
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models.product import ProductType, Product
from apps.masterdata.saledata.models.price import TaxCategory, Currency, Price
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import AccountType, Account

from .extends.signals import SaleDefaultData, ConfigDefaultData
from ..core.base.models import PlanApplication
from ..core.tenant.models import Tenant, TenantPlan
from ..sales.cashoutflow.models import (
    AdvancePayment, AdvancePaymentCost,
    ReturnAdvance, ReturnAdvanceCost,
    Payment, PaymentCost, PaymentCostItems, PaymentCostItemsDetail, PaymentQuotation, PaymentSaleOrder
)
from ..core.workflow.models import WorkflowConfigOfApp, Workflow, Runtime
from ..masterdata.saledata.models import ConditionLocation, FormulaCondition, ShippingCondition, Shipping


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
            for app in app_objs:
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


def set_null_contact_owner():
    list_id = ["d0775ed8-93c6-4e3f-9325-a65fd9131472", "7dcaeee9-af82-4dc8-94d3-a1e09acdbf1a",
               "7dcaeee9-af82-4dc8-94d3-a1e09acdbf1a", "d0775ed8-93c6-4e3f-9325-a65fd9131472",
               "f7230502-922b-4285-b14a-0f08b244c818", "f7230502-922b-4285-b14a-0f08b244c818",
               "f0933e51-8b6b-4dd6-9a7d-b6777d49b333", "5b0311d4-c1d0-467e-89c4-028498988b63",
               "fa5e3399-e32e-4263-bf96-171f0c856288", "d0775ed8-93c6-4e3f-9325-a65fd9131472"]
    contact = Contact.objects.filter(owner__in=list_id)
    if contact:
        contact.update(owner=None)
    print("update contact_owner done.")
    return True
