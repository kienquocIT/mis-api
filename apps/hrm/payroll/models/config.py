from django.db import models
from apps.shared import SimpleAbstractModel, MasterDataAbstractModel


class PayrollConfig(SimpleAbstractModel):
    company = models.OneToOneField(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='company_payroll_config'
    )

    class Meta:
        verbose_name = 'Payroll Config of Company'
        verbose_name_plural = 'Payroll Config of Company'
        default_permissions = ()
        permissions = ()


class PayrollInsuranceRule(MasterDataAbstractModel):
    payroll_config = models.ForeignKey(
        PayrollConfig,
        on_delete=models.CASCADE,
        related_name='payroll_insurance_rule_config'
    )
    social_insurance_employee = models.FloatField(default=0, help_text="Social insurance employee rate")
    social_insurance_employer = models.FloatField(default=0, help_text="Social insurance employer rate")
    social_insurance_ceiling = models.FloatField(default=0)
    unemployment_insurance_employee = models.FloatField(default=0)
    unemployment_insurance_employer = models.FloatField(default=0)
    unemployment_insurance_ceiling = models.FloatField(default=0)
    health_insurance_employee = models.FloatField(default=0)
    health_insurance_employer = models.FloatField(default=0)
    union_insurance_employee = models.FloatField(default=0)
    union_insurance_employer = models.FloatField(default=0)
    effective_date = models.DateField(null=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Payroll Insurance Rule of Company'
        verbose_name_plural = 'Payroll Insurance Rule of Company'
        default_permissions = ()
        permissions = ()


class PayrollDeductionRule(MasterDataAbstractModel):
    payroll_config = models.ForeignKey(
        PayrollConfig,
        on_delete=models.CASCADE,
        related_name='payroll_deduction_rule_config'
    )
    personal_deduction = models.FloatField(default=0)
    dependent_deduction = models.FloatField(default=0)
    effective_date = models.DateField(null=True)
    status = models.BooleanField(default=True)


class PayrollIncomeTaxRule(MasterDataAbstractModel):
    payroll_config = models.ForeignKey(
        PayrollConfig,
        on_delete=models.CASCADE,
        related_name='payroll_income_tax_rule_config'
    )
    effective_date = models.DateField(null=True)
    status = models.BooleanField(default=True)


class PayrollTaxBracket(MasterDataAbstractModel):
    income_tax_rule = models.ForeignKey(
        PayrollIncomeTaxRule,
        on_delete=models.SET_NULL,
        related_name='payroll_tax_bracket_income_tax_rule'
    )
    order = models.IntegerField(default=1)
    min_amount = models.FloatField(default=0)
    max_amount = models.FloatField(default=0)
    rate = models.FloatField(default=0)
