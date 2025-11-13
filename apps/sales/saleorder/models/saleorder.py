from django.db import models
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.inventory.models import GoodsRegistration
from apps.sales.saleorder.utils import SOFinishHandler, DocumentChangeHandler, SOHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel, SALE_ORDER_DELIVERY_STATUS, \
    BastionFieldAbstractModel, RecurrenceAbstractModel, CurrencyAbstractModel


# CONFIG
class SaleOrderAppConfig(MasterDataAbstractModel):
    company = models.OneToOneField(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='sales_order_config_detail',
    )
    short_sale_config = models.JSONField(
        default=dict,
        help_text="all config use for Sale Order without Opportunity, data record in ConfigShortSale"
    )
    long_sale_config = models.JSONField(
        default=dict,
        help_text="all config use for Sale Order with Opportunity, data record in ConfigLongSale"
    )

    class Meta:
        verbose_name = 'Sale Order Config'
        verbose_name_plural = 'Sale Order Configs'
        default_permissions = ()
        permissions = ()


class ConfigOrderShortSale(SimpleAbstractModel):
    sale_order_config = models.OneToOneField(
        SaleOrderAppConfig,
        on_delete=models.CASCADE,
        verbose_name="config short sale",
        related_name="sale_order_config_short_sale"
    )
    is_choose_price_list = models.BooleanField(
        default=False,
        help_text="flag to check if user can choose price in price list"
    )
    is_input_price = models.BooleanField(
        default=False,
        help_text="flag to check if user can input price for any product"
    )
    is_discount_on_product = models.BooleanField(
        default=False,
        help_text="flag to check if user can input discount for any product"
    )
    is_discount_on_total = models.BooleanField(
        default=False,
        help_text="flag to check if user can input discount for total of all products"
    )

    class Meta:
        verbose_name = 'Sale Order Short Sale Config'
        verbose_name_plural = 'Sale Order Short Sale Configs'
        default_permissions = ()
        permissions = ()


class ConfigOrderLongSale(SimpleAbstractModel):
    sale_order_config = models.OneToOneField(
        SaleOrderAppConfig,
        on_delete=models.CASCADE,
        verbose_name="config long sale",
        related_name="sale_order_config_long_sale"
    )
    is_not_input_price = models.BooleanField(
        default=False,
        help_text="flag to check if user can input price for any product"
    )
    is_not_discount_on_product = models.BooleanField(
        default=False,
        help_text="flag to check if user can input discount for any product"
    )
    is_not_discount_on_total = models.BooleanField(
        default=False,
        help_text="flag to check if user can input discount for total of all products"
    )

    class Meta:
        verbose_name = 'Sale Order Long Sale Config'
        verbose_name_plural = 'Sale Order Long Sale Configs'
        default_permissions = ()
        permissions = ()


