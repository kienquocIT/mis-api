import json

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import (
    SimpleAbstractModel, DELIVERY_OPTION, DELIVERY_STATE, DELIVERY_WITH_KIND_PICKUP, DataAbstractModel,
    MasterDataAbstractModel,
)

__all__ = [
    'OrderDelivery',
    'OrderDeliverySub',
    'OrderDeliveryProduct',
    'OrderDeliveryAttachment',
]


class OrderDelivery(DataAbstractModel):
    # sale order
    sale_order = models.OneToOneField(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name='Order Picking of Sale Order',
        help_text='The Sale Order had one/many Order Picking',
        related_name='delivery_of_sale_order',
    )
    sale_order_data = models.JSONField(
        default=dict,
        verbose_name='Sale Order data',
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

    def create_code_delivery(self):
        # auto create code (temporary)
        delivery = OrderDeliverySub.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        if not self.code:
            char = "D"
            temper = delivery + 1
            code = f"{char}{temper:03d}"
            self.code = code

    def save(self, *args, **kwargs):
        self.put_backup_data()
        self.create_code_delivery()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order Delivery'
        verbose_name_plural = 'Order Delivery'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OrderDeliverySub(DataAbstractModel):
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
        null=True
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

    def set_and_check_quantity(self):
        if self.times != 1 and not self.previous_step:
            raise ValueError('The previous step must be required when equal to or greater than second times')
        if self.ready_quantity > self.remaining_quantity:
            raise ValueError(_("Products must have delivery quantity equal to or less than remaining quantity"))
        self.remaining_quantity = self.delivery_quantity - self.delivered_quantity_before

    def create_code_delivery(self):
        # auto create code (temporary)
        delivery = OrderDeliverySub.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        if not self.code:
            char = "D"
            temper = delivery + 1
            code = f"{char}{temper:03d}"
            self.code = code

    def save(self, *args, **kwargs):
        self.set_and_check_quantity()
        if kwargs.get('force_inserts', False):
            times_arr = OrderDeliverySub.objects.filter(order_delivery=self.order_delivery).values_list(
                'times', flat=True
            )
            self.times = (max(times_arr) + 1) if len(times_arr) > 0 else 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order Delivery Sub'
        verbose_name_plural = 'Order Delivery Sub'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OrderDeliveryProduct(SimpleAbstractModel):
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
    )
    product_data = models.JSONField(
        default=dict,
        verbose_name='Product Data backup',
        help_text=json.dumps(
            [
                {'id': '', 'title': '', 'code': '', 'remarks': ''}
            ]
        )
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name='',
    )
    uom_data = models.JSONField(
        default=dict,
        verbose_name='Unit of Measure backup',
        help_text=json.dumps(
            {
                'id': '', 'title': '', 'code': '',
            }
        )
    )
    delivery_quantity = models.FloatField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    delivered_quantity_before = models.FloatField(
        default=0,
        verbose_name='Quantity was picked before',
    )
    # picking information
    remaining_quantity = models.FloatField(
        default=0,
        verbose_name='Quantity need pick'
    )
    ready_quantity = models.FloatField(
        default=0,
        verbose_name='Quantity already for delivery',
    )
    picked_quantity = models.FloatField(
        default=0,
        verbose_name='Quantity was picked',
    )
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
    order = models.IntegerField(
        default=1
    )
    is_promotion = models.BooleanField(
        default=False,
        help_text="flag to know this product is for promotion (discount, gift,...)"
    )
    product_unit_price = models.FloatField(
        default=0
    )
    product_tax_value = models.FloatField(
        default=0
    )
    product_subtotal_price = models.FloatField(
        default=0
    )

    def put_backup_data(self):
        if self.product and not self.product_data:
            self.product_data = {
                "id": str(self.product_id),
                "title": str(self.product.title),
                "code": str(self.product.code),
            }
        if self.uom and not self.uom_data:
            self.uom_data = {
                "id": str(self.uom_id),
                "title": str(self.uom.title),
                "code": str(self.uom.code),
            }
        return True

    def set_and_check_quantity(self):
        if self.picked_quantity > self.remaining_quantity:
            raise ValueError(_("Products must have picked quantity equal to or less than remaining quantity"))
        self.remaining_quantity = self.delivery_quantity - self.delivered_quantity_before

    def create_lot_serial(self):
        if not self.delivery_lot_delivery_product.exists():
            for delivery in self.delivery_data:
                if 'lot_data' in delivery:
                    OrderDeliveryLot.create(
                        delivery_product_id=self.id,
                        delivery_sub_id=self.delivery_sub_id,
                        delivery_id=self.delivery_sub.order_delivery_id,
                        tenant_id=self.delivery_sub.tenant_id,
                        company_id=self.delivery_sub.company_id,
                        lot_data=delivery['lot_data']
                    )
            self.update_product_warehouse_lot()
        if not self.delivery_serial_delivery_product.exists():
            for delivery in self.delivery_data:
                if 'serial_data' in delivery:
                    OrderDeliverySerial.create(
                        delivery_product_id=self.id,
                        delivery_sub_id=self.delivery_sub_id,
                        delivery_id=self.delivery_sub.order_delivery_id,
                        tenant_id=self.delivery_sub.tenant_id,
                        company_id=self.delivery_sub.company_id,
                        serial_data=delivery['serial_data']
                    )
            self.update_product_warehouse_serial()
        return True

    def update_product_warehouse_lot(self):
        for lot in self.delivery_lot_delivery_product.all():
            lot.product_warehouse_lot.quantity_import -= lot.quantity_delivery
            lot.product_warehouse_lot.save(update_fields=['quantity_import'])
        return True

    def update_product_warehouse_serial(self):
        for serial in self.delivery_serial_delivery_product.all():
            serial.product_warehouse_serial.is_delete = True
            serial.product_warehouse_serial.save(update_fields=['is_delete'])
        return True

    def before_save(self):
        self.set_and_check_quantity()
        self.put_backup_data()

    def save(self, *args, **kwargs):
        self.before_save()
        self.create_lot_serial()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Delivery Product'
        verbose_name_plural = 'Delivery Product'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# class OrderDeliveryProductWarehouse(MasterDataAbstractModel):
