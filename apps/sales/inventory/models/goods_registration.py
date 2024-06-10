from django.db import models
from rest_framework import serializers
from apps.sales.delivery.models import DeliveryConfig
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import SubPeriods
from apps.sales.inventory.models.goods_return_sub import (
    GoodsReturnSubSerializerForPicking, GoodsReturnSubSerializerForNonPicking
)
from apps.sales.inventory.utils import ReturnFinishHandler
from apps.sales.report.models import ReportInventorySub
from apps.shared import DataAbstractModel, SimpleAbstractModel


class GoodsRegistration(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder', on_delete=models.CASCADE, related_name='goods_registration_so'
    )

    class Meta:
        verbose_name = 'Goods Registration'
        verbose_name_plural = 'Goods Registrations'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class GoodsRegistrationLineDetail(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, related_name='goods_registration_line_detail'
    )
    so_item = models.ForeignKey(
        'saleorder.SaleOrderProduct', on_delete=models.CASCADE, related_name='goods_registration_line_detail_so_item'
    )
    registered_quantity = models.FloatField(default=0)
    registered_data = models.JSONField(default=dict)
    registered_data_format = {
        'goods_receipt_list': [
            {
                'id': ...,
                'code': ...,
                'title': ...,
                'quantity': ...,
                'warehouse_list': [{
                    'warehouse': {'id': ..., 'code': ..., 'title': ...},
                    'lot_data': [{'lot_id': ..., 'lot_number': ..., 'lot_quantity': ...}]
                }]
            }
        ]
    }

    class Meta:
        verbose_name = 'Goods Registration Line Detail'
        verbose_name_plural = 'Goods Registration Lines Detail'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsRegistrationLot(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, related_name='goods_registration_lot'
    )
    lot_registered = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, related_name='goods_registration_lot_registered'
    )
    lot_registered_quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Registration Lot'
        verbose_name_plural = 'Goods Registration Lots'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsRegistrationSerial(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, related_name='goods_registration_serial'
    )
    sn_registered = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, related_name='goods_registration_sn_registered'
    )

    class Meta:
        verbose_name = 'Goods Registration Serial'
        verbose_name_plural = 'Goods Registration Serials'
        ordering = ()
        default_permissions = ()
        permissions = ()
