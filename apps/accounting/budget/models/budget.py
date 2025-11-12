from django.db import models
from apps.shared import (MasterDataAbstractModel, SYSTEM_STATUS, DisperseModel)


# BUDGET
class Budget(MasterDataAbstractModel):
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE, related_name='budget_application')
    app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}'
    )
    doc_id = models.UUIDField(verbose_name='Feature document ID')
    total = models.FloatField(default=0)
    budget_line_data = models.JSONField(default=list, help_text="json data of budget lines")
    employee_inherit = models.ForeignKey(
        'hr.Employee',
        null=True,
        on_delete=models.SET_NULL,
        related_name='budget_employee_inherit',
    )
    group_inherit = models.ForeignKey(
        'hr.Group',
        null=True,
        on_delete=models.SET_NULL,
        related_name='budget_group_inherit',
    )
    system_status = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(SYSTEM_STATUS),
    )
    date_approved = models.DateTimeField(
        null=True,
        help_text='Push when WF of document is finished'
    )

    @classmethod
    def push_budget(cls, tenant_id, company_id, app_code, doc_id, **kwargs):
        app_obj = cls._get_application(app_code=app_code)
        if app_obj:
            obj, _created = cls.objects.get_or_create(
                tenant_id=tenant_id, company_id=company_id,
                application=app_obj, app_code=app_code, doc_id=doc_id,
                defaults={
                    'employee_inherit_id': kwargs.get('employee_inherit_id', None),
                    'group_inherit_id': kwargs.get('group_inherit_id', None),
                    'system_status': kwargs.get('system_status', 0),
                    'date_approved': kwargs.get('date_approved', None),
                    'budget_line_data': kwargs.get('budget_line_data', []),
                }
            )
            # create new record
            if _created is True:
                return True
            # update old record
            update_fields = []
            for key, value in kwargs.items():
                setattr(obj, key, value)
                update_fields.append(key)
            obj.save(update_fields=update_fields)
            # push BudgetLine
            if 'budget_line_data' in update_fields:
                obj.budget_line_budget.all().delete()
                budget_line_objs = BudgetLine.objects.bulk_create([
                    BudgetLine(
                        tenant_id=tenant_id, company_id=company_id,
                        **budget_line
                    ) for budget_line in obj.budget_line_data
                ])
                if budget_line_objs:
                    for budget_line in budget_line_objs:
                        BudgetLineDimension.objects.bulk_create([
                            BudgetLineDimension(
                                tenant_id=tenant_id, company_id=company_id,
                                **dimension
                            ) for dimension in budget_line.dimension_data
                        ])
        return True

    @classmethod
    def _get_application(cls, app_code):
        model_app = DisperseModel(app_model='base.application').get_model()
        if model_app and hasattr(model_app, 'objects'):
            arr = app_code.split('.')
            if len(arr) == 2:
                return model_app.objects.filter(app_label=arr[0], model_code=arr[1]).first()
        return None

    class Meta:
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        ordering = ('-date_approved',)
        default_permissions = ()
        permissions = ()


# BUDGET LINE
class BudgetLine(MasterDataAbstractModel):
    budget = models.ForeignKey('budget.Budget', on_delete=models.CASCADE, related_name='budget_line_budget')
    remark = models.TextField(blank=True)
    value_planned = models.FloatField(default=0, help_text="Base value pushed from document")
    value_consumed = models.FloatField(default=0, help_text="Consumed value on value_planned")
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Budget line'
        verbose_name_plural = 'Budget lines'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# BUDGET LINE DIMENSION
class BudgetLineDimension(MasterDataAbstractModel):
    budget_line = models.ForeignKey(
        'budget.BudgetLine', on_delete=models.CASCADE, related_name='budget_line_dimension_budget_line'
    )
    md_app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}'
    )
    md_id = models.UUIDField(verbose_name='Master data ID')
    dimension = models.ForeignKey(
        'budget.BudgetLine', on_delete=models.CASCADE, related_name='budget_line_dimension_dimension'
    )
    dimension_value = models.ForeignKey(
        'budget.BudgetLine', on_delete=models.CASCADE, related_name='budget_line_dimension_dimension_value'
    )

    class Meta:
        verbose_name = 'Budget line Dimension'
        verbose_name_plural = 'Budget line Dimensions'
        default_permissions = ()
        permissions = ()
