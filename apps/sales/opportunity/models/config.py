from django.db import models
from apps.shared import SimpleAbstractModel


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
