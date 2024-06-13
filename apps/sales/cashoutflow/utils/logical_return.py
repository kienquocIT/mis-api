from apps.sales.opportunity.models import OpportunityActivityLogs


class ReturnAdHandler:

    # OPPORTUNITY LOG
    @classmethod
    def push_opportunity_log(cls, instance):
        if instance.advance_payment:
            if instance.advance_payment.opportunity_mapped:
                OpportunityActivityLogs.push_opportunity_log(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    opportunity_id=instance.advance_payment.opportunity_mapped_id,
                    employee_created_id=instance.employee_created_id,
                    app_code=str(instance.__class__.get_model_code()),
                    doc_id=instance.id,
                    log_type=0,
                    doc_data={
                        'id': str(instance.id),
                        'title': instance.title,
                        'code': instance.code,
                        'system_status': instance.system_status,
                        'date_created': str(instance.date_created),
                    }
                )
        return True
