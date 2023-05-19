import json

from django.db import models

from apps.shared import (
    SimpleAbstractModel, MasterDataAbstractModel,
    PICKING_STATE, DELIVERY_OPTION,
)

__all__ = [
    'OrderPicking',
    'OrderPickingSub',
    'OrderPickingProduct',
]


class OrderPicking(MasterDataAbstractModel):
    sale_order = models.OneToOneField(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name='Order Picking of Sale Order',
        help_text='The Sale Order had one/many Order Picking',
        related_name='picking_of_sale_order',
    )
    sale_order_data = models.JSONField(
        default=dict,
        verbose_name='Sale Order data',
        help_text=json.dumps(
            {
                'id': '', 'title': '', 'code': '',
            }
        ),
    )
    ware_house = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Ware-House selected for picking',
        help_text='Auto select first ware house in list',
    )
    ware_house_data = models.JSONField(
        default=dict,
        verbose_name='WareHouse data',
        help_text=json.dumps(
            {
                'id': '', 'title': '', 'code': '',
            }
        ),
    )
    estimated_delivery_date = models.DateTimeField(
        null=True,
        verbose_name='Delivery Date '
    )
    state = models.SmallIntegerField(
        choices=PICKING_STATE,
        default=0,
    )
    remarks = models.TextField(blank=True)

    delivery_option = models.SmallIntegerField(
        choices=DELIVERY_OPTION,
        verbose_name='Delivery Option',
        help_text='Delivery option when change in this records',
    )

    sub = models.OneToOneField(
        'OrderPickingSub',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Only one sub in the current'
    )
    pickup_quantity = models.SmallIntegerField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    picked_quantity_before = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked before',
    )
    remaining_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity need pick'
    )
    picked_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked',
    )
    pickup_data = models.JSONField(
        default=dict,
        verbose_name='Picked Info',
        help_text=json.dumps(
            {
                '{ID Product}': {
                    'pickup_quantity': '(Total pickup quantity need pickup)',
                    'picked_quantity_before': '(Total picked quantity before)',
                    'remaining_quantity': '(Quantity need pick in this record)',
                    'picked_quantity': '(Picked quantity was pick in this record)',
                }
            }
        )
    )

    def set_and_check_quantity(self):
        if self.picked_quantity > self.remaining_quantity:
            raise ValueError("Products must have picked quantity equal to or less than remaining quantity")
        self.remaining_quantity = self.pickup_quantity - self.picked_quantity_before

    def put_backup_data(self):
        if self.sale_order and not self.sale_order_data:
            self.sale_order_data = {
                'id': str(self.sale_order_id),
                'title': str(self.sale_order.title),
                'code': str(self.sale_order.code),
            }
        if self.ware_house and not self.ware_house_data:
            self.ware_house_data = {
                'id': str(self.ware_house_id),
                'title': str(self.ware_house.title),
                'code': str(self.ware_house.code),
            }
        return True

    def save(self, *args, **kwargs):
        self.set_and_check_quantity()
        self.put_backup_data()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Sale Order Picking'
        verbose_name_plural = 'Sale Order Picking'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OrderPickingSub(MasterDataAbstractModel):
    order_picking = models.ForeignKey(
        'OrderPicking',
        on_delete=models.CASCADE,
        verbose_name='Order Product of Picking',
    )
    date_done = models.DateTimeField(
        null=True,
        help_text='The record done at value',
    )
    previous_step = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Previous Picking'
    )
    times = models.SmallIntegerField(
        default=1,
        verbose_name='Time Re-Picking',
    )
    products = models.ManyToManyField(
        'saledata.Product',
        through='OrderPickingProduct',
        symmetrical=False,
        related_name='products_of_order_picking',
    )
    pickup_quantity = models.SmallIntegerField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    picked_quantity_before = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked before',
    )
    remaining_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity need pick'
    )
    picked_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked',
    )
    pickup_data = models.JSONField(
        default=dict,
        verbose_name='Picked Info',
        help_text=json.dumps(
            {
                '{ID Product}': {
                    'pickup_quantity': '(Total pickup quantity need pickup)',
                    'picked_quantity_before': '(Total picked quantity before)',
                    'remaining_quantity': '(Quantity need pick in this record)',
                    'picked_quantity': '(Picked quantity was pick in this record)',
                }
            }
        )
    )

    def set_and_check_quantity(self):
        if self.times != 1 and not self.previous_step:
            raise ValueError('The previous step must be required when equal to or greater than second times')
        if self.picked_quantity > self.remaining_quantity:
            raise ValueError("Products must have picked quantity equal to or less than remaining quantity")
        self.remaining_quantity = self.pickup_quantity - self.picked_quantity_before

    def save(self, *args, **kwargs):
        self.set_and_check_quantity()
        if kwargs.get('force_inserts', False):
            times_arr = OrderPickingSub.objects.filter(order_picking=self.order_picking).values_list('times', flat=True)
            self.times = (max(times_arr) + 1) if len(times_arr) > 0 else 1

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order Picking Sub'
        verbose_name_plural = 'Order Picking Sub'
        ordering = ('-times',)
        default_permissions = ()
        permissions = ()


class OrderPickingProduct(SimpleAbstractModel):
    picking_sub = models.ForeignKey(
        'OrderPickingSub',
        on_delete=models.CASCADE,
        verbose_name='Order Picking Sub of Product',
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
    pickup_quantity = models.SmallIntegerField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    picked_quantity_before = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked before',
    )
    remaining_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity need pick'
    )
    picked_quantity = models.SmallIntegerField(
        default=0,
        verbose_name='Quantity was picked',
    )

    def _put_backup_data(self):
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

    def _set_and_check_quantity(self):
        if self.picked_quantity > self.remaining_quantity:
            raise ValueError("Products must have picked quantity equal to or less than remaining quantity")
        self.remaining_quantity = self.pickup_quantity - self.picked_quantity_before

    def before_save(self):
        self._put_backup_data()
        self._set_and_check_quantity()

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Product of Order Picking'
        verbose_name_plural = 'Product of Order Picking'
        ordering = ('picking_sub',)
        # unique_together = ('picking_sub', 'product')
        default_permissions = ()
        permissions = ()
