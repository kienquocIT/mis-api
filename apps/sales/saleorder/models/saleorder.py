from django.db import models

from apps.core.company.models import CompanyFunctionNumber
from apps.sales.acceptance.models import FinalAcceptance
from apps.sales.report.models import ReportRevenue, ReportCustomer, ReportProduct, ReportCashflow
from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel, SALE_ORDER_DELIVERY_STATUS, \
    PAYMENT_TERM_STAGE


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
class SaleOrder(DataAbstractModel):
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
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="sale_order_contact",
        null=True
    )
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
    quotation = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="sale_order_quotation",
        null=True
    )
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
    # total amount of products
    total_product_pretax_amount = models.FloatField(
        default=0,
        help_text="total pretax amount of tab product"
    )
    total_product_discount_rate = models.FloatField(
        default=0,
        help_text="total discount rate (%) of tab product"
    )
    total_product_discount = models.FloatField(
        default=0,
        help_text="total discount of tab product"
    )
    total_product_tax = models.FloatField(
        default=0,
        help_text="total tax of tab product"
    )
    total_product = models.FloatField(
        default=0,
        help_text="total amount of tab product"
    )
    total_product_revenue_before_tax = models.FloatField(
        default=0,
        help_text="total revenue before tax of tab product (after discount on total, apply promotion,...)"
    )
    # total amount of costs
    total_cost_pretax_amount = models.FloatField(
        default=0,
        help_text="total pretax amount of tab cost"
    )
    total_cost_tax = models.FloatField(
        default=0,
        help_text="total tax of tab cost"
    )
    total_cost = models.FloatField(
        default=0,
        help_text="total amount of tab cost"
    )
    # total amount of expenses
    total_expense_pretax_amount = models.FloatField(
        default=0,
        help_text="total pretax amount of tab expense"
    )
    total_expense_tax = models.FloatField(
        default=0,
        help_text="total tax of tab expense"
    )
    total_expense = models.FloatField(
        default=0,
        help_text="total amount of tab expense"
    )
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
    indicator_revenue = models.FloatField(
        default=0,
        help_text="value of indicator revenue (IN0001)",
    )
    indicator_gross_profit = models.FloatField(
        default=0,
        help_text="value of indicator gross profit (IN0003)",
    )
    indicator_net_income = models.FloatField(
        default=0,
        help_text="value of indicator net income (IN0006)",
    )
    # delivery status
    delivery_status = models.SmallIntegerField(
        choices=SALE_ORDER_DELIVERY_STATUS,
        default=0
    )

    class Meta:
        verbose_name = 'Sale Order'
        verbose_name_plural = 'Sale Orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("OR")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            # code = 'OR0001-' + StringHandler.random_str(17)
            code = 'OR0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'OR{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def update_product_wait_delivery_amount(cls, instance):
        for product_order in instance.sale_order_product_sale_order.all():
            if product_order.product:
                uom_product_inventory = product_order.product.inventory_uom
                uom_product_so = product_order.unit_of_measure
                final_ratio = 1
                if uom_product_inventory and uom_product_so:
                    final_ratio = uom_product_so.ratio / uom_product_inventory.ratio
                product_order.product.save(**{
                    'update_transaction_info': True,
                    'quantity_order': product_order.product_quantity * final_ratio,
                    'update_fields': ['wait_delivery_amount', 'available_amount']
                })
        return True

    @classmethod
    def push_to_report_revenue(cls, instance):
        revenue_obj = instance.sale_order_indicator_sale_order.filter(code='IN0001').first()
        gross_profit_obj = instance.sale_order_indicator_sale_order.filter(code='IN0003').first()
        net_income_obj = instance.sale_order_indicator_sale_order.filter(code='IN0006').first()
        ReportRevenue.push_from_so(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            sale_order_id=instance.id,
            employee_created_id=instance.employee_created_id,
            employee_inherit_id=instance.employee_inherit_id,
            group_inherit_id=instance.employee_inherit.group_id,
            date_approved=instance.date_approved,
            revenue=revenue_obj.indicator_value if revenue_obj else 0,
            gross_profit=gross_profit_obj.indicator_value if gross_profit_obj else 0,
            net_income=net_income_obj.indicator_value if net_income_obj else 0,
        )
        return True

    @classmethod
    def push_to_report_product(cls, instance):
        revenue_obj = instance.sale_order_indicator_sale_order.filter(code='IN0001').first()
        gross_profit_obj = instance.sale_order_indicator_sale_order.filter(code='IN0003').first()
        net_income_obj = instance.sale_order_indicator_sale_order.filter(code='IN0006').first()
        gross_profit_rate = 0
        if revenue_obj and gross_profit_obj:
            gross_profit_rate = (gross_profit_obj.indicator_value / revenue_obj.indicator_value) * 100
        net_income_rate = 0
        if revenue_obj and net_income_obj:
            net_income_rate = (net_income_obj.indicator_value / revenue_obj.indicator_value) * 100
        for so_product in instance.sale_order_product_sale_order.filter(is_promotion=False, is_shipping=False):
            revenue = (so_product.product_unit_price - so_product.product_discount_amount) * so_product.product_quantity
            gross_profit = (revenue * gross_profit_rate) / 100
            net_income = (revenue * net_income_rate) / 100
            ReportProduct.push_from_so(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product_id=so_product.product_id,
                employee_created_id=instance.employee_created_id,
                employee_inherit_id=instance.employee_inherit_id,
                group_inherit_id=instance.employee_inherit.group_id,
                date_approved=instance.date_approved,
                revenue=revenue,
                gross_profit=gross_profit,
                net_income=net_income,
            )
        return True

    @classmethod
    def push_to_report_customer(cls, instance):
        revenue_obj = instance.sale_order_indicator_sale_order.filter(code='IN0001').first()
        gross_profit_obj = instance.sale_order_indicator_sale_order.filter(code='IN0003').first()
        net_income_obj = instance.sale_order_indicator_sale_order.filter(code='IN0006').first()
        ReportCustomer.push_from_so(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            customer_id=instance.customer_id,
            employee_created_id=instance.employee_created_id,
            employee_inherit_id=instance.employee_inherit_id,
            group_inherit_id=instance.employee_inherit.group_id,
            date_approved=instance.date_approved,
            revenue=revenue_obj.indicator_value if revenue_obj else 0,
            gross_profit=gross_profit_obj.indicator_value if gross_profit_obj else 0,
            net_income=net_income_obj.indicator_value if net_income_obj else 0,
        )
        return True

    @classmethod
    def push_to_report_cashflow(cls, instance):
        bulk_data = [ReportCashflow(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            sale_order_id=instance.id,
            cashflow_type=2,
            employee_inherit_id=instance.employee_inherit_id,
            group_inherit_id=instance.employee_inherit.group_id,
            due_date=payment_stage.due_date,
            value_estimate_sale=payment_stage.value_before_tax,
        ) for payment_stage in instance.payment_stage_sale_order.all()]
        ReportCashflow.push_from_so_po(bulk_data)
        return True

    @classmethod
    def push_to_final_acceptance(cls, instance):
        list_data_indicator = [
            {
                'tenant_id': instance.tenant_id,
                'company_id': instance.company_id,
                'sale_order_id': instance.id,
                'sale_order_indicator_id': so_ind.id,
                'indicator_id': so_ind.quotation_indicator_id,
                'indicator_value': so_ind.indicator_value,
                'different_value': 0 - so_ind.indicator_value,
                'rate_value': 100 if so_ind.quotation_indicator.code == 'IN0001' else 0,
                'order': so_ind.order,
                'is_indicator': True,
            }
            for so_ind in instance.sale_order_indicator_sale_order.all()
        ]
        FinalAcceptance.create_final_acceptance_from_so(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            sale_order_id=instance.id,
            employee_created_id=instance.employee_created_id,
            employee_inherit_id=instance.employee_inherit_id,
            opportunity_id=instance.opportunity_id,
            list_data_indicator=list_data_indicator
        )
        return True

    @classmethod
    def update_opportunity_stage_by_so(cls, instance):
        if instance.opportunity:
            instance.opportunity.save(**{
                'sale_order_status': instance.system_status,
            })
        return True

    def save(self, *args, **kwargs):
        # if self.system_status == 2:  # added
        if self.system_status in [2, 3]:  # added, finish
            # check if not code then generate code
            if not self.code:
                code_generated = CompanyFunctionNumber.gen_code(company_obj=self.company, func=2)
                if code_generated:
                    self.code = code_generated
                else:
                    self.code = self.generate_code(self.company_id)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
            # check if date_approved then call related functions
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    if 'date_approved' in kwargs['update_fields']:
                        self.update_product_wait_delivery_amount(self)
                        # opportunity
                        self.update_opportunity_stage_by_so(self)
                        # reports
                        self.push_to_report_revenue(self)
                        self.push_to_report_product(self)
                        self.push_to_report_customer(self)
                        self.push_to_report_cashflow(self)
                        # final acceptance
                        self.push_to_final_acceptance(self)

        # hit DB
        super().save(*args, **kwargs)


# SUPPORT PRODUCTS
class SaleOrderProduct(SimpleAbstractModel):
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
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="sale_order_product_uom",
        null=True
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="sale_order_product_tax",
        null=True
    )
    # product information
    product_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_description = models.TextField(
        blank=True,
        null=True
    )
    product_uom_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_uom_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_quantity = models.FloatField(
        default=0
    )
    product_unit_price = models.FloatField(
        default=0
    )
    product_discount_value = models.FloatField(
        default=0
    )
    product_discount_amount = models.FloatField(
        default=0
    )
    product_tax_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_tax_value = models.FloatField(
        default=0
    )
    product_tax_amount = models.FloatField(
        default=0
    )
    product_subtotal_price = models.FloatField(
        default=0
    )
    product_subtotal_price_after_tax = models.FloatField(
        default=0
    )
    order = models.IntegerField(
        default=1
    )
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
    is_shipping = models.BooleanField(
        default=False,
        help_text="flag to know this product is for shipping fee"
    )
    shipping = models.ForeignKey(
        'saledata.Shipping',
        on_delete=models.CASCADE,
        verbose_name="shipping",
        related_name="sale_order_product_shipping",
        null=True
    )

    remain_for_purchase_request = models.FloatField(
        default=0,
    )
    remain_for_purchase_order = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not purchased order yet, update when PO finish"
    )

    class Meta:
        verbose_name = 'Sale Order Product'
        verbose_name_plural = 'Sale Order Products'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT LOGISTICS
