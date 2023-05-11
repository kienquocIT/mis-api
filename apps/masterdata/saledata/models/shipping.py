from django.db import models
from apps.shared import SimpleAbstractModel

from apps.shared import MasterDataAbstractModel
__all__ = [
    'Shipping',
    'ShippingCondition',
    'ConditionLocation',
    'FormularCondition'
]


# Create your models here.
class Shipping(MasterDataAbstractModel):
    margin = models.FloatField(
        default=0,
        help_text='Cost of shipping',
        null=True,
    )

    currency = models.ForeignKey(
        'saledata.Currency',
        on_delete=models.CASCADE,
        verbose_name="currency of shipping",
        related_name="shipping_currency",
    )

    cost_method = models.IntegerField(
        default=1,
        help_text='0 - fixed, 1 - formula, 2 - service provider',
        null=True,
    )

    fixed_price = models.FloatField(
        default=0,
        help_text='Amount while user select Fixed Price for shipping',
        null=True,
    )

    formula_condition = models.JSONField(
        default=dict,
        help_text='Condition while user select Formular for shipping',
        null=True,
    )

    service_provider = models.JSONField(
        default=dict,
        help_text='Condition while user select Service Provider for shipping',
        null=True,
    )


class ShippingCondition(SimpleAbstractModel):
    shipping = models.ForeignKey(
        Shipping,
        on_delete=models.CASCADE,
        related_name="formula_shipping_condition",
    )
    formula = models.JSONField(
        default=dict,
        help_text='formula for each condition',
    )
    location_condition = models.ManyToManyField(
        'base.City',
        through="ConditionLocation",
        symmetrical=False,
        blank=True,
        related_name='location_map_condition',
    )


class ConditionLocation(SimpleAbstractModel):
    location = models.ForeignKey(
        'base.City',
        on_delete=models.CASCADE,
        verbose_name="location for shipping formular",
        related_name="location",
    )

    condition = models.ForeignKey(
        ShippingCondition,
        on_delete=models.CASCADE,
        related_name="condition",
    )


class FormularCondition(SimpleAbstractModel):
    condition = models.ForeignKey(
        ShippingCondition,
        on_delete=models.CASCADE,
        verbose_name="formula of condition",
        related_name="formula_condition",
    )

    uom_group = models.ForeignKey(
        'saledata.UnitOfMeasureGroup',
        on_delete=models.CASCADE,
        related_name='uom_group_condition',
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='uom_condition',
    )
    comparison_operators = models.IntegerField(
        default=1,
        help_text='1 - <; 2 - >; 3 - <=; 4 - >=',
        null=True,

    )
    threshold = models.IntegerField(
        default=0,
        help_text='threshold of unit of measure for comparison operator',
        null=True,
    )
    amount_condition = models.FloatField(
        default=0,
        help_text='fixed price for each condition',
        null=True,
    )
    extra_amount = models.FloatField(
        default=0,
        help_text='extra for amount condition',
        null=True,
    )
