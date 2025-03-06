from apps.sales.reconciliation.models import Reconciliation


class ReconForARInvoiceHandler:
    @classmethod
    def auto_create_recon_doc(cls, ar_invoice_obj):
        Reconciliation.objects.create(
            type=0,
            code=f"RECON000{Reconciliation.objects.filter(company_id=ar_invoice_obj.company_id).count()}",
            title=f"Reconciliation for {ar_invoice_obj.code}",
            customer=ar_invoice_obj.customer_mapped,
            customer_data={
                'id': str(ar_invoice_obj.customer_mapped_id),
                'code': ar_invoice_obj.customer_mapped.code,
                'title': ar_invoice_obj.customer_mapped.title,
            },
            posting_date=ar_invoice_obj.posting_date,
            document_date=ar_invoice_obj.document_date,
            system_status=1,
            company_id=ar_invoice_obj.company_id,
            tenant_id=ar_invoice_obj.tenant_id,
            system_auto_create=True
        )
        return True
