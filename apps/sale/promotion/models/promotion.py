from django.db import models

from apps.sale.saledata.models.product import Product
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel

__all__ = ['Promotion', 'CustomerByList', 'CustomerByCondition', 'DiscountMethod', 'GiftMethod']


class Promotion(MasterDataAbstractModel):
    valid_date_start = models.DateField(
        verbose_name="Valid date start", help_text="promotion valid time form with date format"
    )
    valid_date_end = models.DateField(
        verbose_name="Valid date end", help_text="promotion valid time to with date format"
    )
    remark = models.CharField(verbose_name="Descriptions", max_length=250, blank=True, null=True)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="customer_by_list_promotion",
        null=False
    )
    customer_type = models.IntegerField(
        verbose_name="Customer type",
        help_text="filter customer by option choose (0: all, 1: choose, 2: by condition)"
    )
    customer_by_list = models.JSONField(
        verbose_name="Customer by list", help_text="list of customer follow by customer type (option = 1)", default=list
    )
    customer_by_condition = models.JSONField(
        verbose_name="Customer by condition",
        help_text="condition for filter customer list follow by customer type (option = 2)", default=list
    )
    customer_remark = models.CharField(
        verbose_name="Customer Descriptions", max_length=250, blank=True, null=True,
        help_text="Explanation about customer type"
    )
    is_discount = models.BooleanField(
        verbose_name="Discount check", blank=True, null=True,
        help_text="Promotion for discount"
    )
    is_coupons = models.BooleanField(
        verbose_name="Coupons check", blank=True, null=True,
        help_text="Promotion for Coupons"
    )
    is_gift = models.BooleanField(
        verbose_name="Gift check", blank=True, null=True,
        help_text="Promotion for gift"
    )
    discount_method = models.JSONField(
        verbose_name="JSON discount method",
        default=list,
        help_text="Discount method JSON string data"
    )
    coupons_method = models.JSONField(
        verbose_name="Coupons method",
        default=list,
        help_text="Coupons method JSON string data"
    )
    gift_method = models.JSONField(
        verbose_name="Gift method",
        default=list,
        help_text="Gift method JSON string data"
    )

    class Meta:
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class CustomerByList(SimpleAbstractModel):
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name="customer_by_list_promotion",
        null=False
    )
    customer = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="customer_by_list_customer",
        null=False
    )

    class Meta:
        verbose_name = 'Customer by list'
        verbose_name_plural = 'Customer by lists'
        ordering = ()
        default_permissions = ()
        permissions = ()


class CustomerByCondition(SimpleAbstractModel):
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name="customer_by_condition_promotion",
        null=False
    )
    property = models.CharField(
        verbose_name="Customer property", max_length=50,
        help_text="Customer field in model Customer"
    )
    operator = models.CharField(
        verbose_name="Operator", max_length=50,
        help_text="Operator for filter customer with property and result value had provided"
    )
    result = models.CharField(
        verbose_name="Customer result", max_length=50,
        help_text="Customer value field follow by value of property"
    )
    property_type = models.CharField(
        verbose_name="Customer property type", max_length=50,
        help_text="Customer property type field for format result field purpose."
    )
    logic = models.CharField(
        verbose_name="Logic", max_length=50,
        help_text="Logic between condition for connect 2 or many condition purpose"
    )
    order = models.IntegerField(
        verbose_name="Order",
        blank=True, null=True
    )

    class Meta:
        verbose_name = 'Customer by condition'
        verbose_name_plural = 'Customer by conditions'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


VALID_TIME = (
    (1, 'Valid time'),
    (2, 'Week'),
    (3, 'Month'),
)


class DiscountMethod(SimpleAbstractModel):
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name="discount_method_promotion",
        null=False
    )
    before_after_tax = models.BooleanField(
        verbose_name="Before After tax check",
        help_text="Option check before or after tax"
    )
    percent_fix_amount = models.BooleanField(
        verbose_name="Percent or Fixed amount",
        help_text="Option check before or after tax"
    )
    fix_value = models.IntegerField(
        verbose_name="Fixed amount", blank=True, null=True,
        help_text="This field is required when user check \"percent fix amount\" field is False"
    )
    use_count = models.IntegerField(
        verbose_name="Use count",
        help_text="Count time per customer per times", default=1
    )
    times_condition = models.IntegerField(
        verbose_name="Times choose",
        help_text="Choose times apply for per use per customer",
        choices=VALID_TIME,
        default=1
    )
    max_usages = models.IntegerField(
        verbose_name="Max usages",
        help_text="Maximum of usages is apply for discount campaign code",
        default=0
    )
    is_on_order = models.BooleanField(
        verbose_name="Discount on order",
        default=False
    )
    is_minimum = models.BooleanField(
        verbose_name="Minimum purchase",
        default=False
    )
    minimum_value = models.FloatField(
        verbose_name="Minimum purchase value",
        blank=True, null=True
    )
    is_on_product = models.BooleanField(
        verbose_name="Discount on product",
        default=False
    )
    product_selected = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="discount_method_product",
        null=True, blank=True
    )
    is_min_quantity = models.BooleanField(
        verbose_name="Minimum quantity",
        default=False
    )
    num_minimum = models.IntegerField(
        verbose_name="Number of minimum quantity",
        default=0
    )
    free_shipping = models.BooleanField(
        verbose_name="Free shipping",
        default=0
    )

    class Meta:
        verbose_name = 'Discount method'
        verbose_name_plural = 'Discount methods'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GiftMethod(SimpleAbstractModel):
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name="gift_method_promotion",
        null=False
    )
    use_count = models.IntegerField(
        verbose_name="Use count",
        help_text="Count time per customer per times", default=1
    )
    times_condition = models.IntegerField(
        verbose_name="Times choose",
        help_text="Choose times apply for per use per customer",
        choices=VALID_TIME,
        default=1
    )
    max_usages = models.IntegerField(
        verbose_name="Max usages",
        help_text="Maximum of usages is apply for discount campaign code",
        default=0
    )
    is_free_product = models.BooleanField(
        verbose_name="Free product", default=True,
    )
    num_product_received = models.IntegerField(
        verbose_name="Free product", default=1,
    )
    product_received = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gift_method_product_received",
        null=True, blank=True
    )
    is_min_purchase = models.BooleanField(
        verbose_name="Minimum purchase", default=False,
    )
    before_after_tax = models.BooleanField(
        verbose_name="Before After tax select",
        help_text="Option select before or after tax"
    )
    min_purchase_cost = models.FloatField(
        verbose_name="Cost of total value", default=0
    )
    is_purchase = models.BooleanField(
        verbose_name="Cost of total value", default=False
    )
    purchase_num = models.IntegerField(
        verbose_name="Number of product when purchase", default=0,
    )
    purchase_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gift_method_purchase_product",
        null=True, blank=True
    )


    class Meta:
        verbose_name = 'Gift method'
        verbose_name_plural = 'Gifts method'
        ordering = ()
        default_permissions = ()
        permissions = ()


class CouponsMethod(DiscountMethod):
    coupons_no = models.IntegerField(
        verbose_name="Coupons No",
        default=0
    )

    class Meta:
        verbose_name = 'Coupons method'
        verbose_name_plural = 'Coupons methods'
        ordering = ()
        default_permissions = ()
        permissions = ()
