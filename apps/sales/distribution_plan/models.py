from django.db import models
from apps.shared import SimpleAbstractModel, DataAbstractModel
# Create your models here.


class DistributionPlan(DataAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        related_name='distribution_plan_product',
        on_delete=models.CASCADE
    )
    start_date = models.DateField()
    no_of_month = models.IntegerField()

    product_price = models.FloatField(default=0)
    break_event_point = models.FloatField(default=0)
    expected_number = models.FloatField(default=0)
    net_income = models.FloatField(default=0)
    rate = models.FloatField(default=0)
    plan_description = models.TextField(default="", blank=True, null=True)

    @classmethod
    def generate_code(cls, company_id):
        records = cls.objects.filter(company_id=company_id).count()
        return f"DP00{records+1}"

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.code = self.generate_code(self.company_id)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Distribution Plan'
        verbose_name_plural = 'Distribution Plans'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class DistributionPlanSupplier(SimpleAbstractModel):
    distribution_plan = models.ForeignKey(
        DistributionPlan,
        related_name='distribution_plan_supplier_distribution_plan',
        on_delete=models.CASCADE
    )
    supplier = models.ForeignKey(
        'saledata.Account',
        related_name='distribution_plan_supplier_supplier',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Distribution Plan Supplier'
        verbose_name_plural = 'Distribution Plan Supplier'
        ordering = ()
        default_permissions = ()
        permissions = ()


class DistributionPlanFixedCost(SimpleAbstractModel):
    distribution_plan = models.ForeignKey(
        DistributionPlan,
        related_name='distribution_plan_fixed_cost_distribution_plan',
        on_delete=models.CASCADE
    )
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        related_name='distribution_plan_fixed_cost_expense_item',
        on_delete=models.CASCADE
    )
    value = models.FloatField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Distribution Plan Fixed Cost'
        verbose_name_plural = 'Distribution Plan Fixed Costs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class DistributionPlanVariableCost(SimpleAbstractModel):
    distribution_plan = models.ForeignKey(
        DistributionPlan,
        related_name='distribution_plan_variable_cost_distribution_plan',
        on_delete=models.CASCADE
    )
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        related_name='distribution_plan_variable_cost_expense_item',
        on_delete=models.CASCADE
    )
    value = models.FloatField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Distribution Plan Variable Cost'
        verbose_name_plural = 'Distribution Plan Variable Costs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
