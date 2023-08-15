from django.db import models

from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel


# CONFIG
class QuotationAppConfig(SimpleAbstractModel):
    company = models.OneToOneField(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='sales_quotation_config_detail',
    )
    short_sale_config = models.JSONField(
        default=dict,
        help_text="all config use for Quotation without Opportunity, data record in ConfigShortSale"
    )
    long_sale_config = models.JSONField(
        default=dict,
        help_text="all config use for Quotation with Opportunity, data record in ConfigLongSale"
    )

    class Meta:
        verbose_name = 'Quotation Config'
        verbose_name_plural = 'Quotation Configs'
        default_permissions = ()
        permissions = ()


class ConfigShortSale(SimpleAbstractModel):
    quotation_config = models.OneToOneField(
        QuotationAppConfig,
        on_delete=models.CASCADE,
        verbose_name="config short sale",
        related_name="quotation_config_short_sale"
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
        verbose_name = 'Quotation Short Sale Config'
        verbose_name_plural = 'Quotation Short Sale Configs'
        default_permissions = ()
        permissions = ()


class ConfigLongSale(SimpleAbstractModel):
    quotation_config = models.OneToOneField(
        QuotationAppConfig,
        on_delete=models.CASCADE,
        verbose_name="config long sale",
        related_name="quotation_config_long_sale"
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
        verbose_name = 'Quotation Long Sale Config'
        verbose_name_plural = 'Quotation Long Sale Configs'
        default_permissions = ()
        permissions = ()


# BEGIN QUOTATION
class Quotation(DataAbstractModel):
    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        verbose_name="opportunity",
        related_name="quotation_opportunity",
        null=True
    )
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="quotation_customer",
        null=True,
        help_text="sale data Accounts have type customer"
    )
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="quotation_contact",
        null=True
    )
    sale_person = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="sale person",
        related_name="quotation_sale_person",
        null=True
    )
    payment_term = models.ForeignKey(
        'saledata.PaymentTerm',
        on_delete=models.CASCADE,
        verbose_name="payment term",
        related_name="quotation_payment_term",
        null=True
    )
    # quotation tabs
    quotation_products_data = models.JSONField(
        default=list,
        help_text="read data products, use for get list or detail quotation"
    )
    quotation_term_data = models.JSONField(
        default=dict,
        help_text="read data terms, use for get list or detail quotation"
    )
    quotation_logistic_data = models.JSONField(
        default=dict,
        help_text="read data logistics, use for get list or detail quotation"
    )
    customer_shipping = models.ForeignKey(
        'saledata.AccountShippingAddress',
        on_delete=models.CASCADE,
        verbose_name="customer shipping",
        related_name="quotation_customer_shipping",
        null=True
    )
    customer_billing = models.ForeignKey(
        'saledata.AccountBillingAddress',
        on_delete=models.CASCADE,
        verbose_name="customer billing",
        related_name="quotation_customer_billing",
        null=True
    )
    quotation_costs_data = models.JSONField(
        default=list,
        help_text="read data cost, use for get list or detail quotation"
    )
    quotation_expenses_data = models.JSONField(
        default=list,
        help_text="read data expense, use for get list or detail quotation"
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
    is_customer_confirm = models.BooleanField(
        default=False,
        help_text="flag to check customer confirm quotation"
    )
    # quotation indicators
    quotation_indicators_data = models.JSONField(
        default=list,
        help_text="read data indicators, use for get list or detail quotation, records in model QuotationIndicator"
    )

    class Meta:
        verbose_name = 'Quotation'
        verbose_name_plural = 'Quotations'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        # auto create code (temporary)
        quotation = Quotation.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "QUO"
        if not self.code:
            temper = "%04d" % (quotation + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code

        # hit DB
        super().save(*args, **kwargs)


# SUPPORT PRODUCTS
class QuotationProduct(SimpleAbstractModel):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_product_quotation",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_product_product",
        null=True
    )
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="quotation_product_uom",
        null=True
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="quotation_product_tax",
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
        related_name="quotation_product_promotion",
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
        related_name="quotation_product_shipping",
        null=True
    )

    class Meta:
        verbose_name = 'Quotation Product'
        verbose_name_plural = 'Quotation Products'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT TERMS
class QuotationTerm(SimpleAbstractModel):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
    )
    price_list = models.ManyToManyField(
        'saledata.Price',
        through='QuotationTermPrice',
        symmetrical=False,
        related_name='quotation_term_map_prices',
    )
    discount_list = models.ManyToManyField(
        'saledata.Discount',
        through='QuotationTermDiscount',
        symmetrical=False,
        related_name='quotation_term_map_discounts',
    )
    payment_term = models.ForeignKey(
        'saledata.PaymentTerm',
        on_delete=models.CASCADE,
        verbose_name="payment terms",
        related_name="quotation_term_payment_term",
        null=True
    )

    class Meta:
        verbose_name = 'Quotation Term'
        verbose_name_plural = 'Quotation Terms'
        default_permissions = ()
        permissions = ()


class QuotationTermPrice(SimpleAbstractModel):
    quotation_term = models.ForeignKey(
        QuotationTerm,
        on_delete=models.CASCADE,
    )
    price = models.ForeignKey(
        'saledata.Price',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Quotation Term Price'
        verbose_name_plural = 'Quotation Term Prices'
        default_permissions = ()
        permissions = ()


class QuotationTermDiscount(SimpleAbstractModel):
    quotation_term = models.ForeignKey(
        QuotationTerm,
        on_delete=models.CASCADE,
    )
    discount = models.ForeignKey(
        'saledata.Discount',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Quotation Term Discount'
        verbose_name_plural = 'Quotation Term Discounts'
        default_permissions = ()
        permissions = ()


# SUPPORT LOGISTICS
class QuotationLogistic(SimpleAbstractModel):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
    )
    # shipping_address_list = models.ManyToManyField(
    #     'saledata.AccountShipping',
    #     through='QuotationLogisticShipping',
    #     symmetrical=False,
    #     related_name='quotation_logistic_map_shipping',
    # )
    # billing_address_list = models.ManyToManyField(
    #     'saledata.AccountBilling',
    #     through='QuotationLogisticBilling',
    #     symmetrical=False,
    #     related_name='quotation_logistic_map_billing',
    # )

    shipping_address = models.TextField(
        blank=True,
        null=True
    )
    billing_address = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Quotation Logistic'
        verbose_name_plural = 'Quotation Logistics'
        default_permissions = ()
        permissions = ()


# SUPPORT COST
class QuotationCost(SimpleAbstractModel):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_cost_quotation",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_cost_product",
        null=True
    )
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="quotation_cost_uom",
        null=True
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="quotation_cost_tax",
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
        related_name="quotation_cost_shipping",
        null=True
    )

    class Meta:
        verbose_name = 'Quotation Cost'
        verbose_name_plural = 'Quotation Costs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT EXPENSE
class QuotationExpense(MasterDataAbstractModel):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_expense_quotation",
        null=True
    )
    expense = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.CASCADE,
        verbose_name="expense",
        related_name="quotation_expense_expense",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="quotation_expense_product",
        null=True
    )
    unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="quotation_expense_uom",
        null=True
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="quotation_expense_tax",
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

    class Meta:
        verbose_name = 'Quotation Expense'
        verbose_name_plural = 'Quotation Expenses'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
