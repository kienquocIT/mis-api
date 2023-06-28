from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared import SimpleAbstractModel

STAGE_CONDITION_ATTRIBUTE = [
    (0, _('Customer')),
    (1, _('Product Category')),
    (2, _('Budget')),
    (3, _('Open Date')),
    (4, _('Close Date')),
    (5, _('Decision maker')),
    (6, _('LostByOtherReason')),
    (7, _('Product.line.detail')),
    (8, _('Competitor.Win')),
    (9, _('Quotation.confirm')),
    (10, _('SaleOrder.status')),
    (11, _('SaleOrder.Delivery.Status')),
    (12, _('Close Deal')),
]

LOGICAL_OPERATORS = [
    (0, _('and')),
    (1, _('or')),
]

COMPARISON_OPERATORS = [
    ('=', _('equal')),
    ('≠', _('different'))
]


class OpportunityConfig(SimpleAbstractModel):
    company = models.OneToOneField(
        'company.Company', on_delete=models.CASCADE,
        related_name='sales_opportunity_config_detail',
    )
    is_select_stage = models.BooleanField(
        default=False,
        verbose_name='user select stage of Opp',
    )
    is_input_win_rate = models.BooleanField(
        default=False,
        verbose_name='user input win rate of Opp',
    )
    is_AM_create = models.BooleanField(
        default=False,
        verbose_name='only Am of Customer is allowed create Opportunity for Customer'
    )

    class Meta:
        verbose_name = 'Opportunity Config of Company'
        verbose_name_plural = 'Opportunity Config of Company'
        default_permissions = ()
        permissions = ()


class CustomerDecisionFactor(SimpleAbstractModel):
    title = models.CharField(
        max_length=100,
    )

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='sales_opportunity_customer_decision_factor',
    )

    class Meta:
        verbose_name = 'Opportunity Customer Decision Factor'
        verbose_name_plural = 'Opportunity Customer Decision Factors'
        ordering = ('-title',)
        default_permissions = ()
        permissions = ()


class OpportunityConfigStage(SimpleAbstractModel):
    indicator = models.CharField(
        max_length=100,
    )
    description = models.CharField(
        max_length=500,
    )
    win_rate = models.FloatField(
        default=0,
        verbose_name="win rate of stage",
    )
    logical_operator = models.SmallIntegerField(
        choices=LOGICAL_OPERATORS,
        default=0,
    )
    condition_datas = models.JSONField(
        default=list,
        help_text='condition in stage of Opportunity Config'
    )
    is_default = models.BooleanField(
        default=False,
    )

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='sales_opportunity_config_stage',
    )
    is_deal_closed = models.BooleanField(
        default=False,
    )
    is_delivery = models.BooleanField(
        default=False,
    )
    is_closed_lost = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = 'Opportunity Config Stage'
        verbose_name_plural = 'Opportunity Config Stages'
        ordering = ('indicator',)
        default_permissions = ()
        permissions = ()


class StageCondition(SimpleAbstractModel):
    stage = models.ForeignKey(
        OpportunityConfigStage,
        on_delete=models.CASCADE,
        related_name='stage_condition',
    )
    condition_property = models.ForeignKey(
        'base.ApplicationProperty',
        on_delete=models.CASCADE,
        related_name='property_stage_condition',
    )

    comparison_operator = models.CharField(
        choices=COMPARISON_OPERATORS,
        max_length=10,
        default='='
    )
    compare_data = models.SmallIntegerField(
        default=0
    )

    class Meta:
        verbose_name = 'Opportunity Config Stage Condition'
        verbose_name_plural = 'Opportunity Config Stage Conditions'
        ordering = ()
        default_permissions = ()
        permissions = ()
