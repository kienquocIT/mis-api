from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.masterdata.saledata.models import Tax, UnitOfMeasure, Currency, Product
from apps.shared import SimpleAbstractModel, MasterDataAbstractModel, DataAbstractModel, BastionFieldAbstractModel

# work order tab
WORK_ORDER_STATUS = (
    (0, 'pending'),
    (1, 'in_progress'),
    (2, 'completed'),
    (3, 'cancelled'),
)

# tab payment
PAYMENT_TYPE = (
    (0, 'advance'),
    (1, 'payment'),
)


class ServiceOrder(DataAbstractModel, BastionFieldAbstractModel):
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="service_order_customer"
    )
    customer_data = models.JSONField(default=dict)
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


# service detail tab
class ServiceOrderServiceDetail(MasterDataAbstractModel):
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="service_details"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
    )
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.SET_NULL,
        null=True,
    )
    uom_data = models.JSONField(default=dict)
    price = models.FloatField(default=0)
    tax = models.ForeignKey(
        Tax,
        on_delete=models.SET_NULL,
        null=True,
    )
    tax_data = models.JSONField()
    sub_total_value = models.FloatField(default=0)
    total_value = models.FloatField(default=0)

    # data related to work order
    delivery_balance_value = models.FloatField(default=0)
    total_contribution_percent = models.FloatField(default=0)

    # data related to payment
    total_payment_percent = models.FloatField(default=0)
    total_payment_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Service order service detail'
        verbose_name_plural = 'Service order service details'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ServiceOrderWorkOrder(MasterDataAbstractModel):
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="work_orders"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
    )
    order = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_delivery_point = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)
    unit_cost = models.FloatField(default=0)
    total_value = models.FloatField(default=0)
    work_status = models.PositiveSmallIntegerField(
        default=0,
        choices=WORK_ORDER_STATUS
    )
    task = models.ForeignKey(
        'task.OpportunityTask',
        on_delete=models.SET_NULL,
        verbose_name="task",
        related_name="service_order_work_order_task",
        null=True,
    )

    class Meta:
        verbose_name = 'Service order work order'
        verbose_name_plural = 'Service order work orders'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ServiceOrderWorkOrderCost(SimpleAbstractModel):
    work_order = models.ForeignKey(
        'ServiceOrderWorkOrder',
        on_delete=models.CASCADE,
        related_name="work_order_costs"
    )
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=0)
    unit_cost = models.FloatField(default=0)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.SET_NULL,
        null=True,
    )
    total_value = models.FloatField(default=0)
    exchanged_total_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Service order work order cost'
        verbose_name_plural = 'Service order work order costs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ServiceOrderWorkOrderContribution(SimpleAbstractModel):
    work_order = models.ForeignKey(
        'ServiceOrderWorkOrder',
        on_delete=models.CASCADE,
        related_name="work_order_contributions"
    )
    service_detail = models.ForeignKey(
        'ServiceOrderServiceDetail',
        on_delete=models.CASCADE,
        related_name="service_detail_contributions"
    )
    is_selected = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=150, blank=True)
    contribution_percent = models.FloatField(default=0)
    balance_quantity = models.FloatField(default=0)
    delivered_quantity = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Service order work order contribution'
        verbose_name_plural = 'Service order work order contributions'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ServiceOrderPayment(MasterDataAbstractModel):
    service_order = models.ForeignKey(
        'ServiceOrder',
        on_delete=models.CASCADE,
        related_name="payments"
    )
    installment = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    payment_type = models.PositiveSmallIntegerField(choices=PAYMENT_TYPE)
    is_invoice_required = models.BooleanField(default=False)
    payment_value = models.FloatField(default=0)
    tax_value = models.FloatField(default=0)
    reconcile_value = models.FloatField(default=0)
    receivable_value = models.FloatField(default=0)
    due_date = models.DateField()

    class Meta:
        verbose_name = 'Service order payment'
        verbose_name_plural = 'Service order payments'
        ordering = ('installment',)
        default_permissions = ()
        permissions = ()


class ServiceOrderPaymentDetail(SimpleAbstractModel):
    service_order_payment = models.ForeignKey(
        'ServiceOrderPayment',
        on_delete=models.CASCADE,
        related_name="payment_details"
    )
    service_detail = models.ForeignKey(
        'ServiceOrderServiceDetail',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=150, blank=True)
    sub_total_value = models.FloatField(default=0)
    payment_percent = models.FloatField(default=0)
    payment_value = models.FloatField(default=0)

    # No invoice only data
    total_reconciled_value = models.FloatField(default=0, help_text='Total reconciled value')

    # With invoice only data
    issued_value = models.FloatField(default=0)
    balance_value = models.FloatField(default=0)
    tax_value = models.FloatField(default=0)
    reconcile_value = models.FloatField(default=0)
    receivable_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Service order payment detail'
        verbose_name_plural = 'Service order detail'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ServiceOrderPaymentReconcile(SimpleAbstractModel):
    advance_payment_detail = models.ForeignKey(
        'ServiceOrderPaymentDetail',
        on_delete=models.CASCADE,
        help_text="the advance payment detail mapping with this reconcile record"
    )
    payment_detail = models.ForeignKey(
        'ServiceOrderPaymentDetail',
        on_delete=models.CASCADE,
        related_name="payment_detail_reconciles",
        help_text="the payment detail contains this reconcile record"
    )
    service_detail = models.ForeignKey(
        'ServiceOrderServiceDetail',
        on_delete=models.SET_NULL,
        null=True,
    )
    installment = models.PositiveIntegerField(default=0)
    total_value = models.FloatField(default=0)
    reconcile_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Service order payment reconcile'
        verbose_name_plural = 'Service order payment reconciles'
        ordering = ()
        default_permissions = ()
        permissions = ()


# shipment tab
class ServiceOrderShipment(MasterDataAbstractModel):
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="service_order_shipment_service_order"
    )
    order = models.IntegerField(default=1)
    reference_number = models.CharField(max_length=100, null=True, blank=True)  # Package can allow null
    weight = models.FloatField(default=0, verbose_name="Weight (kg)")
    dimension = models.FloatField(default=0, verbose_name="Dimension")
    description = models.TextField(blank=True, help_text="Note")
    reference_container = models.CharField(max_length=100, null=True, blank=True, help_text="Only use for package")
    is_container = models.BooleanField(default=True)
    container_type = models.ForeignKey(
        'saledata.ContainerTypeInfo',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Container type",
        related_name="service_order_shipment_container_type"
    )
    package_type = models.ForeignKey(
        'saledata.PackageTypeInfo',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Package type",
        help_text="service_order_shipment_package_type"
    )

    class Meta:
        verbose_name = 'Service order shipment'
        verbose_name_plural = 'Service order shipments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ServiceOrderContainer(MasterDataAbstractModel):
    order = models.IntegerField(default=1)
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="service_order_containers"
    )
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


class ServiceOrderPackage(MasterDataAbstractModel):
    order = models.IntegerField(default=1)
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="service_order_packages"
    )
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
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_order_expense_expense_item"
    )
    expense_item_data = models.JSONField(default=dict)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_order_expense_uom"
    )
    uom_data = models.JSONField(default=dict)
    quantity = models.FloatField(default=0)
    expense_price = models.FloatField(default=0)
    tax = models.ForeignKey(
        'saledata.Tax',
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_order_expense_tax"
    )
    tax_data = models.JSONField(default=dict)
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
