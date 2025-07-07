from django.db import models
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.purchasing.utils import PRHandler
from apps.shared import DataAbstractModel, MasterDataAbstractModel, REQUEST_FOR, PURCHASE_STATUS


class PurchaseRequest(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="sale_order",
        null=True,
    )
    distribution_plan = models.ForeignKey(
        'distributionplan.DistributionPlan',
        on_delete=models.CASCADE,
        related_name="pr_distribution_plan",
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
    def update_remain_for_purchase_request_so(cls, instance):
        if instance.request_for == 0:
            for pr_product in instance.purchase_request.all():
                if pr_product.sale_order_product:
                    pr_product.sale_order_product.remain_for_purchase_request -= pr_product.quantity
                    pr_product.sale_order_product.save(update_fields=['remain_for_purchase_request'])
        if instance.request_for == 3:
            request_quantity = 0
            for pr_product in instance.purchase_request.all():
                request_quantity += pr_product.quantity
            instance.distribution_plan.purchase_request_number += request_quantity
            instance.distribution_plan.save(update_fields=['purchase_request_number'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    code_generated = CompanyFunctionNumber.gen_auto_code(app_code='purchaserequest')
                    if code_generated:
                        self.code = code_generated
                        kwargs['update_fields'].append('code')
                    else:
                        self.add_auto_generate_code_to_instance(self, 'PR[n4]', True, kwargs)
                    self.update_remain_for_purchase_request_so(self)
        # diagram
        PRHandler.push_diagram(instance=self)
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
        null=True
    )
    sub_total_price = models.FloatField()
    # fields for purchase order
    remain_for_purchase_order = models.FloatField(default=0, help_text="minus when purchase")
    date_modified = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        verbose_name = 'Purchase Request Product'
        verbose_name_plural = 'Purchase Request Products'
        ordering = ()
        default_permissions = ()
        permissions = ()


class PurchaseRequestAttachmentFile(M2MFilesAbstractModel):
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='purchase_request_attachments'
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'purchase_request'

    class Meta:
        verbose_name = 'Purchase Request attachment'
        verbose_name_plural = 'Purchase Request attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
