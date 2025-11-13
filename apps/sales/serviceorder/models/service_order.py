from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.masterdata.saledata.models import Tax, UnitOfMeasure, Currency, Product
from apps.sales.cashoutflow.utils import AdvanceHandler
from apps.sales.serviceorder.utils.logical_finish import ServiceOrderFinishHandler
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
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name="contact",
        related_name="service_order_contact",
        null=True
    )
    contact_data = models.JSONField(default=dict, help_text='data json of contact')
    start_date = models.DateField()
    end_date = models.DateField()
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='ServiceOrderAttachMapAttachFile',
        symmetrical=False,
        blank=True,
        related_name='service_order_attachment_m2m'
    )
    exchange_rate_data = models.JSONField(default=dict)

    # total product
    total_product_pretax_amount = models.FloatField(default=0, help_text="total pretax of tab product")
    total_product_tax = models.FloatField(default=0, help_text="total tax of tab product")
    total_product = models.FloatField(default=0, help_text="total of tab product")
    total_product_revenue_before_tax = models.FloatField(default=0, help_text="total before tax of tab product")

    # total cost
    total_cost_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab cost")
    total_cost_tax = models.FloatField(default=0, help_text="total tax of tab cost")
    total_cost = models.FloatField(default=0, help_text="total amount of tab cost")

    # expense value
    total_expense_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab expense")
    total_expense_tax = models.FloatField(default=0, help_text="total tax of tab expense")
    total_expense = models.FloatField(default=0, help_text="total amount of tab expense")

    # indicators
    service_order_indicators_data = models.JSONField(
        default=list,
        help_text="read data indicators, records in model ServiceOrderIndicator"
    )
    indicator_revenue = models.FloatField(default=0, help_text="value of indicator revenue (IN0001)")
    indicator_gross_profit = models.FloatField(default=0, help_text="value of indicator gross profit (IN0003)")
    indicator_net_income = models.FloatField(default=0, help_text="value of indicator net income (IN0006)")

    is_done_purchase_request = models.BooleanField(default=False)

    @classmethod
    def check_change_document(cls, instance):
        # check if there is CR not done
        if cls.objects.filter_on_company(document_root_id=instance.document_root_id, system_status__in=[1, 2]).exists():
            return False
        if not instance:
            return False
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
        if not self.code:
            self.code = CompanyFunctionNumber.auto_gen_code_based_on_config(
                app_code='serviceorder', in_workflow=False, instance=self
            )
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):

                if 'date_approved' in kwargs['update_fields']:
                    # CompanyFunctionNumber.auto_gen_code_based_on_config(
                    #     app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                    # )
                    ServiceOrderFinishHandler.re_processing_folder_task_files(instance=self)
        # hit DB
        AdvanceHandler.push_opportunity_log(self)
        super().save(*args, **kwargs)
        ServiceOrderFinishHandler.save_log_snapshot(instance=self)

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
    product_data = models.JSONField(default=dict)
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.SET_NULL,
        null=True,
    )
    uom_data = models.JSONField(default=dict)
    service_percent = models.FloatField(default=0, help_text='Weighting factor for service detail')
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

    # data attribute
    selected_attributes = models.JSONField(default=dict)
    attributes_total_cost = models.FloatField(default=0)
    duration_value = models.IntegerField(default=0)
    duration = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.SET_NULL,
        null=True,
        related_name='service_order_service_details'
    )
    duration_unit_data = models.JSONField(default=dict)

    remain_for_purchase_request = models.FloatField(default=0)

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
    task_data = models.JSONField(default=list, help_text="list task data, records in ServiceOrderWorkOrderTask")
    tasks = models.ManyToManyField(
        'task.OpportunityTask',
        through="ServiceOrderWorkOrderTask",
        symmetrical=False,
        blank=True,
        related_name='service_order_work_order_m2m_task'
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
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_order_work_order_costs"
    )
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
    unit_cost = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)

    # package feature
    has_package = models.BooleanField(default=False)
    package_data = models.JSONField(default=list, null=True)
    delivery_call = models.BooleanField(
        default=False,
        verbose_name='Called delivery',
        help_text='State call delivery of this',
    )

    class Meta:
        verbose_name = 'Service order work order contribution'
        verbose_name_plural = 'Service order work order contributions'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ServiceOrderWorkOrderTask(MasterDataAbstractModel):
    work_order = models.ForeignKey(
        'ServiceOrderWorkOrder',
        on_delete=models.CASCADE,
        related_name="service_order_work_order_task_wo"
    )
    task = models.ForeignKey(
        'task.OpportunityTask',
        on_delete=models.SET_NULL,
        verbose_name="task",
        related_name="service_order_work_order_task_task",
        null=True,
    )

    class Meta:
        verbose_name = 'Service order work order task'
        verbose_name_plural = 'Service order work order tasks'
        ordering = ('-date_created',)
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
    order = models.IntegerField(default=0)
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
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ServiceOrderPaymentReconcile(SimpleAbstractModel):
    order = models.IntegerField(default=0)
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
        ordering = ('order',)
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
    expense_subtotal_price = models.FloatField(default=0)

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


# indicator
class ServiceOrderIndicator(MasterDataAbstractModel):
    service_order = models.ForeignKey(
        'serviceorder.ServiceOrder',
        on_delete=models.CASCADE,
        verbose_name="service order",
        related_name="service_order_indicator_service_order",
    )
    indicator_value = models.FloatField(
        default=0,
        help_text="value of specific indicator for sale order"
    )
    indicator_rate = models.FloatField(
        default=0,
        help_text="rate value of specific indicator for sale order"
    )
    quotation_indicator = models.ForeignKey(
        'quotation.QuotationIndicatorConfig',
        on_delete=models.CASCADE,
        verbose_name="quotation indicator",
        related_name="service_order_indicator_quotation_indicator",
        null=True
    )
    quotation_indicator_data = models.JSONField(default=dict, help_text='data json of quotation indicator')
    quotation_indicator_value = models.FloatField(
        default=0,
        help_text="value of specific indicator for quotation mapped with service order"
    )
    quotation_indicator_rate = models.FloatField(
        default=0,
        help_text="rate value of specific indicator for quotation mapped with service order"
    )
    difference_indicator_value = models.FloatField(
        default=0,
        help_text="difference value between quotation and sale order"
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Service Order Indicator'
        verbose_name_plural = 'Service Order Indicators'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
