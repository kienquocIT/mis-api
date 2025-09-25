import json
from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.shared import SimpleAbstractModel, DataAbstractModel, RecurrenceAbstractModel


class DeliveryService(DataAbstractModel):
    service_order = models.ForeignKey('serviceorder.ServiceOrder', on_delete=models.CASCADE)
    work_order = models.ForeignKey('serviceorder.ServiceOrderWorkOrder', on_delete=models.CASCADE, null=True)
    work_order_data = models.JSONField(default=dict)
    customer = models.ForeignKey('saledata.Account', on_delete=models.CASCADE)
    customer_data = models.JSONField(default=dict)
    # {'id', 'code', 'name', 'tax_code'}
    contact = models.ForeignKey('saledata.Contact', on_delete=models.CASCADE, null=True)
    contact_data = models.JSONField(default=dict)
    # {'id', 'code', 'fullname'}
    estimated_delivery_date = models.DateField()
    actual_date = models.DateField()
    description = models.TextField()
    delivery_logistic = models.JSONField(
        default=list,
        null=True,
        verbose_name='delivery shipping and billing address',
        help_text=json.dumps(
            {
                "shipping_address": "...",
                "billing_address": "..."
            }
        ),
    )

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'd09c9846-a101-43fc-ba1d-6f666c8b03b4'

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('deliveryservice', True, self, kwargs)
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Delivery Service'
        verbose_name_plural = 'Deliveries Service'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class DeliveryServiceItem(SimpleAbstractModel):
    delivery_service = models.ForeignKey(
        DeliveryService, on_delete=models.CASCADE, related_name='delivery_service_items'
    )

    order = models.IntegerField(default=0)
    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    product_data = models.JSONField(default=dict)
    # {'id', 'code', 'title', 'description'}
    uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.SET_NULL, null=True)
    uom_data = models.JSONField(default=dict)
    # {'id', 'code', 'title', 'group_id'}
    order_quantity = models.FloatField(default=0)
    delivered_quantity = models.FloatField(default=0)
    remain_quantity = models.FloatField(default=0)
    this_time_quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Delivery Service Item'
        verbose_name_plural = 'Delivery Service Items'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class DeliveryServiceItemPW(SimpleAbstractModel):
    delivery_service = models.ForeignKey(DeliveryService, on_delete=models.CASCADE)

    delivery_service_item = models.ForeignKey(
        DeliveryServiceItem, on_delete=models.CASCADE, related_name='delivery_service_item_pw'
    )
    product_warehouse = models.ForeignKey('saledata.ProductWareHouse', on_delete=models.CASCADE)
    product_warehouse_data = models.JSONField(default=dict)
    # {
    #     'id',
    #     'product_data': {'id', 'code', 'title', 'description'},
    #     'warehouse_data': {'id', 'code', 'title'},
    #     'current_quantity'
    # }
    quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Delivery Service Item PW'
        verbose_name_plural = 'Delivery Service Items PW'
        ordering = ()
        default_permissions = ()
        permissions = ()


class DeliveryServiceItemPWSerial(SimpleAbstractModel):
    delivery_service = models.ForeignKey(DeliveryService, on_delete=models.CASCADE)
    delivery_service_item = models.ForeignKey(DeliveryServiceItem, on_delete=models.CASCADE)

    delivery_service_item_pw = models.ForeignKey(
        DeliveryServiceItemPW, on_delete=models.CASCADE, related_name='delivery_service_item_pw_serial'
    )
    serial = models.ForeignKey('saledata.ProductWareHouseSerial', on_delete=models.CASCADE)
    serial_data = models.JSONField(default=dict)
    # {
    #     'id', 'vendor_serial_number', 'serial_number', 'expire_date',
    #     'manufacture_date', 'warranty_start', 'warranty_end',
    # }

    class Meta:
        verbose_name = 'Delivery Service Item PW Serial'
        verbose_name_plural = 'Delivery Service Item PW Serials'
        ordering = ()
        default_permissions = ()
        permissions = ()


class DeliveryServiceItemPWLot(SimpleAbstractModel):
    delivery_service = models.ForeignKey(DeliveryService, on_delete=models.CASCADE)
    delivery_service_item = models.ForeignKey(DeliveryServiceItem, on_delete=models.CASCADE)

    delivery_service_item_pw = models.ForeignKey(
        DeliveryServiceItemPW, on_delete=models.CASCADE, related_name='delivery_service_item_pw_lot'
    )
    lot = models.ForeignKey('saledata.ProductWareHouseLot', on_delete=models.CASCADE)
    lot_data = models.JSONField(default=dict)
    # {
    #     'id', 'lot_number', 'expire_date', 'manufacture_date', 'current_quantity'
    # }
    quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Delivery Service Item PW Lot'
        verbose_name_plural = 'Delivery Service Item PW Lots'
        ordering = ()
        default_permissions = ()
        permissions = ()


class DeliveryServiceAttachmentFile(M2MFilesAbstractModel):
    delivery_service = models.ForeignKey(
        DeliveryService, on_delete=models.CASCADE, related_name="delivery_service_attachments",
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'delivery_service'

    class Meta:
        verbose_name = 'Delivery Service Attachment'
        verbose_name_plural = 'Delivery Service Attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
