from django.db import models

from apps.shared import DataAbstractModel, MasterDataAbstractModel


class FinalAcceptance(DataAbstractModel):
    sale_order = models.OneToOneField(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="final_acceptance_sale_order",
    )
    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        verbose_name="opportunity",
        related_name="final_acceptance_opportunity",
        null=True,
    )

    @classmethod
    def create_final_acceptance_from_so(
            cls,
            tenant_id,
            company_id,
            sale_order_id,
            employee_created_id,
            employee_inherit_id,
            opportunity_id,
            list_data_indicator: list,
    ):
        if not cls.objects.filter(tenant_id=tenant_id, company_id=company_id, sale_order_id=sale_order_id).exists():
            final_acceptance = cls.objects.create(
                tenant_id=tenant_id,
                company_id=company_id,
                sale_order_id=sale_order_id,
                employee_created_id=employee_created_id,
                employee_inherit_id=employee_inherit_id,
                opportunity_id=opportunity_id,
            )
            if final_acceptance:
                list_indicator = [
                    FinalAcceptanceIndicator(
                        final_acceptance=final_acceptance,
                        **data_indicator,
                    )
                    for data_indicator in list_data_indicator
                ]
                FinalAcceptanceIndicator.create_final_acceptance_indicators(
                    tenant_id=tenant_id,
                    company_id=company_id,
                    final_acceptance_id=final_acceptance.id,
                    list_indicator=list_indicator,
                )
        return True

    class Meta:
        verbose_name = 'Final Acceptance'
        verbose_name_plural = 'Final Acceptances'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class FinalAcceptanceIndicator(MasterDataAbstractModel):
    final_acceptance = models.ForeignKey(
        FinalAcceptance,
        on_delete=models.CASCADE,
        verbose_name="final acceptance",
        related_name="fa_indicator_final_acceptance",
    )
    sale_order_indicator = models.OneToOneField(
        'saleorder.SaleOrderIndicator',
        on_delete=models.CASCADE,
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="fa_indicator_sale_order",
        null=True,
    )
    indicator_value = models.FloatField(default=0)
    actual_value = models.FloatField(default=0)
    different_value = models.FloatField(default=0)
    rate_value = models.FloatField(default=0)
    remark = models.CharField(
        verbose_name='remark',
        max_length=500,
        blank=True,
        null=True,
    )
    order = models.IntegerField(default=1)
    is_indicator = models.BooleanField(default=False)
    is_sale_order = models.BooleanField(default=False)
    is_delivery = models.BooleanField(default=False)
    is_payment = models.BooleanField(default=False)

    @classmethod
    def create_final_acceptance_indicators(
            cls,
            tenant_id,
            company_id,
            final_acceptance_id,
            list_indicator,
    ):
        if not cls.objects.filter(
                tenant_id=tenant_id,
                company_id=company_id,
                final_acceptance_id=final_acceptance_id
        ).exists():
            cls.objects.bulk_create(list_indicator)
        return True

    class Meta:
        verbose_name = 'Final Acceptance Indicator'
        verbose_name_plural = 'Final Acceptance Indicators'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