class SaleOrderLogistic(SimpleAbstractModel):
    sale_order = models.ForeignKey(
        SaleOrder,
        on_delete=models.CASCADE,
    )
    shipping_address = models.TextField(
        blank=True,
        null=True
    )
    billing_address = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Sale Order Logistic'
        verbose_name_plural = 'Sale Order Logistics'
        default_permissions = ()
        permissions = ()


# SUPPORT COST
class SaleOrderCost(SimpleAbstractModel):
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
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="sale_order_cost_uom",
        null=True
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="sale_order_cost_tax",
        null=True
    )
    # cost information
    product_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_uom_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_uom_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_quantity = models.FloatField(
        default=0
    )
    product_cost_price = models.FloatField(
        default=0
    )
    product_tax_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_tax_value = models.FloatField(
        default=0
    )
    product_tax_amount = models.FloatField(
        default=0
    )
    product_subtotal_price = models.FloatField(
        default=0
    )
    product_subtotal_price_after_tax = models.FloatField(
        default=0
    )
    order = models.IntegerField(
        default=1
    )
    is_shipping = models.BooleanField(
        default=False,
        help_text="flag to know this cost is for shipping fee"
    )
    shipping = models.ForeignKey(
        'saledata.Shipping',
        on_delete=models.CASCADE,
        verbose_name="shipping",
        related_name="sale_order_cost_shipping",
        null=True
    )

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
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        verbose_name="expense item",
        related_name="sale_order_expense_expense_item",
        null=True
    )
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
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="sale_order_expense_tax",
        null=True
    )
    # expense information
    expense_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    expense_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    expense_type_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    expense_uom_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    expense_uom_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    expense_quantity = models.FloatField(
        default=0
    )
    expense_price = models.FloatField(
        default=0
    )
    expense_tax_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    expense_tax_value = models.FloatField(
        default=0
    )
    expense_tax_amount = models.FloatField(
        default=0
    )
    expense_subtotal_price = models.FloatField(
        default=0
    )
    expense_subtotal_price_after_tax = models.FloatField(
        default=0
    )
    order = models.IntegerField(
        default=1
    )
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
        related_name="payment_stage_sale_order",
    )
    stage = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(PAYMENT_TERM_STAGE),
    )
    remark = models.CharField(verbose_name='remark', max_length=500, blank=True, null=True)
    date = models.DateTimeField(null=True)
    date_type = models.SmallIntegerField(default=0)
    number_of_day = models.IntegerField(default=0, help_text='number of days before due date')
    payment_ratio = models.FloatField(default=0)
    value_before_tax = models.FloatField(default=0)
    due_date = models.DateTimeField(null=True)
    is_ar_invoice = models.BooleanField(default=False)
    order = models.IntegerField(default=1)
    is_balance = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Sale Order Payment Stage'
        verbose_name_plural = 'Sale Order Payment Stages'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
