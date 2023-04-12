from django.db import models

from apps.sales.opportunity.models.opportunity import Opportunity
from apps.shared import DataAbstractModel, SimpleAbstractModel


class Quotation(DataAbstractModel):
    opportunity = models.ForeignKey(
        Opportunity,
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
        null=True
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
    quotation_costs_data = models.JSONField(
        default=list,
        help_text="read data cost, use for get list or detail quotation"
    )
    quotation_expenses_data = models.JSONField(
        default=list,
        help_text="read data expense, use for get list or detail quotation"
    )
    total_pretax_revenue = models.FloatField(
        default=0
    )
    total_tax = models.FloatField(
        default=0
    )
    total = models.FloatField(
        default=0
    )
    is_customer_confirm = models.BooleanField(
        default=False,
        help_text="flag to check customer confirm quotation"
    )

    class Meta:
        verbose_name = 'Quotation'
        verbose_name_plural = 'Quotations'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


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
    product_quantity = models.IntegerField(
        default=0
    )
    product_unit_price = models.FloatField(
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
    product_subtotal_price = models.FloatField(
        default=0
    )
    order = models.IntegerField(
        default=1
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
        '',
        through='',
        symmetrical=False,
        related_name='quotation_term_map_prices',
    )
    discount_list = models.ManyToManyField(
        '',
        through='',
        symmetrical=False,
        related_name='quotation_term_map_discounts',
    )
    payment_term = models.ForeignKey(
        '',
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
        '',
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
        '',
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
    shipping_address_list = models.ManyToManyField(
        '',
        through='',
        symmetrical=False,
        related_name='quotation_logistic_map_shipping',
    )
    billing_address_list = models.ManyToManyField(
        '',
        through='',
        symmetrical=False,
        related_name='quotation_logistic_map_billing',
    )

    class Meta:
        verbose_name = 'Quotation Logistic'
        verbose_name_plural = 'Quotation Logistics'
        default_permissions = ()
        permissions = ()


class QuotationLogisticShipping(SimpleAbstractModel):
    quotation_logistic = models.ForeignKey(
        QuotationLogistic,
        on_delete=models.CASCADE,
    )
    shipping_address = models.ForeignKey(
        '',
        on_delete=models.CASCADE,
        verbose_name="shipping address",
        related_name="quotation_logistic_shipping",
        null=True
    )

    class Meta:
        verbose_name = 'Quotation Logistic Shipping'
        verbose_name_plural = 'Quotation Logistic Shipping'
        default_permissions = ()
        permissions = ()


class QuotationLogisticBilling(SimpleAbstractModel):
    quotation_logistic = models.ForeignKey(
        QuotationLogistic,
        on_delete=models.CASCADE,
    )
    billing_address = models.ForeignKey(
        '',
        on_delete=models.CASCADE,
        verbose_name="billing address",
        related_name="quotation_logistic_billing",
        null=True
    )

    class Meta:
        verbose_name = 'Quotation Logistic Billing'
        verbose_name_plural = 'Quotation Logistic Billing'
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
    product_quantity = models.IntegerField(
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
    product_subtotal_price = models.FloatField(
        default=0
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Quotation Cost'
        verbose_name_plural = 'Quotation Costs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT EXPENSE
class QuotationExpense(SimpleAbstractModel):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_expense_quotation",
        null=True
    )
    expense = models.ForeignKey(
        '',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_expense_expense",
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
    # cost information
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
    expense_quantity = models.IntegerField(
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
    expense_subtotal_price = models.FloatField(
        default=0
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Quotation Expense'
        verbose_name_plural = 'Quotation Expenses'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
