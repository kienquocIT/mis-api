from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.sales.reconciliation.models import Reconciliation, ReconciliationItem


class ReconForARInvoiceHandler:
    @classmethod
    def auto_create_recon_doc(cls, ar_invoice_obj):
        recon_obj = Reconciliation.objects.create(
            recon_type=0,
            title=f"Reconciliation for {ar_invoice_obj.code}",
            business_partner=ar_invoice_obj.customer_mapped,
            business_partner_data={
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

        for item in ar_invoice_obj.ar_invoice_deliveries.all():
            for je_item in item.delivery_mapped.je_items.filter(je_item_type=1):
                ReconciliationItem.objects.create(
                    recon=recon_obj,
                    recon_data={
                        'id': str(recon_obj.id),
                        'code': recon_obj.code,
                        'title': recon_obj.title,
                    },
                    order=1,
                    credit_app_code='delivery.orderdeliverysub',
                    credit_doc_id=str(item.delivery_mapped_id),
                    credit_doc_data={
                        'id': str(item.delivery_mapped_id),
                        'code': item.delivery_mapped.code,
                        'title': item.delivery_mapped.title,
                        'document_date': '',
                        'posting_date': '',
                    },
                    credit_account=je_item.account,
                    credit_account_data={
                        'id': str(je_item.account_id),
                        'acc_code': je_item.account.acc_code,
                        'acc_name': je_item.account.acc_name,
                        'foreign_acc_name': je_item.account.foreign_acc_name
                    } if je_item.account else {},
                    recon_total=je_item.credit,
                    recon_balance=je_item.credit,
                    recon_amount=je_item.credit
                )

        ReconciliationItem.objects.create(
            recon=recon_obj,
            recon_data={
                'id': str(recon_obj.id),
                'code': recon_obj.code,
                'title': recon_obj.title,
            },
            order=1,
            debit_app_code='arinvoice.arinvoice',
            debit_doc_id=str(ar_invoice_obj.id),
            debit_doc_data={
                'id': str(ar_invoice_obj.id),
                'code': ar_invoice_obj.code,
                'title': ar_invoice_obj.title,
                'document_date': ar_invoice_obj.document_date,
                'posting_date': ar_invoice_obj.posting_date,
            },
            debit_account=je_item.account,
            debit_account_data={
                'id': str(je_item.account_id),
                'acc_code': je_item.account.acc_code,
                'acc_name': je_item.account.acc_name,
                'foreign_acc_name': je_item.account.foreign_acc_name
            } if je_item.account else {},
            recon_total=je_item.credit,
            recon_balance=je_item.credit,
            recon_amount=je_item.credit
        )
        return True
