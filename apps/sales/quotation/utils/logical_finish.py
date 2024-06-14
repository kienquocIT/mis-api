from apps.masterdata.saledata.models import AccountActivity


class QuotationFinishHandler:

    # OPPORTUNITY STAGE
    @classmethod
    def update_opportunity_stage_by_quotation(cls, instance):
        if instance.opportunity:
            # update field quotation
            instance.opportunity.quotation = instance
            instance.opportunity.save(**{
                'update_fields': ['quotation'],
                'quotation_confirm': instance.is_customer_confirm,
            })
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
