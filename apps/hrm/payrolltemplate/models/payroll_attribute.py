from django.db import models

from apps.shared import MasterDataAbstractModel, SimpleAbstractModel

DATA_TYPE = (
    (0, 'number'),
    (1, 'text'),
    (2, 'date'),
    (3, 'boolean'),
    (4, 'formula'),
)


DATA_SOURCE = (
    (0, 'system'),   # Lấy tự động từ hệ thống (từ hợp đồng, chấm công)
    (1, 'manual'),   # Nhập thủ công mỗi tháng
    (2, 'formula'),  # Tính toán theo công thức từ các cột khác
    (3, 'import'),   # Nhập từ file Excel/CSV
)


class PayrollAttribute(MasterDataAbstractModel):
    column_name = models.CharField(
        max_length=250,
        verbose_name="Column name"
    )
    column_code = models.CharField(
        max_length=250,
        verbose_name="Column code"
    )
    data_type = models.IntegerField(
        verbose_name="Data type",
        choices=DATA_TYPE
    )
    data_source = models.IntegerField(
        verbose_name="Data source",
        choices=DATA_SOURCE
    )
    formula = models.CharField(
        max_length=500,
        verbose_name="expression (if type = formula)",
        null=True,
        blank=True,
    )
    mandatory = models.BooleanField(
        verbose_name='Whether input is required',
        default=True,
    )
    order = models.IntegerField(
        verbose_name="Column position in payroll"
    )

    class Meta:
        verbose_name = 'Payroll attribute'
        verbose_name_plural = 'list Payroll attribute'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class AttributeComponent(SimpleAbstractModel):
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.CASCADE,
        help_text='The company claims that this record belongs to them',
        related_name='company_attribute_component',
    )
    component_title = models.CharField(
        max_length=250,
        verbose_name="Component title",
        blank=True,
        null=True
    )
    component_name = models.CharField(
        max_length=250,
        verbose_name="Component name"
    )
    component_code = models.CharField(
        max_length=250,
        verbose_name="Component code"
    )
    component_type = models.IntegerField(
        verbose_name="Component type"
    )
    component_formula = models.CharField(
        max_length=500,
        verbose_name="expression (if type = formula)",
        null=True,
        blank=True,
    )
    component_mandatory = models.BooleanField(
        verbose_name='Component whether input is required',
        default=True,
    )
    is_system = models.BooleanField(
        verbose_name='Component is system',
        default=False,
        null=True
    )

    class Meta:
        verbose_name = 'Payroll attribute component'
        verbose_name_plural = 'list Payroll attribute component system and user created'
        ordering = ('component_name',)
        default_permissions = ()
        permissions = ()
