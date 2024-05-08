from django.db import models

from apps.shared import DataAbstractModel, REPORT_CASHFLOW_TYPE


# REPORT REVENUE
class ReportRevenue(DataAbstractModel):
    sale_order = models.OneToOneField(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name='report_revenue_sale_order',
        null=True,
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
    is_initial = models.BooleanField(default=False, help_text="flag to know this is record created by revenue plan")

    @classmethod
    def push_from_so(
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

    @classmethod
    def push_from_plan(
            cls,
            tenant_id,
            company_id,
            employee_created_id,
            employee_inherit_id,
            group_inherit_id,
    ):
        if not cls.objects.filter(
                tenant_id=tenant_id,
                company_id=company_id,
                employee_inherit_id=employee_inherit_id,
                group_inherit_id=group_inherit_id,
                is_initial=True
        ).exists():
            cls.objects.create(
                tenant_id=tenant_id,
                company_id=company_id,
                employee_created_id=employee_created_id,
                employee_inherit_id=employee_inherit_id,
                group_inherit_id=group_inherit_id,
                is_initial=True,
            )
        return True

    class Meta:
        verbose_name = 'Report Revenue'
        verbose_name_plural = 'Report Revenues'
        ordering = ('employee_inherit__code',)
        default_permissions = ()
        permissions = ()


# REPORT PRODUCT
class ReportProduct(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name='report_product_sale_order',
        null=True,
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_product_product',
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
    def push_from_so(
            cls,
            tenant_id,
            company_id,
            sale_order_id,
            product_id,
            employee_created_id,
            employee_inherit_id,
            group_inherit_id,
            date_approved,
            revenue: float,
            gross_profit: float,
            net_income: float,
    ):
        cls.objects.create(
            tenant_id=tenant_id,
            company_id=company_id,
            sale_order_id=sale_order_id,
            product_id=product_id,
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
        verbose_name = 'Report Product'
        verbose_name_plural = 'Report Products'
        ordering = ('product__code',)
        default_permissions = ()
        permissions = ()


# REPORT CUSTOMER
class ReportCustomer(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name='report_customer_sale_order',
        null=True,
    )
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name='report_customer_customer',
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
    def push_from_so(
            cls,
            tenant_id,
            company_id,
            sale_order_id,
            customer_id,
            employee_created_id,
            employee_inherit_id,
            group_inherit_id,
            date_approved,
            revenue: float,
            gross_profit: float,
            net_income: float,
    ):
        cls.objects.create(
            tenant_id=tenant_id,
            company_id=company_id,
            sale_order_id=sale_order_id,
            customer_id=customer_id,
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
        verbose_name = 'Report Customer'
        verbose_name_plural = 'Report Customers'
        ordering = ('customer__code',)
        default_permissions = ()
        permissions = ()


# REPORT PIPELINE
class ReportPipeline(DataAbstractModel):
    opportunity = models.OneToOneField(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        related_name='report_pipeline_opportunity',
    )

    @classmethod
    def push_from_opp(
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


# REPORT CASHFLOW
class ReportCashflow(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name='report_cashflow_sale_order',
        null=True,
    )
    purchase_order = models.ForeignKey(
        'purchasing.PurchaseOrder',
        on_delete=models.CASCADE,
        related_name='report_cashflow_purchase_order',
        null=True
    )
    cashflow_type = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(REPORT_CASHFLOW_TYPE),
    )
    group_inherit = models.ForeignKey(
        'hr.Group',
        null=True,
        on_delete=models.SET_NULL,
        related_name='report_cashflow_group_inherit',
    )
    due_date = models.DateTimeField(null=True)
    # so
    value_estimate_sale = models.FloatField(default=0)
    value_actual_sale = models.FloatField(default=0)
    value_variance_sale = models.FloatField(default=0)
    # po
    value_estimate_cost = models.FloatField(default=0)
    value_actual_cost = models.FloatField(default=0)
    value_variance_cost = models.FloatField(default=0)

    @classmethod
    def push_from_so_po(cls, bulk_data):
        cls.objects.bulk_create(bulk_data)
        return True

    class Meta:
        verbose_name = 'Report Cashflow'
        verbose_name_plural = 'Report Cashflows'
        ordering = ('-due_date',)
        default_permissions = ()
        permissions = ()
