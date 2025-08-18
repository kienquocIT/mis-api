
from django.db import models

from apps.shared import MasterDataAbstractModel, PRICE_CONFIG_TYPE


class Attribute(MasterDataAbstractModel):
    parent_n = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="attribute_parent_n",
        verbose_name="parent attribute",
        null=True,
    )
    price_config_type = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(PRICE_CONFIG_TYPE),
    )
    price_config_data = models.JSONField(default=dict, help_text='data JSON of price_config')
    is_category = models.BooleanField(default=False, help_text='flag to know this is attribute or category')

    class Meta:
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class AttributeNumeric(MasterDataAbstractModel):
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        verbose_name="attribute",
        related_name="attribute_numeric_attribute",
    )
    attribute_unit = models.CharField(max_length=100, blank=True)
    duration_unit = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="duration_unit",
        related_name="attribute_numeric_duration_unit",
        null=True
    )
    duration_unit_data = models.JSONField(default=dict, help_text='data json of duration unit')
    min_value = models.FloatField(default=0)
    max_value = models.FloatField(default=0)
    increment = models.FloatField(default=0)
    price_per_unit = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Attribute numeric'
        verbose_name_plural = 'Attribute numerics'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class AttributeList(MasterDataAbstractModel):
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        verbose_name="attribute",
        related_name="attribute_list_attribute",
    )
    duration_unit = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="duration unit",
        related_name="attribute_list_duration_unit",
        null=True
    )
    duration_unit_data = models.JSONField(default=dict, help_text='data json of duration unit')
    list_item = models.JSONField(default=list, help_text='data JSON of list items')

    class Meta:
        verbose_name = 'Attribute list'
        verbose_name_plural = 'Attribute lists'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class AttributeListItem(MasterDataAbstractModel):
    attribute_list = models.ForeignKey(
        AttributeList,
        on_delete=models.CASCADE,
        verbose_name="attribute list",
        related_name="attribute_list_item_attribute_list",
    )
    additional_cost = models.FloatField(default=0)
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Attribute list item'
        verbose_name_plural = 'Attribute items'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class AttributeWarranty(MasterDataAbstractModel):
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        verbose_name="attribute",
        related_name="attribute_warranty_attribute",
    )
    quantity = models.FloatField(default=0)
    duration_unit = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="duration unit",
        related_name="attribute_warranty_duration_unit",
        null=True
    )
    duration_unit_data = models.JSONField(default=dict, help_text='data json of duration unit')
    additional_cost = models.FloatField(default=0)
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Attribute warranty'
        verbose_name_plural = 'Attribute warranties'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
