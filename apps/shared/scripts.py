from apps.core.company.models import Company
from apps.masterdata.saledata.models.product import ProductType, Product
from apps.masterdata.saledata.models.price import TaxCategory, Currency, Price
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import AccountType, Account

from apps.core.base.models import PlanApplication, ApplicationProperty
from apps.core.tenant.models import Tenant, TenantPlan
from apps.sales.cashoutflow.models import (
    AdvancePayment, AdvancePaymentCost,
    ReturnAdvance, ReturnAdvanceCost,
    Payment, PaymentCost, PaymentCostItems, PaymentCostItemsDetail, PaymentQuotation, PaymentSaleOrder,
)
from apps.core.workflow.models import WorkflowConfigOfApp, Workflow, Runtime, RuntimeStage, RuntimeAssignee, RuntimeLog
from apps.masterdata.saledata.models import ConditionLocation, FormulaCondition, ShippingCondition, Shipping, \
    ProductWareHouse
from . import MediaForceAPI

from .extends.signals import SaleDefaultData, ConfigDefaultData
from ..sales.delivery.models import OrderDelivery, OrderDeliverySub, OrderPicking, OrderPickingSub
from ..sales.opportunity.models import Opportunity, OpportunityConfigStage, OpportunityStage
from ..sales.quotation.models import QuotationIndicatorConfig
from ..sales.saleorder.models import SaleOrderIndicatorConfig


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