# BEGIN SALE ORDER
class SaleOrder(DataAbstractModel, BastionFieldAbstractModel, RecurrenceAbstractModel, CurrencyAbstractModel):
    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'a870e392-9ad2-4fe2-9baa-298a38691cf2'

    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        verbose_name="opportunity",
        related_name="sale_order_opportunity",
        null=True
    )
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="sale_order_customer",
        null=True,
        help_text="sale data Accounts have type customer"
    )
    customer_data = models.JSONField(default=dict, help_text='data json of customer')
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="sale_order_contact",
        null=True
    )
    contact_data = models.JSONField(default=dict, help_text='data json of contact')
    sale_person = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="sale person",
        related_name="sale_order_sale_person",
        null=True
    )
    payment_term = models.ForeignKey(
        'saledata.PaymentTerm',
        on_delete=models.CASCADE,
        verbose_name="payment term",
        related_name="sale_order_payment_term",
        null=True
    )
    payment_term_data = models.JSONField(
        default=dict,
        help_text="read data payment term, use for get list or detail sale order"
    )
    quotation = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="sale_order_quotation",
        null=True
    )
    quotation_data = models.JSONField(default=dict, help_text='data json of quotation')
    # sale order tabs
    sale_order_products_data = models.JSONField(
        default=list,
        help_text="read data products, use for get list or detail sale order"
    )
    sale_order_logistic_data = models.JSONField(
        default=dict,
        help_text="read data logistics, use for get list or detail sale order"
    )
    customer_shipping = models.ForeignKey(
        'saledata.AccountShippingAddress',
        on_delete=models.SET_NULL,
        verbose_name="sale order shipping",
        related_name="sale_order_customer_shipping",
        null=True
    )
    customer_billing = models.ForeignKey(
        'saledata.AccountBillingAddress',
        on_delete=models.SET_NULL,
        verbose_name="sale order billing",
        related_name="sale_order_customer_billing",
        null=True
    )
    sale_order_costs_data = models.JSONField(
        default=list,
        help_text="read data cost, use for get list or detail sale order"
    )
    sale_order_expenses_data = models.JSONField(
        default=list,
        help_text="read data expense, use for get list or detail sale order"
    )
    sale_order_payment_stage = models.JSONField(
        default=list,
        help_text="read data payment stage, use for get list or detail sale order"
    )
    sale_order_invoice = models.JSONField(
        default=list,
        help_text="read data invoice, use for get list or detail sale order"
    )
    # total amount of products
    total_product_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab product")
    total_product_discount_rate = models.FloatField(default=0, help_text="total discount rate (%) of tab product")
    total_product_discount = models.FloatField(default=0, help_text="total discount of tab product")
    total_product_tax = models.FloatField(default=0, help_text="total tax of tab product")
    total_product = models.FloatField(default=0, help_text="total amount of tab product")
    total_product_revenue_before_tax = models.FloatField(
        default=0,
        help_text="total revenue before tax of tab product (after discount on total, apply promotion,...)"
    )
    # total amount of costs
    total_cost_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab cost")
    total_cost_tax = models.FloatField(default=0, help_text="total tax of tab cost")
    total_cost = models.FloatField(default=0, help_text="total amount of tab cost")
    # total amount of expenses
    total_expense_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab expense")
    total_expense_tax = models.FloatField(default=0, help_text="total tax of tab expense")
    total_expense = models.FloatField(default=0, help_text="total amount of tab expense")
    delivery_call = models.BooleanField(
        default=False,
        verbose_name='Called delivery',
        help_text='State call delivery of this',
    )
    # sale order indicators
    sale_order_indicators_data = models.JSONField(
        default=list,
        help_text="read data indicators, use for get list or detail sale order, records in model SaleOrderIndicator"
    )
    indicator_revenue = models.FloatField(default=0, help_text="value of indicator revenue (IN0001)")
    indicator_gross_profit = models.FloatField(default=0, help_text="value of indicator gross profit (IN0003)")
    indicator_net_income = models.FloatField(default=0, help_text="value of indicator net income (IN0006)")
    # delivery status
    delivery_status = models.SmallIntegerField(choices=SALE_ORDER_DELIVERY_STATUS, default=0)
    has_regis = models.BooleanField(
        default=False,
        help_text='is True if linked with registration else False',
    )
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='SaleOrderAttachment',
        symmetrical=False,
        blank=True,
        related_name='file_of_sale_order',
    )
    date_created = models.DateTimeField(
        default=timezone.now,
        help_text='The record created at value',
    )

    is_done_purchase_request = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Sale Order'
        verbose_name_plural = 'Sale Orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def check_change_document(cls, instance):
        # check if there is CR not done
        if cls.objects.filter_on_company(document_root_id=instance.document_root_id, system_status__in=[1, 2]).exists():
            return False
        # check if SO was used for PR
        if instance.pr_sale_order.filter(system_status__in=[1, 2, 3]).exists():
            return False
        # check delivery (if SO was used for OrderDelivery and all OrderDeliverySub is done => can't change)
        # if hasattr(instance, 'delivery_of_sale_order'):
        #     if not instance.delivery_of_sale_order.delivery_sub_order_delivery.filter(**{
        #         'tenant_id': instance.tenant_id,
        #         'company_id': instance.company_id,
        #         'order_delivery__sale_order_id': instance.id,
        #         'state__in': [0, 1]
        #     }).exists():
        #         return False

        # check delivery (if SO was used for OrderDelivery => can't reject)
        if hasattr(instance, 'delivery_of_sale_order'):
            return False
        return True

    @classmethod
    def check_reject_document(cls, instance):
        # check if there is CR not done
        if cls.objects.filter_on_company(document_root_id=instance.document_root_id, system_status__in=[1, 2]).exists():
            return False
        # check if SO was used for PR
        if instance.pr_sale_order.filter(system_status__in=[1, 2, 3]).exists():
            return False
        # check delivery (if SO was used for OrderDelivery => can't reject)
        if hasattr(instance, 'delivery_of_sale_order'):
            return False
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config(
                        app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                    )
                    if self.opportunity:  # registration
                        GoodsRegistration.check_and_create_goods_registration(self)
                    SOFinishHandler.push_product_info(instance=self)  # product info
                    SOFinishHandler.update_opportunity(instance=self)  # opportunity
                    SOFinishHandler.push_to_customer_activity(instance=self)  # customer
                    SOFinishHandler.push_to_report_revenue(instance=self)  # reports
                    SOFinishHandler.push_to_report_product(instance=self)
                    SOFinishHandler.push_to_report_customer(instance=self)
                    SOFinishHandler.push_to_report_cashflow(instance=self)
                    SOFinishHandler.push_final_acceptance_so(instance=self)  # final acceptance
                    SOFinishHandler.push_to_payment_plan(instance=self)  # payment plan
                    SOFinishHandler.set_true_file_is_approved(instance=self)  # file
                    SOFinishHandler.update_recurrence_task(instance=self)  # recurrence
                    DocumentChangeHandler.change_handle(instance=self)  # change document handle

        if self.system_status in [4]:  # cancel
            # product
            SOFinishHandler.push_product_info(instance=self)
            # opportunity
            SOFinishHandler.update_opportunity(instance=self)
        # opportunity log
        SOHandler.push_opportunity_log(instance=self)
        # diagram
        SOHandler.push_diagram(instance=self)
        # hit DB
        super().save(*args, **kwargs)


