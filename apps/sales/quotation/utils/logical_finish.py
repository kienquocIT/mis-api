from apps.masterdata.saledata.models import AccountActivity
from apps.shared import DisperseModel


class QuotationFinishHandler:

    # OPPORTUNITY STAGE
    @classmethod
    def update_opportunity(cls, instance):
        if instance.opportunity:
            instance.opportunity.quotation = instance if instance.system_status == 3 else None
            instance.opportunity.save(update_fields=['quotation'])
            # handle stage & win_rate
            instance.opportunity.handle_stage_win_rate(obj=instance.opportunity)
        return True

    # CUSTOMER ACTIVITY
    @classmethod
    def push_to_customer_activity(cls, instance):
        if instance.customer:
            AccountActivity.push_activity(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                account_id=instance.customer_id,
                app_code=instance._meta.label_lower,
                document_id=instance.id,
                title=instance.title,
                code=instance.code,
                date_activity=instance.date_approved,
                revenue=instance.indicator_revenue,
            )
        return True

    # REPORT
    @classmethod
    def push_to_report_revenue(cls, instance):
        model_target = DisperseModel(app_model='report.reportrevenue').get_model()
        if model_target and hasattr(model_target, 'push_from_so'):
            model_target.push_from_so(**{
                'tenant_id': instance.tenant_id,
                'company_id': instance.company_id,
                'sale_order_id': None,
                'quotation_id': instance.id,
                'opportunity_id': instance.opportunity_id,
                'customer_id': instance.customer_id,
                'employee_created_id': instance.employee_created_id,
                'employee_inherit_id': instance.employee_inherit_id,
                'group_inherit_id': instance.employee_inherit.group_id if instance.employee_inherit else None,
                'date_approved': instance.date_approved,
                'revenue': instance.indicator_revenue,
                'gross_profit': instance.indicator_gross_profit,
                'net_income': instance.indicator_net_income,
            })
        return True
