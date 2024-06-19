from apps.masterdata.saledata.models import AccountActivity


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
