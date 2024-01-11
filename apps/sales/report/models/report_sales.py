from django.db import models

from apps.shared import DataAbstractModel


class ReportRevenue(DataAbstractModel):
    sale_order = models.OneToOneField(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
    )
    group_inherit = models.ForeignKey(
        'hr.Group',
        null=True,
        on_delete=models.SET_NULL,
        related_name='report_revenue_group_inherit',
    )
    revenue = models.FloatField(default=0)
    gross_profit = models.FloatField(default=0)
    net_income = models.FloatField(default=0)

    @classmethod
    def create_report_revenue_from_so(
            cls,
            tenant_id,
            company_id,
            sale_order_id,
            employee_created_id,
            employee_inherit_id,
            group_inherit_id,
            date_approved,
            revenue: float,
            gross_profit: float,
            net_income: float,
    ):
        if not cls.objects.filter(tenant_id=tenant_id, company_id=company_id, sale_order_id=sale_order_id).exists():
            cls.objects.create(
                tenant_id=tenant_id,
                company_id=company_id,
                sale_order_id=sale_order_id,
                employee_created_id=employee_created_id,
                employee_inherit_id=employee_inherit_id,
                group_inherit_id=group_inherit_id,
                date_approved=date_approved,
                revenue=revenue,
                gross_profit=gross_profit,
                net_income=net_income,
            )
        return True

    class Meta:
        verbose_name = 'Report Revenue'
        verbose_name_plural = 'Report Revenues'
        ordering = ('employee_inherit__code',)
        default_permissions = ()
        permissions = ()


class ReportProduct(DataAbstractModel):
    product = models.OneToOneField(
        'saledata.Product',
        on_delete=models.CASCADE,
    )
    group_inherit = models.ForeignKey(
        'hr.Group',
        null=True,
        on_delete=models.SET_NULL,
        related_name='report_product_group_inherit',
    )
    revenue = models.FloatField(default=0)
    gross_profit = models.FloatField(default=0)
    net_income = models.FloatField(default=0)

    @classmethod
    def update_report_product_from_so(
            cls,
            tenant_id,
            company_id,
            product_id,
            employee_created_id,
            employee_inherit_id,
            group_inherit_id,
            date_approved,
            revenue: float,
            gross_profit: float,
            net_income: float,
    ):
        obj, _created = cls.objects.get_or_create(
            tenant_id=tenant_id, company_id=company_id, product_id=product_id,
            defaults={
                'employee_created_id': employee_created_id,
                'employee_inherit_id': employee_inherit_id,
                'group_inherit_id': group_inherit_id,
                'date_approved': date_approved,
                'revenue': revenue,
                'gross_profit': gross_profit,
                'net_income': net_income,
            }
        )
        if _created is True:
            return True
        obj.revenue += revenue
        obj.gross_profit += gross_profit
        obj.net_income += net_income
        obj.save(update_fields=['revenue', 'gross_profit', 'net_income'])
        return True

    class Meta:
        verbose_name = 'Report Product'
        verbose_name_plural = 'Report Products'
        ordering = ('product__code',)
        default_permissions = ()
        permissions = ()


class ReportCustomer(DataAbstractModel):
    customer = models.OneToOneField(
        'saledata.Account',
        on_delete=models.CASCADE,
    )
    group_inherit = models.ForeignKey(
        'hr.Group',
        null=True,
        on_delete=models.SET_NULL,
        related_name='report_customer_group_inherit',
    )
    revenue = models.FloatField(default=0)
    gross_profit = models.FloatField(default=0)
    net_income = models.FloatField(default=0)

    @classmethod
    def update_report_customer_from_so(
            cls,
            tenant_id,
            company_id,
            customer_id,
            employee_created_id,
            employee_inherit_id,
            group_inherit_id,
            date_approved,
            revenue: float,
            gross_profit: float,
            net_income: float,
    ):
        obj, _created = cls.objects.get_or_create(
            tenant_id=tenant_id, company_id=company_id, customer_id=customer_id,
            defaults={
                'employee_created_id': employee_created_id,
                'employee_inherit_id': employee_inherit_id,
                'group_inherit_id': group_inherit_id,
                'date_approved': date_approved,
                'revenue': revenue,
                'gross_profit': gross_profit,
                'net_income': net_income,
            }
        )
        if _created is True:
            return True
        obj.revenue += revenue
        obj.gross_profit += gross_profit
        obj.net_income += net_income
        obj.save(update_fields=['revenue', 'gross_profit', 'net_income'])
        return True

    class Meta:
        verbose_name = 'Report Customer'
        verbose_name_plural = 'Report Customers'
        ordering = ('customer__code',)
        default_permissions = ()
        permissions = ()


class ReportPipeline(DataAbstractModel):
    opportunity = models.OneToOneField(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
    )

    @classmethod
    def create_report_pipeline_by_opp(
            cls,
            tenant_id,
            company_id,
            opportunity_id,
            employee_inherit_id,
    ):
        cls.objects.get_or_create(
            tenant_id=tenant_id, company_id=company_id, opportunity_id=opportunity_id,
            defaults={
                'employee_inherit_id': employee_inherit_id,
            }
        )
        return True

    class Meta:
        verbose_name = 'Report Pipeline'
        verbose_name_plural = 'Report Pipelines'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
