from apps.accounting.budget.models import BudgetLineTransaction


class BudgetExtendHandler:

    @classmethod
    def push_budget_line_transaction(cls, instance, data_list):
        old_qs = cls.get_budget_line_transaction(instance=instance)
        if old_qs:
            old_qs.delete()
        BudgetLineTransaction.objects.bulk_create([
            BudgetLineTransaction(
                tenant_id=instance.tenant_id, company_id=instance.company_id,
                app_code=instance.__class__.get_model_code(), doc_id=instance.id,
                **data
            ) for data in data_list
        ])
        return True

    @classmethod
    def get_budget_line_transaction(cls, instance):
        return BudgetLineTransaction.objects.filter(
            tenant_id=instance.tenant_id, company_id=instance.company_id,
            app_code=instance.__class__.get_model_code(), doc_id=instance.id
        )

    @classmethod
    def apply_to_budget_line(cls, instance):
        for bl_transaction in cls.get_budget_line_transaction(instance=instance):
            if bl_transaction.budget_line:
                bl_transaction.budget_line.value_consumed += bl_transaction.value_consume
                bl_transaction.budget_line.save(update_fields=['value_consumed'])
        return True