# SUPPORT PRODUCTS
class SaleOrderProduct(MasterDataAbstractModel):
    sale_order = models.ForeignKey(
        SaleOrder,
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="sale_order_product_sale_order",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="sale_order_product_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    product_specific = models.ForeignKey(
        'saledata.ProductSpecificIdentificationSerialNumber',
        on_delete=models.CASCADE,
        verbose_name="product specific",
        related_name="sale_order_product_product_specific",
        null=True
    )
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="sale_order_product_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="sale_order_product_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="sale_order_product_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    # product information
    product_title = models.TextField(blank=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_uom_title = models.CharField(max_length=100, blank=True, null=True)
    product_uom_code = models.CharField(max_length=100, blank=True, null=True)
    product_quantity = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
    product_unit_price = models.FloatField(default=0)
    product_discount_value = models.FloatField(default=0)
    product_discount_amount = models.FloatField(default=0)
    product_discount_amount_total = models.FloatField(default=0)
    product_tax_title = models.CharField(max_length=100, blank=True, null=True)
    product_tax_value = models.FloatField(default=0)
    product_tax_amount = models.FloatField(default=0)
    product_subtotal_price = models.FloatField(default=0)
    product_subtotal_price_after_tax = models.FloatField(default=0)
    order = models.IntegerField(default=1)
    is_promotion = models.BooleanField(
        default=False,
        help_text="flag to know this product is for promotion (discount, gift,...)"
    )
    promotion = models.ForeignKey(
        'promotion.Promotion',
        on_delete=models.CASCADE,
        verbose_name="promotion",
        related_name="sale_order_product_promotion",
        null=True
    )
    promotion_data = models.JSONField(default=dict, help_text='data json of promotion')
    is_shipping = models.BooleanField(default=False, help_text="flag to know this product is for shipping fee")
    shipping = models.ForeignKey(
        'saledata.Shipping',
        on_delete=models.CASCADE,
        verbose_name="shipping",
        related_name="sale_order_product_shipping",
        null=True
    )
    shipping_data = models.JSONField(default=dict, help_text='data json of shipping')
    remain_for_purchase_request = models.FloatField(default=0)
    remain_for_purchase_order = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not purchased order yet, update when PO finish"
    )
    is_group = models.BooleanField(default=False, help_text="flag to know product group not product")
    group_title = models.CharField(max_length=100, blank=True, null=True)
    group_order = models.IntegerField(default=1)
    quantity_wo_remain = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not work ordered yet, update when WO finish"
    )

    class Meta:
        verbose_name = 'Sale Order Product'
        verbose_name_plural = 'Sale Order Products'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT LOGISTICS
class SaleOrderLogistic(MasterDataAbstractModel):
    sale_order = models.ForeignKey(
        SaleOrder,
        on_delete=models.CASCADE,
    )
    shipping_address = models.TextField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Sale Order Logistic'
        verbose_name_plural = 'Sale Order Logistics'
        default_permissions = ()
        permissions = ()


