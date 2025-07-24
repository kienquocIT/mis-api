import logging
from django.db import transaction
from apps.accounting.journalentry.models import JournalEntryItem
from apps.sales.reconciliation.models import Reconciliation, ReconciliationItem


logger = logging.getLogger(__name__)


class ReconForAPInvoiceHandler:
    @classmethod
    def auto_create_recon_doc(cls, ar_invoice_obj):
        """ Tạo phiếu cấn trừ tự động """
        try:
            with transaction.atomic():
                recon_obj = Reconciliation.objects.create(
                    recon_type=0,
                    title=f"Reconciliation for {ar_invoice_obj.code}",
                    business_partner=ar_invoice_obj.customer_mapped,
                    business_partner_data={
                        'id': str(ar_invoice_obj.customer_mapped_id),
                        'code': ar_invoice_obj.customer_mapped.code,
                        'name': ar_invoice_obj.customer_mapped.name,
                    } if ar_invoice_obj.customer_mapped else {},
                    posting_date=str(ar_invoice_obj.posting_date),
                    document_date=str(ar_invoice_obj.document_date),
                    system_status=1,
                    company_id=str(ar_invoice_obj.company_id),
                    tenant_id=str(ar_invoice_obj.tenant_id),
                    system_auto_create=True
                )

                # tạo các dòng cấn trừ
                bulk_info = []
                # tìm bút toán của hóa đơn
                for ar_je_item in JournalEntryItem.objects.filter(
                    journal_entry__je_transaction_app_code=ar_invoice_obj.get_model_code(),
                    journal_entry__je_transaction_id=str(ar_invoice_obj.id),
                    use_for_recon=True,
                    use_for_recon_type='ar-deli'
                ):
                    bulk_info.append(
                        ReconciliationItem(
                            recon=recon_obj,
                            recon_data={
                                'id': str(recon_obj.id),
                                'code': recon_obj.code,
                                'title': recon_obj.title,
                            } if recon_obj else {},
                            order=len(bulk_info),
                            credit_app_code=ar_invoice_obj.get_model_code(),
                            credit_doc_id=str(ar_invoice_obj.id),
                            credit_doc_data={
                                'id': str(ar_invoice_obj.id),
                                'code': ar_invoice_obj.code,
                                'title': ar_invoice_obj.title,
                                'document_date': str(ar_invoice_obj.document_date),
                                'posting_date': str(ar_invoice_obj.posting_date),
                                'app_code': ar_invoice_obj.get_model_code()
                            } if ar_invoice_obj else {},
                            credit_account=ar_je_item.account,
                            credit_account_data={
                                'id': str(ar_je_item.account_id),
                                'acc_code': ar_je_item.account.acc_code,
                                'acc_name': ar_je_item.account.acc_name,
                                'foreign_acc_name': ar_je_item.account.foreign_acc_name
                            } if ar_je_item.account else {},
                            recon_total=ar_je_item.credit,
                            recon_balance=ar_je_item.credit,
                            recon_amount=ar_je_item.credit
                        )
                    )
                    # đối với từng bút toán của hóa đơn, tìm các bút toán của phiếu giao hàng gắn với hóa đơn đó
                    for item in ar_invoice_obj.ar_invoice_deliveries.all():
                        delivery_obj = item.delivery_mapped
                        for deli_je_item in JournalEntryItem.objects.filter(
                            journal_entry__je_transaction_app_code=delivery_obj.get_model_code(),
                            journal_entry__je_transaction_id=str(delivery_obj.id),
                            use_for_recon=True,
                            use_for_recon_type='deli-ar'
                        ):
                            bulk_info.append(
                                ReconciliationItem(
                                    recon=recon_obj,
                                    recon_data={
                                        'id': str(recon_obj.id),
                                        'code': recon_obj.code,
                                        'title': recon_obj.title,
                                    } if recon_obj else {},
                                    order=len(bulk_info),
                                    debit_app_code=delivery_obj.get_model_code(),
                                    debit_doc_id=str(delivery_obj.id),
                                    debit_doc_data={
                                        'id': str(delivery_obj.id),
                                        'code': delivery_obj.code,
                                        'title': delivery_obj.title,
                                        'document_date': str(delivery_obj.date_approved),
                                        'posting_date': str(delivery_obj.date_approved),
                                        'app_code': delivery_obj.get_model_code()
                                    } if delivery_obj else {},
                                    debit_account=deli_je_item.account,
                                    debit_account_data={
                                        'id': str(deli_je_item.account_id),
                                        'acc_code': deli_je_item.account.acc_code,
                                        'acc_name': deli_je_item.account.acc_name,
                                        'foreign_acc_name': deli_je_item.account.foreign_acc_name
                                    } if deli_je_item.account else {},
                                    recon_total=ar_je_item.credit,
                                    recon_balance=ar_je_item.credit,
                                    recon_amount=ar_je_item.credit,
                                )
                            )
                ReconciliationItem.objects.bulk_create(bulk_info)
                print('# Reconciliation created successfully!')
                return True
        except Exception as err:
            logger.error(msg=f'[RECON] Error while creating Reconciliation: {err}')
            return False
