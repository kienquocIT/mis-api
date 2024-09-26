from django.db import models

from apps.shared import DataAbstractModel, TYPE_PRODUCTION, SimpleAbstractModel, STATUS_PRODUCTION, \
    MasterDataAbstractModel


class ProductionOrder(DataAbstractModel):
    bom = models.ForeignKey(
        'production.BOM',
        on_delete=models.CASCADE,
        verbose_name="bom",
        related_name="production_order_bom",
    )
    bom_data = models.JSONField(default=dict, help_text='data json of bom')
    type_production = models.SmallIntegerField(default=0, help_text='choices= ' + str(TYPE_PRODUCTION))
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="production_order_product",
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    quantity = models.FloatField(default=0, help_text='quantity order')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="production_order_uom",
        null=True,
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="production_order_warehouse",
        null=True,
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    sale_order = models.ManyToManyField(
        'saleorder.SaleOrder',
        through="ProductionOrderSaleOrder",
        symmetrical=False,
        blank=True,
        related_name='production_order_map_so'
    )
    sale_order_data = models.JSONField(default=list, help_text='data json of SO, records in ProductionOrderSaleOrder')
    status_production = models.SmallIntegerField(default=0, help_text='choices= ' + str(STATUS_PRODUCTION))
    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)
    group = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        verbose_name="group",
        related_name="production_order_group",
        null=True,
    )
    group_data = models.JSONField(default=dict, help_text='data json of group')
    time = models.FloatField(default=0, help_text='total time for production')
    task_data = models.JSONField(default=list, help_text='data json of task, records in ProductionOrderTask')
    gr_remain_quantity = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not goods receipted yet, update when GR finish"
    )
    done_issue = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Production order'
        verbose_name_plural = 'Production orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def update_production_order_issue_state(self):
        flag = True
        for item in self.po_task_production_order.filter(is_task=False):
            if item.quantity != item.issued_quantity:
                flag = False
                break
        self.done_issue = flag
        self.save(update_fields=['done_issue'])
        return True

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("PO")[1])
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
            code = 'PO0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'PO{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_code(cls, instance, kwargs):
        if not instance.code:
            instance.code = cls.generate_code(company_id=instance.company_id)
            kwargs['update_fields'].append('code')
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    # code
                    self.push_code(instance=self, kwargs=kwargs)
        # hit DB
        super().save(*args, **kwargs)


class ProductionOrderSaleOrder(SimpleAbstractModel):
    production_order = models.ForeignKey(
        'production.ProductionOrder',
        on_delete=models.CASCADE,
        verbose_name="production order",
        related_name="production_sale_order_production",
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="production_sale_order_so",
    )

    class Meta:
        verbose_name = 'Production Sale Order'
        verbose_name_plural = 'Production Sale Orders'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ProductionOrderTask(MasterDataAbstractModel):
    production_order = models.ForeignKey(
        'production.ProductionOrder',
        on_delete=models.CASCADE,
        verbose_name="production order",
        related_name="po_task_production_order",
    )
    is_task = models.BooleanField(default=False, help_text='flag to know this record is task')
    task_title = models.CharField(max_length=100, blank=True)
    task_order = models.IntegerField(default=1)
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="po_task_product",
        null=True,
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="po_task_uom",
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
        related_name="po_task_warehouse",
        null=True,
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    stock = models.FloatField(default=0)
    available = models.FloatField(default=0)
    tool = models.ManyToManyField(
        'saledata.Product',
        through="ProductionOrderTaskTool",
        symmetrical=False,
        blank=True,
        related_name='po_task_map_tool'
    )
    tool_data = models.JSONField(default=list, help_text='data json of tool, records in ProductionOrderTaskTool')
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Production Order Task'
        verbose_name_plural = 'Production Order Tasks'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ProductionOrderTaskTool(SimpleAbstractModel):
    po_task = models.ForeignKey(
        'production.ProductionOrderTask',
        on_delete=models.CASCADE,
        verbose_name="production order task",
        related_name="po_task_tool_task",
    )
    tool = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="tool",
        related_name="po_task_tool_tool",
    )

    class Meta:
        verbose_name = 'Production Order Task Tool'
        verbose_name_plural = 'Production Order Task Tools'
        ordering = ()
        default_permissions = ()
        permissions = ()
