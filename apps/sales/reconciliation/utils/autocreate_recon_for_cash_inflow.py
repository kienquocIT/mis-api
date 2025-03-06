from apps.sales.reconciliation.models import Reconciliation, ReconciliationItem


class ReconForCIFHandler:
    @classmethod
    def auto_create_recon_doc(cls, cif_obj):
        if cif_obj.has_ar_invoice_value > 0:
            recon_obj = Reconciliation.objects.create(
                type=0,
                code=f"RECON000{Reconciliation.objects.filter(company_id=cif_obj.company_id).count()}",
                title=f"Reconciliation for {cif_obj.code}",
                customer=cif_obj.customer,
                customer_data=cif_obj.customer_data,
                posting_date=cif_obj.posting_date,
                document_date=cif_obj.document_date,
                system_status=1,
                company_id=cif_obj.company_id,
                tenant_id=cif_obj.tenant_id,
                system_auto_create=True
            )
            order = 0
            for cif_item in cif_obj.cash_inflow_item_cash_inflow.all():
                if cif_item.ar_invoice:
                    ReconciliationItem.objects.create(
                        recon=recon_obj,
                        recon_data={
                            'id': str(recon_obj.id),
                            'code': recon_obj.code,
                            'title': recon_obj.title
                        },
                        order=order,
                        ar_invoice=cif_item.ar_invoice,
                        ar_invoice_data=cif_item.ar_invoice_data,
                        recon_balance=cif_item.sum_balance_value,
                        recon_amount=cif_item.sum_payment_value,
                        note='',
                        accounting_account='1311'
                    )
                    ReconciliationItem.objects.create(
                        recon=recon_obj,
                        recon_data={
                            'id': str(recon_obj.id),
                            'code': recon_obj.code,
                            'title': recon_obj.title
                        },
                        order=order + 1,
                        cash_inflow=cif_obj,
                        cash_inflow_data={
                            'id': str(cif_obj.id),
                            'code': cif_obj.code,
                            'title': cif_obj.title,
                            'type_doc': 'Cash inflow',
                            'document_date': str(cif_obj.document_date),
                            'posting_date': str(cif_obj.posting_date),
                            'sum_total_value': cif_obj.total_value
                        },
                        recon_balance=cif_item.sum_balance_value,
                        recon_amount=cif_item.sum_payment_value,
                        note='',
                        accounting_account='1311'
                    )
                    order += 2
            return True
        return False
