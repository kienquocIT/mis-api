from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel

ORDER_STATUS_TYPE_CHOICES = [
    (1, _('Open')),
    (0, _('Close')),
]

PAYMENT_STATUS_TYPE_CHOICES = [
    (1, _('Paid')),
    (0, _('Unpaid')),
]


class GroupOrder(DataAbstractModel):
    order_number = models.CharField(max_length=100, blank=True)
    service_start_date = models.DateField()
    service_end_date = models.DateField()
    service_created_date = models.DateField()
    max_guest = models.PositiveIntegerField(default=0)
    registered_guest = models.PositiveIntegerField(default=0)
    order_status = models.SmallIntegerField(
        default=1,
        choices=ORDER_STATUS_TYPE_CHOICES
    )
    payment_term = models.ForeignKey(
        'saledata.PaymentTerm',
        on_delete=models.SET_NULL,
        related_name="payment_term_group_orders",
        null=True
    )
    cost_per_guest = models.FloatField(default=0)
    cost_per_registered_guest = models.FloatField(default=0)
    planned_revenue = models.FloatField(default=0)
    actual_revenue = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.SET_NULL,
        null=True,
        related_name='tax_group_orders'
    )
    total_amount_including_VAT = models.FloatField(default=0)

    total_general_price = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)

    data_selected_price_list = models.JSONField(default=dict)
    # example: data_selected_price_list={
    #     "customer_id": [
    #         {
    #             "id": product_price_list_id,
    #             "value": 1000,
    #             "productId": product_id
    #         }
    #     ]
    # }

    data_product_list = models.JSONField(default=list)
    # example: data_product_list=[
    #     {
    #         id: product_id,
    #         code: product_code,
    #         title: product_title,
    #         standard_price: product_standard_price,
    #         bom_product: {},
    #         general_price: {},
    #         product_price_list_data: []
    #     }
    # ]

    class Meta:
        verbose_name = _('Group Order')
        verbose_name_plural = _('Group Orders')
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("GO")[1])
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
            code = 'GO0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'GO{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_code(cls, instance, kwargs):
        if not instance.code:
            instance.code = cls.generate_code(company_id=instance.company_id)
            # kwargs['update_fields'].append('code')
        return True

    def save(self, *args, **kwargs):
        if not self.code:
            self.push_code(instance=self, kwargs=kwargs)

        # hit DB
        super().save(*args, **kwargs)

class GroupOrderCustomer(MasterDataAbstractModel):
    group_order = models.ForeignKey(
        'GroupOrder',
        on_delete=models.CASCADE,
        related_name='group_order_group_order_customers',
    )
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.SET_NULL,
        related_name='customer_group_order_customers',
        null=True
    )
    customer_code = models.CharField(max_length=100, blank=True)
    customer_name = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    register_code = models.CharField(max_length=100, blank=True, help_text='Or Service Code')
    service_name = models.CharField(max_length=100, blank=True)
    register_date = models.DateField(null=True)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.FloatField(default=0)
    sub_total = models.FloatField(default=0)
    payment_status = models.SmallIntegerField(
        default=1,
        choices=PAYMENT_STATUS_TYPE_CHOICES
    )
    note = models.TextField(blank=True)
    order = models.SmallIntegerField(default=0, help_text='Order of each row of the table on UI')

    class Meta:
        verbose_name = _('Group Order Customer')
        verbose_name_plural = _('Group Order Customers')
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

class GroupOrderCustomerSelectedPriceList(SimpleAbstractModel):
    group_order_customer = models.ForeignKey(
        'GroupOrderCustomer',
        on_delete=models.CASCADE,
        related_name='group_order_customer_selected_price_lists',
    )
    product_price_list = models.ForeignKey(
        'saledata.ProductPriceList',
        on_delete=models.SET_NULL,
        null=True,
    )
    value = models.FloatField(default=0)

class GroupOrderCost(MasterDataAbstractModel):
    group_order = models.ForeignKey(
        'GroupOrder',
        on_delete=models.CASCADE,
        related_name='group_order_costs',
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.SET_NULL,
        related_name='product_group_order_costs',
        null=True
    )
    quantity = models.PositiveIntegerField(default=0)
    guest_quantity = models.PositiveIntegerField(default=0)
    is_using_guest_quantity = models.BooleanField(default=False)
    unit_cost = models.FloatField(default=0)
    sub_total = models.FloatField(default=0)
    order = models.SmallIntegerField(default=0, help_text='Order of each row of the table on UI')

    class Meta:
        verbose_name = _('Group Order Cost')
        verbose_name_plural = _('Group Order Costs')
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

class GroupOrderExpense(MasterDataAbstractModel):
    group_order =  models.ForeignKey(
        'GroupOrder',
        on_delete=models.CASCADE,
        related_name='group_order_expenses',
    )
    expense = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.SET_NULL,
        related_name='expense_group_order_expenses',
        null=True
    )
    expense_name = models.CharField(max_length=100, blank=True)
    expense_uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.SET_NULL,
        related_name="expense_uom_group_order_expenses",
        null=True
    )
    quantity = models.PositiveIntegerField(default=0)
    cost = models.FloatField(default=0)
    expense_tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.SET_NULL,
        related_name='tax_group_order_expenses',
        null=True
    )
    sub_total = models.FloatField(default=0)
    order = models.SmallIntegerField(default=0, help_text='Order of each row of the table on UI')

    class Meta:
        verbose_name = _('Group Order Expense')
        verbose_name_plural = _('Group Order Expenses')
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
