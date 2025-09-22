from django.db import models
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.purchasing.utils import PRHandler
from apps.shared import DataAbstractModel, MasterDataAbstractModel, REQUEST_FOR, PURCHASE_STATUS


class PurchaseRequest(DataAbstractModel):
    request_for = models.SmallIntegerField(choices=REQUEST_FOR, default=0)
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder', on_delete=models.CASCADE, related_name="sale_order", null=True
    )
    sale_order_data = models.JSONField(default=dict)
    distribution_plan = models.ForeignKey(
        'distributionplan.DistributionPlan',
        on_delete=models.CASCADE,
        related_name="pr_distribution_plan",
        null=True
    )
    distribution_plan_data = models.JSONField(default=dict)
    supplier = models.ForeignKey(
        'saledata.Account', on_delete=models.CASCADE, related_name="purchase_supplier"
    )
    supplier_data = models.JSONField(default=dict)
    contact = models.ForeignKey(
        'saledata.Contact', on_delete=models.CASCADE, related_name="purchase_contact"
    )
    contact_data = models.JSONField(default=dict)
    delivered_date = models.DateTimeField(help_text='Deadline for delivery')
    purchase_status = models.SmallIntegerField(choices=PURCHASE_STATUS, default=0)
    note = models.CharField(max_length=1000)
    purchase_request_product_datas = models.JSONField(
        default=list, help_text="read data product, use for get list or detail purchase",
    )
    pretax_amount = models.FloatField(help_text='total price of products before tax')
    taxes = models.FloatField(help_text='total tax')
    total_price = models.FloatField(help_text='total price of products')
    is_all_ordered = models.BooleanField(default=False, help_text="True if all products are ordered by Purchase Order")

    class Meta:
        verbose_name = 'Purchase Request'
        verbose_name_plural = 'Purchase Requests'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf'

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

    @classmethod
    def check_reject_document(cls, instance):
        # check if there is CR not done
        if cls.objects.filter_on_company(document_root_id=instance.document_root_id, system_status__in=[1, 2]).exists():
            return False
        if not instance:
            return False
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('purchaserequest', True, self, kwargs)
                    self.update_remain_for_purchase_request_so(self)
        # diagram
        PRHandler.push_diagram(instance=self)
        # hit DB
        super().save(*args, **kwargs)


class PurchaseRequestProduct(MasterDataAbstractModel):
    purchase_request = models.ForeignKey(
        PurchaseRequest, on_delete=models.CASCADE, related_name="purchase_request"
    )
    sale_order_product = models.ForeignKey(
        'saleorder.SaleOrderProduct',
        on_delete=models.CASCADE,
        related_name="purchase_request_so_product",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product', on_delete=models.CASCADE, related_name="purchase_request_product"
    )
    product_data = models.JSONField(default=dict)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure', on_delete=models.CASCADE, related_name="purchase_request_uom"
    )
    uom_data = models.JSONField(default=dict)
    quantity = models.FloatField()
    unit_price = models.FloatField()
    tax = models.ForeignKey(
        'saledata.Tax', on_delete=models.CASCADE, related_name="purchase_request_tax", null=True
    )
    tax_data = models.JSONField(default=dict)
    sub_total_price = models.FloatField()
    # fields for purchase order
    remain_for_purchase_order = models.FloatField(default=0, help_text="minus when purchase")

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
