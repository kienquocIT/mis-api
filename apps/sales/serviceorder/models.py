from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
# from apps.masterdata.saledata.models import Account, ExpenseItem, Tax, UnitOfMeasure
# from apps.masterdata.saledata.models.shipment import ContainerTypeInfo, PackageTypeInfo
from apps.shared import SimpleAbstractModel, MasterDataAbstractModel, DataAbstractModel


class ServiceOrder(DataAbstractModel):
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="service_order_customer"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='ServiceOrderAttachMapAttachFile',
        symmetrical=False,
        blank=True,
        related_name='service_order_attachment_m2m'
    )
    # expense value
    expense_pretax_value = models.FloatField(default=0)
    expense_tax_value = models.FloatField(default=0)
    expense_total_value = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('serviceorder', True, self, kwargs)
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Service Order'
        verbose_name_plural = 'Service Orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


# shipment tab
class ServiceOrderShipment(MasterDataAbstractModel):
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="service_order_shipment_service_order"
    )
    reference_number = models.CharField(max_length=100, null=True, help_text="Package can allow null")
    weight = models.FloatField(default=0, verbose_name="Weight (kg)")
    dimension = models.FloatField(default=0, verbose_name="Dimension")
    description = models.TextField(blank=True, help_text="Note")
    is_container = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Service order shipment'
        verbose_name_plural = 'Service order shipments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ServiceOrderContainer(SimpleAbstractModel):
    order = models.IntegerField(default=1)
    shipment = models.ForeignKey(
        ServiceOrderShipment,
        on_delete=models.CASCADE,
        related_name="service_order_container_shipment"
    )
    container_type = models.ForeignKey(
        'saledata.ContainerTypeInfo',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Container type",
        related_name="service_order_container_container_type"
    )

    class Meta:
        verbose_name = 'Service order container'
        verbose_name_plural = 'Service order containers'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ServiceOrderPackage(SimpleAbstractModel):
    order = models.IntegerField(default=1)
    shipment = models.ForeignKey(
        ServiceOrderShipment,
        on_delete=models.CASCADE,
        related_name="service_order_package_shipment"
    )
    container_reference = models.ForeignKey(
        ServiceOrderContainer,
        on_delete=models.CASCADE,
        related_name="service_order_package_container_reference"
    )
    package_type = models.ForeignKey(
        'saledata.PackageTypeInfo',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Package type",
        help_text="service_order_package_package_type"
    )

    class Meta:
        verbose_name = 'Service order package'
        verbose_name_plural = 'Service order packages'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# expense tab
class ServiceOrderExpense(MasterDataAbstractModel):
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="service_order_expense_service_order"
    )
    expense_items = models.ForeignKey(
        'saledata.ExpenseItem',
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_order_expense_expense_items"
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_order_expense_uom"
    )
    quantity = models.FloatField(default=0)
    expense_price = models.FloatField(default=0)
    tax = models.ForeignKey(
        'saledata.Tax',
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_order_expense_tax"
    )
    subtotal_price = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Service order expense'
        verbose_name_plural = 'Service order expenses'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


# attachment tab
class ServiceOrderAttachMapAttachFile(M2MFilesAbstractModel):
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        verbose_name='Attachment File of Service Order',
        related_name="service_order_attachment_service_order",
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'service_order'

    class Meta:
        verbose_name = 'Service order attachment'
        verbose_name_plural = 'Service order attachment'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
