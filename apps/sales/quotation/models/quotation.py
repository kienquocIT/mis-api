from django.db import models

from apps.shared import DataAbstractModel, SimpleAbstractModel


class Quotation(DataAbstractModel):
    opportunity = models.ForeignKey(
        '',
        on_delete=models.CASCADE,
        verbose_name="opportunity",
        related_name="quotation_opportunity",
        null=True
    )
    customer = models.ForeignKey(
        '',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="quotation_customer",
        null=True
    )
    contact = models.ForeignKey(
        '',
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
    quotation_products = models.ManyToManyField(
        '',
        through='QuotationProduct',
        symmetrical=False,
        related_name='quotations_map_products',
    )
    quotation_products_data = models.JSONField(
        default=list,
        help_text="read data products, use for get list or detail quotation"
    )
    quotation_terms_data = models.JSONField(
        default=dict,
        help_text="read data terms, use for get list or detail quotation"
    )
    quotation_logistics_data = models.JSONField(
        default=dict,
        help_text="read data logistics, use for get list or detail quotation"
    )
    quotation_cost_data = models.JSONField(
        default=list,
        help_text="read data cost, use for get list or detail quotation"
    )
    quotation_expense_data = models.JSONField(
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
        '',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_product_product",
        null=True
    )
    unit_of_measure = models.ForeignKey(
        '',
        on_delete=models.CASCADE,
        verbose_name="unit",
        related_name="quotation_product_uom",
        null=True
    )
    tax = models.ForeignKey(
        '',
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

    class Meta:
        verbose_name = 'Quotation Product'
        verbose_name_plural = 'Quotation Products'
        ordering = ('-date_created',)
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
    payment_terms = models.ForeignKey(
        '',
        on_delete=models.CASCADE,
        verbose_name="payment terms",
        related_name="quotation_term_payment_term",
        null=True
    )

    class Meta:
        verbose_name = 'Quotation Term'
        verbose_name_plural = 'Quotation Terms'
        ordering = ('-date_created',)
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
        ordering = ('-date_created',)
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
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


# SUPPORT LOGISTICS
class QuotationLogistic(SimpleAbstractModel):
    quotation = models.ForeignKey(
        Quotation,
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
        verbose_name = 'Quotation Logistic'
        verbose_name_plural = 'Quotation Logistics'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


# SUPPORT COST