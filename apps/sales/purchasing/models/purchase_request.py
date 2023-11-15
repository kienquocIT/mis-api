from django.db import models
from django.utils import timezone

from apps.shared import DataAbstractModel, MasterDataAbstractModel, REQUEST_FOR, PURCHASE_STATUS


class PurchaseRequest(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="sale_order",
        null=True,
    )
    supplier = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="purchase_supplier",
    )
    request_for = models.SmallIntegerField(
        choices=REQUEST_FOR,
        default=0
    )
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        related_name="purchase_contact",
    )
    delivered_date = models.DateTimeField(
        help_text='Deadline for delivery'
    )
    purchase_status = models.SmallIntegerField(
        choices=PURCHASE_STATUS,
        default=0
    )
    note = models.CharField(
        max_length=1000
    )
    purchase_request_product_datas = models.JSONField(
        default=list,
        help_text="read data product, use for get list or detail purchase",
    )
    pretax_amount = models.FloatField(
        help_text='total price of products before tax'
    )
    taxes = models.FloatField(
        help_text='total tax'
    )
    total_price = models.FloatField(
        help_text='total price of products'
    )
    is_all_ordered = models.BooleanField(
        default=False,
        help_text="True if all products are ordered by Purchase Order"
    )

    class Meta:
        verbose_name = 'Purchase Request'
        verbose_name_plural = 'Purchase Requests'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("PR")[1])
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
            # code = 'PR0001-' + StringHandler.random_str(17)
            code = 'PR0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'PR{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def update_remain_for_purchase_request_so(cls, instance):
        for pr_product in instance.purchase_request.all():
            if pr_product.sale_order_product:
                pr_product.sale_order_product.remain_for_purchase_request -= pr_product.quantity
                pr_product.sale_order_product.save(update_fields=['remain_for_purchase_request'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.code = self.generate_code(self.company_id)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
                self.update_remain_for_purchase_request_so(self)

        # hit DB
        super().save(*args, **kwargs)


class PurchaseRequestProduct(MasterDataAbstractModel):
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name="purchase_request",
    )
    sale_order_product = models.ForeignKey(
        'saleorder.SaleOrderProduct',
        on_delete=models.CASCADE,
        related_name="purchase_request_so_product",
        null=True,
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="purchase_request_product",
    )
    description = models.CharField(
        max_length=500,
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name="purchase_request_uom",
    )
    quantity = models.FloatField()
    unit_price = models.FloatField()
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        related_name="purchase_request_tax",
    )
    sub_total_price = models.FloatField()
    remain_for_purchase_order = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not purchased order yet, update when PO finish"
    )
    date_modified = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        verbose_name = 'Purchase Request Product'
        verbose_name_plural = 'Purchase Request Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
