from django.db import models

from apps.core.company.models import CompanyFunctionNumber
from apps.sales.leaseorder.utils.logical import LOHandler
from apps.sales.leaseorder.utils.logical_finish import LOFinishHandler
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SALE_ORDER_DELIVERY_STATUS, \
    BastionFieldAbstractModel, RecurrenceAbstractModel, ASSET_TYPE


# BEGIN LEASE ORDER
class LeaseOrder(DataAbstractModel, BastionFieldAbstractModel, RecurrenceAbstractModel):
    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return '010404b3-bb91-4b24-9538-075f5f00ef14'

    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        verbose_name="opportunity",
        related_name="lease_opportunity",
        null=True
    )
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="lease_customer",
        null=True,
        help_text="sale data Accounts have type customer"
    )
    customer_data = models.JSONField(default=dict, help_text='data json of customer')
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="lease_contact",
        null=True
    )
    contact_data = models.JSONField(default=dict, help_text='data json of contact')
    sale_person = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="sale person",
        related_name="lease_sale_person",
        null=True
    )
    payment_term = models.ForeignKey(
        'saledata.PaymentTerm',
        on_delete=models.CASCADE,
        verbose_name="payment term",
        related_name="lease_payment_term",
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
        related_name="lease_quotation",
        null=True
    )
    quotation_data = models.JSONField(default=dict, help_text='data json of quotation')
    lease_from = models.DateField(null=True)
    lease_to = models.DateField(null=True)
    # sale order tabs
    lease_products_data = models.JSONField(
        default=list,
        help_text="read data products, use for get list or detail sale order"
    )
    lease_logistic_data = models.JSONField(
        default=dict,
        help_text="read data logistics, use for get list or detail sale order"
    )
    customer_shipping = models.ForeignKey(
        'saledata.AccountShippingAddress',
        on_delete=models.SET_NULL,
        verbose_name="lease order shipping",
        related_name="lease_customer_shipping",
        null=True
    )
    customer_billing = models.ForeignKey(
        'saledata.AccountBillingAddress',
        on_delete=models.SET_NULL,
        verbose_name="lease order billing",
        related_name="lease_customer_billing",
        null=True
    )
    lease_costs_data = models.JSONField(
        default=list,
        help_text="read data cost, use for get list or detail sale order"
    )
    lease_expenses_data = models.JSONField(
        default=list,
        help_text="read data expense, use for get list or detail sale order"
    )
    lease_payment_stage = models.JSONField(
        default=list,
        help_text="read data payment stage, use for get list or detail sale order"
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
    lease_indicators_data = models.JSONField(
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

    class Meta:
        verbose_name = 'Lease Order'
        verbose_name_plural = 'Lease Orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("LO")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(codes=existing_codes)
        if num_max is None:
            code = 'LO0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'LO{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_code(cls, instance, kwargs):
        if not instance.code:
            code_generated = CompanyFunctionNumber.gen_code(company_obj=instance.company, func=2)
            instance.code = code_generated if code_generated else cls.generate_code(company_id=instance.company_id)
            kwargs['update_fields'].append('code')
        return True

    @classmethod
    def check_change_document(cls, instance):
        if not instance:
            return False
        return True

    @classmethod
    def check_reject_document(cls, instance):
        if not instance:
            return False
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    self.push_code(instance=self, kwargs=kwargs)  # code
                    LOFinishHandler.push_product_info(instance=self)  # product info

                    LOFinishHandler.push_final_acceptance_lo(instance=self)  # final acceptance
                    LOFinishHandler.update_recurrence_task(instance=self)  # recurrence

        if self.system_status in [4]:  # cancel
            ...
        # opportunity log
        LOHandler.push_opportunity_log(instance=self)
        # hit DB
        super().save(*args, **kwargs)


# SUPPORT PRODUCTS
class LeaseOrderProduct(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_product_lease_order",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_product_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    asset_type = models.SmallIntegerField(default=0, help_text='choices= ' + str(ASSET_TYPE))
    offset = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_product_offset",
        null=True
    )
    offset_data = models.JSONField(default=dict, help_text='data json of offset')
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="lease_order_product_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="lease_order_product_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="lease_order_product_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    # product information
    product_title = models.CharField(max_length=100, blank=True, null=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_uom_title = models.CharField(max_length=100, blank=True, null=True)
    product_uom_code = models.CharField(max_length=100, blank=True, null=True)
    product_quantity = models.FloatField(default=0)
    product_quantity_new = models.FloatField(default=0)
    product_quantity_leased = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
    product_unit_price = models.FloatField(default=0)
    product_discount_value = models.FloatField(default=0)
    product_discount_amount = models.FloatField(default=0)
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
        related_name="lease_order_product_promotion",
        null=True
    )
    promotion_data = models.JSONField(default=dict, help_text='data json of promotion')
    is_shipping = models.BooleanField(default=False, help_text="flag to know this product is for shipping fee")
    shipping = models.ForeignKey(
        'saledata.Shipping',
        on_delete=models.CASCADE,
        verbose_name="shipping",
        related_name="lease_order_product_shipping",
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
        verbose_name = 'Lease Order Product'
        verbose_name_plural = 'Lease Order Products'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT LOGISTICS
class LeaseOrderLogistic(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
    )
    shipping_address = models.TextField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Lease Order Logistic'
        verbose_name_plural = 'Lease Order Logistics'
        default_permissions = ()
        permissions = ()


# SUPPORT COST
class LeaseOrderCost(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_cost_lease_order",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_cost_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="lease_order_cost_warehouse",
        null=True
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="lease_order_cost_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="lease_order_cost_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="lease_order_cost_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    # cost information
    product_title = models.CharField(max_length=100, blank=True, null=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)
    product_uom_title = models.CharField(max_length=100, blank=True, null=True)
    product_uom_code = models.CharField(max_length=100, blank=True, null=True)
    product_quantity = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
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
        related_name="lease_order_cost_shipping",
        null=True
    )
    shipping_data = models.JSONField(default=dict, help_text='data json of shipping')
    supplied_by = models.SmallIntegerField(default=0)  # (0: 'purchasing', 1: 'making')

    class Meta:
        verbose_name = 'Lease Order Cost'
        verbose_name_plural = 'Lease Order Costs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT EXPENSE
class LeaseOrderExpense(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_expense_lease_order",
        null=True
    )
    expense = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.CASCADE,
        verbose_name="expense",
        related_name="lease_order_expense_expense",
        null=True
    )
    expense_data = models.JSONField(default=dict, help_text='data json of expense')
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        verbose_name="expense item",
        related_name="lease_order_expense_expense_item",
        null=True
    )
    expense_item_data = models.JSONField(default=dict, help_text='data json of expense_item')
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="lease_order_expense_product",
        null=True
    )
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="lease_order_expense_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="lease_order_expense_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    # expense information
    expense_title = models.CharField(max_length=100, blank=True, null=True)
    expense_code = models.CharField(max_length=100, blank=True, null=True)
    product_title = models.CharField(max_length=100, blank=True, null=True)
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
        verbose_name = 'Lease Order Expense'
        verbose_name_plural = 'Lease Order Expenses'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT PAYMENT TERM STAGE
class LeaseOrderPaymentStage(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        LeaseOrder,
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="payment_stage_lease_order",
    )
    remark = models.CharField(verbose_name='remark', max_length=500, blank=True, null=True)
    term = models.ForeignKey(
        'saledata.Term',
        on_delete=models.SET_NULL,
        verbose_name="payment term",
        related_name="lease_payment_stage_term",
        null=True
    )
    term_data = models.JSONField(default=dict)
    date = models.DateTimeField(null=True)
    date_type = models.CharField(max_length=200, blank=True)
    payment_ratio = models.FloatField(default=0)
    value_before_tax = models.FloatField(default=0)
    issue_invoice = models.IntegerField(null=True)
    value_after_tax = models.FloatField(default=0)
    value_total = models.FloatField(default=0)
    due_date = models.DateTimeField(null=True)
    is_ar_invoice = models.BooleanField(default=False)
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Lease Order Payment Stage'
        verbose_name_plural = 'Lease Order Payment Stages'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
