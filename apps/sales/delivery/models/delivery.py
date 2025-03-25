import json
from copy import deepcopy
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounting.journalentry.utils.log_for_delivery import JEForDeliveryHandler
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.masterdata.saledata.models import SubPeriods
from apps.sales.delivery.utils import DeliFinishHandler, DeliHandler
from apps.sales.report.utils.log_for_delivery import IRForDeliveryHandler
from apps.shared import (
    DELIVERY_OPTION, DELIVERY_STATE, DELIVERY_WITH_KIND_PICKUP, DataAbstractModel,
    MasterDataAbstractModel, ASSET_TYPE, PRODUCT_CONVERT_INTO,
)

__all__ = [
    'OrderDelivery',
    'OrderDeliverySub',
    'OrderDeliveryProduct',
    'OrderDeliveryAttachment',
    'OrderDeliveryProductTool',
    'OrderDeliveryProductAsset',
]


class OrderDelivery(DataAbstractModel):
    # sale order
    sale_order = models.OneToOneField(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name='Order Delivery of Sale Order',
        help_text='The Sale Order had one/many Order Picking',
        related_name='delivery_of_sale_order',
        null=True,
    )
    sale_order_data = models.JSONField(
        default=dict,
        verbose_name='Sale Order data',
        help_text='data json of sale order',
    )
    # lease order
    lease_order = models.OneToOneField(
        'leaseorder.LeaseOrder',
        on_delete=models.CASCADE,
        verbose_name='Order Delivery of Lease Order',
        related_name='delivery_of_lease_order',
        null=True,
    )
    lease_order_data = models.JSONField(
        default=dict,
        verbose_name='Lease Order data',
        help_text='data json of lease order',
    )
    from_picking_area = models.TextField(
        blank=True,
        verbose_name='From Picking Area'
    )
    # customer from sale order
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="order_delivery_customer",
        null=True,
        help_text="sale data Accounts have type customer"
    )
    customer_data = models.JSONField(
        default=dict,
        verbose_name='Customer Data backup',
        help_text=json.dumps({'id': '', 'title': '', 'code': ''})
    )
    # contact
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="order_delivery_contact",
        null=True
    )
    contact_data = models.JSONField(
        default=dict,
        verbose_name='Contact Data backup',
        help_text=json.dumps({'id': '', 'title': '', 'code': ''})
    )

    estimated_delivery_date = models.DateTimeField(
        null=True,
        verbose_name='Delivery Date '
    )
    actual_delivery_date = models.DateTimeField(
        null=True,
        verbose_name='Delivery Date '
    )
    kind_pickup = models.SmallIntegerField(
        choices=DELIVERY_WITH_KIND_PICKUP,
        default=0,
        verbose_name='Is wait pickup',
        help_text='Wait picking push trigger or person manual update product in warehouse',
    )
    state = models.SmallIntegerField(
        choices=DELIVERY_STATE,
        default=0,
    )
    remarks = models.TextField(blank=True)
    sub = models.OneToOneField(
        'OrderDeliverySub',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Only one sub in the current'
    )
    delivery_option = models.SmallIntegerField(
        choices=DELIVERY_OPTION,
        verbose_name='Delivery Option',
        help_text='Delivery option when change in this records',
    )
    delivery_quantity = models.FloatField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    delivered_quantity_before = models.FloatField(
        default=0,
        verbose_name='Quantity was picked before',
    )
    remaining_quantity = models.FloatField(
        default=0,
        verbose_name='Quantity need pick'
    )
    ready_quantity = models.FloatField(
        default=0,
        verbose_name='Quantity was picked',
    )
    delivery_data = models.JSONField(
        default=list,
        verbose_name='Delivery Info',
        help_text=json.dumps(
            {
                '{ID Product}': {
                    'delivery_quantity': '(Total delivery quantity need delivery)',
                    'delivered_quantity_before': '(Total delivered quantity before)',
                    'remaining_quantity': '(Quantity need delivery in this record)',
                    'ready_quantity': '(Delivery quantity was delivered in this record)',
                }
            }
        )
    )

    def put_backup_data(self):
        if self.sale_order and not self.sale_order_data:
            self.sale_order_data = {
                'id': str(self.sale_order_id),
                'title': str(self.sale_order.title),
                'code': str(self.sale_order.code),
            }
        if self.lease_order and not self.lease_order_data:
            self.lease_order_data = {
                'id': str(self.lease_order_id),
                'title': str(self.lease_order.title),
                'code': str(self.lease_order.code),
            }
        if self.customer and not self.customer_data:
            self.customer_data = {
                'id': str(self.customer_id),
                'title': str(self.customer.name),
                'code': str(self.customer.code)
            }
        if self.contact and not self.contact_data:
            self.contact_data = {
                'id': str(self.contact_id),
                'title': str(self.contact.fullname),
                'code': str(self.contact.code)
            }
        return True

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("D")[1])
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
            code = 'D0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'D{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_code(cls, instance):
        if not instance.code:
            code_generated = CompanyFunctionNumber.gen_code(company_obj=instance.company, func=4)
            instance.code = code_generated if code_generated else cls.generate_code(company_id=instance.company_id)
        return True

    def save(self, *args, **kwargs):
        self.put_backup_data()
        # self.push_code(instance=self)  # code
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order Delivery'
        verbose_name_plural = 'Order Delivery'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OrderDeliverySub(DataAbstractModel):
    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return "1373e903-909c-4b77-9957-8bcf97e8d6d3"

    order_delivery = models.ForeignKey(
        OrderDelivery,
        on_delete=models.CASCADE,
        verbose_name='Order Delivery',
    )
    date_done = models.DateTimeField(
        help_text='The record done at value',
        null=True
    )
    previous_step = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Previous Delivery'
    )
    times = models.SmallIntegerField(
        default=1,
        verbose_name='Time Re-Picking',
    )
    products = models.ManyToManyField(
        'saledata.Product',
        through='OrderDeliveryProduct',
        symmetrical=False,
        related_name='products_of_order_delivery',
        through_fields=('delivery_sub', 'product')  # Explicitly specify the foreign keys
    )
    delivery_quantity = models.FloatField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    delivered_quantity_before = models.FloatField(
        default=0,
        verbose_name='Quantity was picked before',
    )
    remaining_quantity = models.FloatField(
        default=0,
        verbose_name='Quantity need pick'
    )
    ready_quantity = models.FloatField(
        default=0,
        verbose_name='Quantity was picked',
    )
    delivery_data = models.JSONField(
        default=list,
        verbose_name='Delivery Info',
        help_text=json.dumps(
            {
                '{ID Product}': {
                    'delivery_quantity': '(Total delivery quantity need delivery)',
                    'delivered_quantity_before': '(Total delivered quantity before)',
                    'remaining_quantity': '(Quantity need delivery in this record)',
                    'ready_quantity': '(Delivery quantity was delivered in this record)',
                }
            }
        ),
        null=True
    )
    is_updated = models.BooleanField(
        default=False,
        verbose_name='Sub is update',
        help_text=json.dumps('Red Flag')
    )
    state = models.SmallIntegerField(
        choices=DELIVERY_STATE,
        default=0,
    )
    sale_order_data = models.JSONField(
        default=dict,
        verbose_name='Sale Order data',
        help_text='data json of sale order',
    )
    lease_order_data = models.JSONField(
        default=dict,
        verbose_name='Lease Order data',
        help_text='data json of lease order',
    )
    estimated_delivery_date = models.DateTimeField(
        null=True,
        verbose_name='Delivery Date '
    )
    actual_delivery_date = models.DateTimeField(
        null=True,
        verbose_name='Delivery Date '
    )
    customer_data = models.JSONField(
        default=dict,
        verbose_name='Customer Data backup',
        help_text=json.dumps({'id': '', 'title': '', 'code': ''}),
        null=True
    )
    contact_data = models.JSONField(
        default=dict,
        verbose_name='Contact Data backup',
        help_text=json.dumps({'id': '', 'title': '', 'code': ''}),
        null=True
    )
    remarks = models.TextField(blank=True)
    config_at_that_point = models.JSONField(
        default=dict,
        verbose_name='this is config was created at that time',
        help_text=json.dumps(
            {'is_picking': True, 'is_partial_ship': False}
        ),
    )
    attachments = models.JSONField(
        default=list,
        null=True,
        verbose_name='order delivery attachment',
        help_text=json.dumps(['uuid4', 'uuid4']),
    )
    delivery_logistic = models.JSONField(
        default=list,
        null=True,
        verbose_name='delivery shipping and billing address',
        help_text=json.dumps(
            {
                "shipping_address": "lorem ipsum dolor sit amet",
                "billing_address": "consectetur adipiscing elit."
            }
        ),
    )
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='OrderDeliveryAttachment',
        symmetrical=False,
        blank=True,
        related_name='file_of_delivery',
    )

    def set_and_check_quantity(self):
        if self.times != 1 and not self.previous_step:
            raise ValueError('The previous step must be required when equal to or greater than second times')
        if self.ready_quantity > self.remaining_quantity:
            raise ValueError(_("Products must have delivery quantity equal to or less than remaining quantity"))
        self.remaining_quantity = self.delivery_quantity - self.delivered_quantity_before

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("D")[1])
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
            code = 'D0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'D{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_code(cls, instance, kwargs):
        if not instance.code:
            code_generated = CompanyFunctionNumber.gen_code(company_obj=instance.company, func=4)
            instance.code = code_generated if code_generated else cls.generate_code(company_id=instance.company_id)
            kwargs['update_fields'].append('code')
        return True

    @classmethod
    def push_state(cls, instance, kwargs):
        instance.state = 2
        kwargs['update_fields'].append('state')
        return True

    def save(self, *args, **kwargs):
        SubPeriods.check_period(self.tenant_id, self.company_id)
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    self.push_code(instance=self, kwargs=kwargs)  # code
                    self.push_state(instance=self, kwargs=kwargs)  # state
                    DeliFinishHandler.create_new(instance=self)  # new sub + product
                    DeliFinishHandler.push_product_warehouse(instance=self)  # product warehouse
                    DeliFinishHandler.update_asset_status(instance=self)  # asset status => delivered
                    DeliFinishHandler.force_create_new_asset(instance=self)  # create new asset
                    DeliFinishHandler.force_create_new_tool(instance=self)  # create new tool
                    DeliFinishHandler.push_product_info(instance=self)  # product
                    DeliFinishHandler.push_so_lo_status(instance=self)  # sale order
                    DeliFinishHandler.push_final_acceptance(instance=self)  # final acceptance
                    DeliHandler.push_diagram(instance=self)  # diagram

                    IRForDeliveryHandler.push_to_inventory_report(self)
                    JEForDeliveryHandler.push_to_journal_entry(self)

        self.set_and_check_quantity()
        if kwargs.get('force_inserts', False):
            times_arr = OrderDeliverySub.objects.filter(order_delivery=self.order_delivery).values_list(
                'times', flat=True
            )
            self.times = (max(times_arr) + 1) if len(times_arr) > 0 else 1

        # diagram
        if self.system_status not in [2, 3]:
            DeliHandler.push_diagram(instance=self)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order Delivery Sub'
        verbose_name_plural = 'Order Delivery Sub'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OrderDeliveryProduct(MasterDataAbstractModel):
    delivery_sub = models.ForeignKey(
        OrderDeliverySub,
        on_delete=models.CASCADE,
        verbose_name='Order Delivery of Product',
        related_name='delivery_product_delivery_sub',
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name='Product need Picking',
        related_name='delivery_product_product',
    )
    product_data = models.JSONField(
        default=dict,
        verbose_name='Product Data backup',
        help_text='data json of product'
    )
    asset_type = models.SmallIntegerField(null=True, help_text='choices= ' + str(ASSET_TYPE))
    offset = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="delivery_product_offset",
        null=True
    )
    offset_data = models.JSONField(default=dict, help_text='data json of offset')
    asset_data = models.JSONField(default=list, help_text='data json of asset')
    tool_data = models.JSONField(default=list, help_text='data json of tool')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name='uom',
        related_name="delivery_product_uom",
        null=True,
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom time",
        related_name="delivery_product_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom time')
    delivery_quantity = models.FloatField(verbose_name='Quantity need pickup of SaleOrder',)
    delivered_quantity_before = models.FloatField(default=0, verbose_name='Quantity was picked before',)
    remaining_quantity = models.FloatField(default=0, verbose_name='Quantity need pick')
    ready_quantity = models.FloatField(default=0, verbose_name='Quantity already for delivery',)
    picked_quantity = models.FloatField(default=0, verbose_name='Quantity was picked',)
    delivery_data = models.JSONField(
        default=list,
        verbose_name='data about product, warehouse, stock',
        help_text=json.dumps(
            [{
                'warehouse_id': 'stock number',
            }]
        ),
        null=True
    )
    order = models.IntegerField(default=1)
    is_promotion = models.BooleanField(
        default=False,
        help_text="flag to know this product is for promotion (discount, gift,...)"
    )
    product_quantity = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
    product_cost = models.FloatField(default=0)
    product_tax_value = models.FloatField(default=0)
    product_subtotal_cost = models.FloatField(default=0)

    # Begin depreciation fields

    product_depreciation_subtotal = models.FloatField(default=0)
    product_depreciation_price = models.FloatField(default=0)
    product_depreciation_method = models.SmallIntegerField(default=0)  # (0: 'Line', 1: 'Adjustment')
    product_depreciation_adjustment = models.FloatField(default=0)
    product_depreciation_time = models.FloatField(default=0)
    product_depreciation_start_date = models.DateField(null=True)
    product_depreciation_end_date = models.DateField(null=True)

    product_lease_start_date = models.DateField(null=True)
    product_lease_end_date = models.DateField(null=True)

    depreciation_data = models.JSONField(default=list, help_text='data json of depreciation')

    product_convert_into = models.SmallIntegerField(choices=PRODUCT_CONVERT_INTO, null=True)

    # End depreciation fields

    returned_quantity_default = models.FloatField(default=0)

    # fields for recovery
    quantity_remain_recovery = models.FloatField(default=0, help_text="minus when recovery")

    def put_backup_data(self):
        if self.product and not self.product_data:
            self.product_data = {
                "id": str(self.product_id),
                "title": str(self.product.title),
                "code": str(self.product.code),
                "general_traceability_method": self.product.general_traceability_method,
            }
        if self.offset and not self.offset_data:
            self.offset_data = {
                "id": str(self.offset_id),
                "title": str(self.offset.title),
                "code": str(self.offset.code),
                "general_traceability_method": self.offset.general_traceability_method,
            }
        if self.uom and not self.uom_data:
            self.uom_data = {
                "id": str(self.uom_id),
                "title": str(self.uom.title),
                "code": str(self.uom.code),
                "ratio": self.uom.ratio,
            }
        return True

    def set_and_check_quantity(self):
        if self.picked_quantity > self.remaining_quantity:
            raise ValueError(_("Products must have picked quantity equal to or less than remaining quantity"))
        self.remaining_quantity = self.delivery_quantity - self.delivered_quantity_before
        return True

    def before_save(self):
        self.set_and_check_quantity()
        self.put_backup_data()

    def setup_new_obj(
            self,
            old_obj, new_sub,
            delivery_quantity, delivered_quantity_before,
            remaining_quantity, ready_quantity,
    ):
        new_obj = deepcopy(old_obj)
        # Override data
        new_obj.id = None  # Clear the primary key
        new_obj.delivery_sub = new_sub
        new_obj.delivery_quantity = delivery_quantity
        new_obj.delivered_quantity_before = delivered_quantity_before
        new_obj.remaining_quantity = remaining_quantity
        new_obj.ready_quantity = ready_quantity
        new_obj.picked_quantity = 0
        new_obj.delivery_data = []
        # Check and store asset not delivered to field asset_data
        new_obj.asset_data = [
            asset_data for asset_data in new_obj.asset_data
            if asset_data.get('picked_quantity', 0) <= 0
        ]
        # Check and store tool not delivered to field tool_data
        new_obj.tool_data = [
            tool_data for tool_data in new_obj.tool_data
            if tool_data.get('picked_quantity', 0) <= 0
        ]

        new_obj.before_save()
        return new_obj

    def save(self, *args, **kwargs):
        others_check_list = ['for_goods_return', 'for_goods_recovery']
        # active flag save_for_other if there is any value of others_check_list in kwargs
        save_for_other = any(key in kwargs for key in others_check_list)
        # remove key of others_check_list from kwargs
        for key in others_check_list:
            kwargs.pop(key, None)
        # Save normal Delivery if not flag save_for_other
        if not save_for_other:
            self.before_save()
            DeliHandler.create_delivery_product_asset(instance=self)
            DeliHandler.create_delivery_product_tool(instance=self)
            DeliHandler.create_delivery_product_warehouse(instance=self)
            DeliHandler.create_delivery_lot_serial(instance=self)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Delivery Product'
        verbose_name_plural = 'Delivery Products'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class OrderDeliveryProductTool(MasterDataAbstractModel):
    delivery_sub = models.ForeignKey(
        OrderDeliverySub,
        on_delete=models.CASCADE,
        verbose_name="delivery sub",
        related_name="delivery_pt_delivery_sub",
        null=True,
    )
    delivery_product = models.ForeignKey(
        'delivery.OrderDeliveryProduct',
        on_delete=models.CASCADE,
        verbose_name="delivery product",
        related_name="delivery_pt_delivery_product",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="delivery_pt_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    tool = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.CASCADE,
        verbose_name="tool",
        related_name="delivery_pt_tool",
        null=True
    )
    tool_data = models.JSONField(default=dict, help_text='data json of tool')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom time",
        related_name="delivery_pt_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom time')
    product_quantity = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
    remaining_quantity = models.FloatField(default=0, verbose_name='Quantity remain delivery')
    picked_quantity = models.FloatField(default=0, verbose_name='Quantity was delivered')
    # Begin depreciation fields

    product_depreciation_subtotal = models.FloatField(default=0)
    product_depreciation_price = models.FloatField(default=0)
    product_depreciation_method = models.SmallIntegerField(default=0)  # (0: 'Line', 1: 'Adjustment')
    product_depreciation_adjustment = models.FloatField(default=0)
    product_depreciation_time = models.FloatField(default=0)
    product_depreciation_start_date = models.DateField(null=True)
    product_depreciation_end_date = models.DateField(null=True)

    product_lease_start_date = models.DateField(null=True)
    product_lease_end_date = models.DateField(null=True)

    depreciation_data = models.JSONField(default=list, help_text='data json of depreciation')

    # End depreciation fields

    # fields for recovery
    quantity_remain_recovery = models.FloatField(default=0, help_text="minus when recovery")

    class Meta:
        verbose_name = 'Delivery Product Tool'
        verbose_name_plural = 'Delivery Products Tools'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OrderDeliveryProductAsset(MasterDataAbstractModel):
    delivery_sub = models.ForeignKey(
        OrderDeliverySub,
        on_delete=models.CASCADE,
        verbose_name="delivery sub",
        related_name="delivery_pa_delivery_sub",
        null=True,
    )
    delivery_product = models.ForeignKey(
        'delivery.OrderDeliveryProduct',
        on_delete=models.CASCADE,
        verbose_name="delivery product",
        related_name="delivery_pa_delivery_product",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="delivery_pa_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    asset = models.ForeignKey(
        'asset.FixedAsset',
        on_delete=models.CASCADE,
        verbose_name="asset",
        related_name="delivery_pa_asset",
        null=True
    )
    asset_data = models.JSONField(default=dict, help_text='data json of asset')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom time",
        related_name="delivery_pa_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom time')
    product_quantity_time = models.FloatField(default=0)
    picked_quantity = models.FloatField(default=0, verbose_name='Quantity was delivered')
    # Begin depreciation fields

    product_depreciation_subtotal = models.FloatField(default=0)
    product_depreciation_price = models.FloatField(default=0)
    product_depreciation_method = models.SmallIntegerField(default=0)  # (0: 'Line', 1: 'Adjustment')
    product_depreciation_adjustment = models.FloatField(default=0)
    product_depreciation_time = models.FloatField(default=0)
    product_depreciation_start_date = models.DateField(null=True)
    product_depreciation_end_date = models.DateField(null=True)

    product_lease_start_date = models.DateField(null=True)
    product_lease_end_date = models.DateField(null=True)

    depreciation_data = models.JSONField(default=list, help_text='data json of depreciation')

    # End depreciation fields

    # fields for recovery
    quantity_remain_recovery = models.FloatField(default=0, help_text="minus when recovery")

    class Meta:
        verbose_name = 'Delivery Product Asset'
        verbose_name_plural = 'Delivery Products Assets'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OrderDeliveryProductWarehouse(MasterDataAbstractModel):
    delivery_product = models.ForeignKey(
        'delivery.OrderDeliveryProduct',
        on_delete=models.CASCADE,
        verbose_name="delivery product",
        related_name="delivery_pw_delivery_product",
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="delivery_pw_sale_order",
        help_text="main sale order of this delivery or sale order from other project (borrow)",
        null=True,
    )
    sale_order_data = models.JSONField(default=dict, help_text='data json of sale order')
    lease_order = models.ForeignKey(
        'leaseorder.LeaseOrder',
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="delivery_pw_lease_order",
        help_text="main lease order of this delivery or lease order from other project (borrow)",
        null=True,
    )
    lease_order_data = models.JSONField(default=dict, help_text='data json of lease order')
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="delivery_pw_warehouse",
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="delivery_pw_uom",
        help_text='uom ordered',
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    lot_data = models.JSONField(
        default=list, help_text='data json of lot [{}, {}], records in OrderDeliveryLot'
    )
    serial_data = models.JSONField(
        default=list, help_text='data json of serial [{}, {}], records in OrderDeliverySerial'
    )
    quantity_delivery = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Delivery Product Warehouse'
        verbose_name_plural = 'Delivery Product Warehouses'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create(
            cls,
            tenant_id,
            company_id,
            pw_data,
            **kwargs
    ):
        cls.objects.bulk_create([cls(
            **data, **kwargs,
            tenant_id=tenant_id,
            company_id=company_id,
        ) for data in pw_data])
        return True