# SUPPORT COST
class SaleOrderCost(MasterDataAbstractModel):
    sale_order = models.ForeignKey(
        SaleOrder,
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="sale_order_cost_sale_order",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="sale_order_cost_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="sale_order_cost_warehouse",
        null=True
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="sale_order_cost_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="sale_order_cost_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    # cost information
    product_title = models.TextField(blank=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_uom_title = models.CharField(max_length=100, blank=True, null=True)
    product_uom_code = models.CharField(max_length=100, blank=True, null=True)
    product_quantity = models.FloatField(default=0)
    product_cost_price = models.FloatField(default=0)
    product_tax_title = models.CharField(max_length=100, blank=True, null=True)
    product_tax_value = models.FloatField(default=0)
    product_tax_amount = models.FloatField(default=0)
    product_subtotal_price = models.FloatField(default=0)
    product_subtotal_price_after_tax = models.FloatField(default=0)
    order = models.IntegerField(default=1)
    is_shipping = models.BooleanField(default=False, help_text="flag to know this cost is for shipping fee")
    shipping = models.ForeignKey(
        'saledata.Shipping',
        on_delete=models.CASCADE,
        verbose_name="shipping",
        related_name="sale_order_cost_shipping",
        null=True
    )
    shipping_data = models.JSONField(default=dict, help_text='data json of shipping')
    supplied_by = models.SmallIntegerField(default=0)  # (0: 'purchasing', 1: 'making')

    class Meta:
        verbose_name = 'Sale Order Cost'
        verbose_name_plural = 'Sale Order Costs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT EXPENSE
class SaleOrderExpense(MasterDataAbstractModel):
    sale_order = models.ForeignKey(
        SaleOrder,
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="sale_order_expense_sale_order",
        null=True
    )
    expense = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.CASCADE,
        verbose_name="expense",
        related_name="sale_order_expense_expense",
        null=True
    )
    expense_data = models.JSONField(default=dict, help_text='data json of expense')
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        verbose_name="expense item",
        related_name="sale_order_expense_expense_item",
        null=True
    )
    expense_item_data = models.JSONField(default=dict, help_text='data json of expense_item')
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="sale_order_expense_product",
        null=True
    )
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="sale_order_expense_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="sale_order_expense_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    # expense information
    expense_title = models.CharField(max_length=100, blank=True, null=True)
    expense_code = models.CharField(max_length=100, blank=True, null=True)
    product_title = models.TextField(blank=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)
    expense_type_title = models.CharField(max_length=100, blank=True, null=True)
    expense_uom_title = models.CharField(max_length=100, blank=True, null=True)
    expense_uom_code = models.CharField(max_length=100, blank=True, null=True)
    expense_quantity = models.FloatField(default=0)
    expense_price = models.FloatField(default=0)
    expense_tax_title = models.CharField(max_length=100, blank=True, null=True)
    expense_tax_value = models.FloatField(default=0)
    expense_tax_amount = models.FloatField(default=0)
    expense_subtotal_price = models.FloatField(default=0)
    expense_subtotal_price_after_tax = models.FloatField(default=0)
    order = models.IntegerField(default=1)
    is_product = models.BooleanField(
        default=False,
        help_text='flag to check if record is MasterData Expense or Product, if True is Product'
    )
    is_labor = models.BooleanField(
        default=False,
        help_text="flag to check if record is MasterData Internal Labor Item (model Expense)"
    )

    class Meta:
        verbose_name = 'Sale Order Expense'
        verbose_name_plural = 'Sale Order Expenses'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT PAYMENT TERM STAGE
class SaleOrderPaymentStage(MasterDataAbstractModel):
    sale_order = models.ForeignKey(
        SaleOrder,
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="sale_order_payment_stage_sale_order",
    )
    remark = models.CharField(verbose_name='remark', max_length=500, blank=True, null=True)
    term = models.ForeignKey(
        'saledata.Term',
        on_delete=models.SET_NULL,
        verbose_name="payment term",
        related_name="sale_order_payment_stage_term",
        null=True
    )
    term_data = models.JSONField(default=dict)
    date = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)
    date_type = models.CharField(max_length=200, blank=True)
    ratio = models.FloatField(null=True)
    invoice = models.IntegerField(null=True)
    invoice_data = models.JSONField(default=dict, help_text='data json of invoice')
    value_before_tax = models.FloatField(default=0)
    value_reconcile = models.FloatField(default=0)
    reconcile_data = models.JSONField(default=list, help_text='data json of reconcile')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="sale_order_payment_stage_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    value_tax = models.FloatField(default=0)
    value_total = models.FloatField(default=0)
    is_ar_invoice = models.BooleanField(default=False)
    order = models.IntegerField(default=1)
    cash_inflow_done = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Sale Order Payment Stage'
        verbose_name_plural = 'Sale Order Payment Stages'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class SaleOrderInvoice(MasterDataAbstractModel):
    sale_order = models.ForeignKey(
        SaleOrder,
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="sale_order_invoice_sale_order",
    )
    remark = models.CharField(verbose_name='remark', max_length=500, blank=True, null=True)
    date = models.DateTimeField(null=True)
    term_data = models.JSONField(default=list, help_text='data json of terms')
    ratio = models.FloatField(null=True)
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="sale_order_invoice_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    total = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Sale Order Invoice'
        verbose_name_plural = 'Sale Order Invoices'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class SaleOrderAttachment(M2MFilesAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="sale_order_attachment_sale_order",
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'sale_order'

    class Meta:
        verbose_name = 'Sale order attachment'
        verbose_name_plural = 'Sale order attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