#     delivery = models.ForeignKey(
#         OrderDelivery,
#         on_delete=models.CASCADE,
#         verbose_name="delivery",
#         related_name="delivery_product_warehouse_delivery",
#         null=True,
#     )
#     delivery_product = models.ForeignKey(
#         OrderDeliveryProduct,
#         on_delete=models.CASCADE,
#         verbose_name="delivery product",
#         related_name="delivery_product_warehouse_delivery_product",
#         null=True,
#     )
#     product_warehouse = models.ForeignKey(
#         'saledata.ProductWareHouse',
#         on_delete=models.CASCADE,
#         verbose_name="product",
#         related_name="delivery_product_warehouse_product_warehouse",
#         null=True
#     )
#     quantity_delivery = models.FloatField(default=0)
#     total_picking = models.FloatField(default=0)
#
#     class Meta:
#         verbose_name = 'Order Delivery Product Warehouse'
#         verbose_name_plural = 'Order Delivery Products Warehouse'
#         ordering = ('-date_created',)
#         default_permissions = ()
#         permissions = ()
#
#
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
    quantity_initial = models.FloatField(
        default=0,
        help_text='quantity in ProductWarehouseLot at the time create this record'
    )
    quantity_delivery = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Order Delivery Lot'
        verbose_name_plural = 'Order Delivery Lots'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create(
            cls,
            delivery_product_id,
            delivery_sub_id,
            delivery_id,
            tenant_id,
            company_id,
            lot_data
    ):
        cls.objects.bulk_create([cls(
            **data,
            delivery_product_id=delivery_product_id,
            delivery_sub_id=delivery_sub_id,
            delivery_id=delivery_id,
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

    class Meta:
        verbose_name = 'Order Delivery Serial'
        verbose_name_plural = 'Order Delivery Serials'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create(
            cls,
            delivery_product_id,
            delivery_sub_id,
            delivery_id,
            tenant_id,
            company_id,
            serial_data
    ):
        cls.objects.bulk_create([cls(
            **data,
            delivery_product_id=delivery_product_id,
            delivery_sub_id=delivery_sub_id,
            delivery_id=delivery_id,
            tenant_id=tenant_id,
            company_id=company_id,
        ) for data in serial_data])
        return True


class OrderDeliveryAttachment(SimpleAbstractModel):
    delivery_sub = models.ForeignKey(
        OrderDeliverySub,
        on_delete=models.CASCADE,
        verbose_name="delivery attachment file",
        related_name="order_delivery_attachment",
        help_text="foreigner key to order delivery sub"
    )
    files = models.OneToOneField(
        'attachments.Files',
        on_delete=models.CASCADE,
        verbose_name='Order delivery attachment files',
        help_text='Delivery sub had one/many attachment file',
        related_name='order_delivery_attachment_files',
    )
    media_file = models.UUIDField(unique=True)

    class Meta:
        verbose_name = 'Order Delivery Attachment'
        verbose_name_plural = 'Order Delivery Attachment'
        # ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