class OrderDeliveryLot(MasterDataAbstractModel):
    delivery = models.ForeignKey(
        OrderDelivery,
        on_delete=models.CASCADE,
        verbose_name="delivery",
        related_name="delivery_lot_delivery",
    )
    delivery_sub = models.ForeignKey(
        OrderDeliverySub,
        on_delete=models.CASCADE,
        verbose_name="delivery sub",
        related_name="delivery_lot_delivery_sub",
    )
    delivery_product = models.ForeignKey(
        OrderDeliveryProduct,
        on_delete=models.CASCADE,
        verbose_name="delivery product",
        related_name="delivery_lot_delivery_product",
    )
    product_warehouse_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.CASCADE,
        verbose_name="product warehouse lot",
        related_name="delivery_lot_product_warehouse_lot",
    )
    product_warehouse_lot_data = models.JSONField(default=dict, help_text='data json of lot')
    quantity_initial = models.FloatField(
        default=0,
        help_text='quantity in ProductWarehouseLot at the time create this record'
    )
    quantity_delivery = models.FloatField(default=0)
    returned_quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Order Delivery Lot'
        verbose_name_plural = 'Order Delivery Lots'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create(
            cls,
            tenant_id,
            company_id,
            lot_data,
            **kwargs
    ):
        cls.objects.bulk_create([cls(
            **data, **kwargs,
            tenant_id=tenant_id,
            company_id=company_id,
        ) for data in lot_data])
        return True


