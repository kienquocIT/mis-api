from apps.sales.reconciliation.models import Reconciliation


class ReconForCIFHandler:
    @classmethod
    def auto_create_recon_doc(cls, cif_obj):
        if cif_obj.has_ar_invoice_value > 0:
            Reconciliation.objects.create(
                type=0,
                title=f"Reconciliation for {cif_obj.code}",
                business_partner=cif_obj.customer,
                business_partner_data={
                    'id': str(cif_obj.customer_id),
                    'code': cif_obj.customer.code,
                    'title': cif_obj.customer.title,
                },
                posting_date=cif_obj.posting_date,
                document_date=cif_obj.document_date,
                system_status=1,
                company_id=cif_obj.company_id,
                tenant_id=cif_obj.tenant_id,
                system_auto_create=True
            )
            return True
        return False
