import json

from django.db import models

from apps.shared import (
    SimpleAbstractModel, MasterDataAbstractModel,
    DELIVERY_OPTION, DELIVERY_STATE, DELIVERY_WITH_KIND_PICKUP,
)

__all__ = [
    'OrderDelivery',
    'OrderDeliverySub',
    'OrderDeliveryProduct',
]


class OrderDelivery(MasterDataAbstractModel):
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
    delivery_quantity = models.SmallIntegerField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    delivered_quantity_before = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked before',
    )
    remaining_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity need pick'
    )
    ready_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked',
    )
    delivery_data = models.JSONField(
        default=dict,
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
        return True

    def save(self, *args, **kwargs):
        self.put_backup_data()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order Delivery'
        verbose_name_plural = 'Order Delivery'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OrderDeliverySub(MasterDataAbstractModel):
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

    delivery_quantity = models.SmallIntegerField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    delivered_quantity_before = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked before',
    )
    remaining_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity need pick'
    )
    ready_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked',
    )
    delivery_data = models.JSONField(
        default=dict,
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

    def set_and_check_quantity(self):
        if self.times != 1 and not self.previous_step:
            raise ValueError('The previous step must be required when equal to or greater than second times')
        if self.ready_quantity > self.remaining_quantity:
            raise ValueError("Products must have delivery quantity equal to or less than remaining quantity")
        self.remaining_quantity = self.delivery_quantity - self.delivered_quantity_before

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
        verbose_name='Order Delivery of Product'
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
    delivery_quantity = models.SmallIntegerField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    delivered_quantity_before = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked before',
    )
    remaining_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity need pick'
    )
    ready_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked',
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
        if self.ready_quantity > self.remaining_quantity:
            raise ValueError("Products must have picked quantity equal to or less than remaining quantity")
        self.remaining_quantity = self.delivery_quantity - self.delivered_quantity_before

    def save(self, *args, **kwargs):
        self.set_and_check_quantity()
        self.put_backup_data()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Delivery Product'
        verbose_name_plural = 'Delivery Product'
        ordering = ('delivery_sub',)
        # unique_together = ('delivery_sub', 'product')
        default_permissions = ()
        permissions = ()
