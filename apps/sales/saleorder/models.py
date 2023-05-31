from django.db import models

from apps.shared import DataAbstractModel, SimpleAbstractModel


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
    sale_order_costs_data = models.JSONField(
        default=list,
        help_text="read data cost, use for get list or detail sale order"
    )
    sale_order_expenses_data = models.JSONField(
        default=list,
        help_text="read data expense, use for get list or detail sale order"
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

    class Meta:
        verbose_name = 'Sale Order'
        verbose_name_plural = 'Sale Orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        # auto create code (temporary)
        sale_order = SaleOrder.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "ORDER.CODE."
        if not self.code:
            temper = "%04d" % (sale_order + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code

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
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Sale Order Cost'
        verbose_name_plural = 'Sale Order Costs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT EXPENSE
class SaleOrderExpense(SimpleAbstractModel):
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
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Sale Order Expense'
        verbose_name_plural = 'Sale Order Expenses'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