class OrderDeliverySerial(MasterDataAbstractModel):
    delivery = models.ForeignKey(
        OrderDelivery,
        on_delete=models.CASCADE,
        verbose_name="delivery",
        related_name="delivery_serial_delivery",
    )
    delivery_sub = models.ForeignKey(
        OrderDeliverySub,
        on_delete=models.CASCADE,
        verbose_name="delivery sub",
        related_name="delivery_serial_delivery_sub",
    )
    delivery_product = models.ForeignKey(
        OrderDeliveryProduct,
        on_delete=models.CASCADE,
        verbose_name="delivery product",
        related_name="delivery_serial_delivery_product",
    )
    product_warehouse_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial',
        on_delete=models.CASCADE,
        verbose_name="product warehouse serial",
        related_name="delivery_serial_product_warehouse_serial",
    )
    product_warehouse_serial_data = models.JSONField(default=dict, help_text='data json of serial')
    is_returned = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Order Delivery Serial'
        verbose_name_plural = 'Order Delivery Serials'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create(
            cls,
            tenant_id,
            company_id,
            serial_data,
            **kwargs
    ):
        cls.objects.bulk_create([cls(
            **data, **kwargs,
            tenant_id=tenant_id,
            company_id=company_id,
        ) for data in serial_data])
        return True


class OrderDeliveryAttachment(M2MFilesAbstractModel):
    delivery_sub = models.ForeignKey(
        OrderDeliverySub,
        on_delete=models.CASCADE,
        verbose_name="delivery attachment file",
        related_name="delivery_attachment_delivery",
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'delivery_sub'

    class Meta:
        verbose_name = 'Delivery attachments'
        verbose_name_plural = 'Delivery attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
