from django.db import models

from apps.core.company.models import CompanyFunctionNumber
from apps.sales.production.utils.logical_finish_wo import WorkOrderHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel, STATUS_PRODUCTION, \
    MasterDataAbstractModel, BastionFieldAbstractModel


class WorkOrder(DataAbstractModel, BastionFieldAbstractModel):
    bom = models.ForeignKey(
        'production.BOM',
        on_delete=models.CASCADE,
        verbose_name="bom",
        related_name="work_order_bom",
    )
    bom_data = models.JSONField(default=dict, help_text='data json of bom')
    opportunity_data = models.JSONField(default=dict, help_text='data json of opportunity')
    employee_inherit_data = models.JSONField(default=dict, help_text='data json of employee_inherit')
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="work_order_product",
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    quantity = models.FloatField(default=0, help_text='quantity order')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="work_order_uom",
        null=True,
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="work_order_warehouse",
        null=True,
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="work_order_sale_order",
        null=True,
    )
    sale_order_data = models.JSONField(default=dict, help_text='data json of SO')
    status_production = models.SmallIntegerField(default=0, help_text='choices= ' + str(STATUS_PRODUCTION))
    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)
    group = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        verbose_name="group",
        related_name="work_order_group",
        null=True,
    )
    group_data = models.JSONField(default=dict, help_text='data json of group')
    time = models.FloatField(default=0, help_text='total time for production')
    task_data = models.JSONField(default=list, help_text='data json of task, records in ProductionOrderTask')
    gr_remain_quantity = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not goods receipted yet, update when GR finish"
    )

    class Meta:
        verbose_name = 'Work order'
        verbose_name_plural = 'Work orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('workorder', True, self, kwargs)
                    WorkOrderHandler.wo_info_for_so(instance=self)
        # hit DB
        super().save(*args, **kwargs)


class WorkOrderTask(MasterDataAbstractModel):
    work_order = models.ForeignKey(
        'production.WorkOrder',
        on_delete=models.CASCADE,
        verbose_name="work order",
        related_name="wo_task_work_order",
    )
    is_task = models.BooleanField(default=False, help_text='flag to know this record is task')
    task_title = models.CharField(max_length=100, blank=True)
    task_order = models.IntegerField(default=1)
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="wo_task_product",
        null=True,
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="wo_task_uom",
        null=True,
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    quantity_bom = models.FloatField(default=0)
    quantity = models.FloatField(default=0)
    issued_quantity = models.FloatField(default=0)
    is_all_warehouse = models.BooleanField(
        default=False, help_text='flag to know can use this product of all warehouse'
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="wo_task_warehouse",
        null=True,
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    stock = models.FloatField(default=0)
    available = models.FloatField(default=0)
    tool = models.ManyToManyField(
        'saledata.Product',
        through="WorkOrderTaskTool",
        symmetrical=False,
        blank=True,
        related_name='wo_task_map_tool'
    )
    tool_data = models.JSONField(default=list, help_text='data json of tool, records in WorkOrderTaskTool')
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Work Order Task'
        verbose_name_plural = 'Work Order Tasks'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class WorkOrderTaskTool(SimpleAbstractModel):
    wo_task = models.ForeignKey(
        'production.WorkOrderTask',
        on_delete=models.CASCADE,
        verbose_name="work order task",
        related_name="wo_task_tool_task",
    )
    tool = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="tool",
        related_name="wo_task_tool_tool",
    )

    class Meta:
        verbose_name = 'Work Order Task Tool'
        verbose_name_plural = 'Work Order Task Tools'
        ordering = ()
        default_permissions = ()
        permissions = ()
