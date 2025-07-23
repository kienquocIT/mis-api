import logging
from django.db import transaction
from apps.accounting.journalentry.models import JournalEntryItem
from apps.sales.reconciliation.models import Reconciliation, ReconciliationItem


logger = logging.getLogger(__name__)


class ReconForCIFHandler:
    @classmethod
    def auto_create_recon_doc(cls, cif_obj):
        """ Tạo phiếu cấn trừ tự động """
        try:
            with transaction.atomic():
                if cif_obj.has_ar_invoice_value > 0:
                    recon_obj = Reconciliation.objects.create(
                        recon_type=0,
                        title=f"Reconciliation for {cif_obj.code}",
                        business_partner=cif_obj.customer,
                        business_partner_data={
                            'id': str(cif_obj.customer_id),
                            'code': cif_obj.customer.code,
                            'name': cif_obj.customer.name,
                        } if cif_obj.customer else {},
                        posting_date=str(cif_obj.posting_date),
                        document_date=str(cif_obj.document_date),
                        system_status=3,
                        company_id=str(cif_obj.company_id),
                        tenant_id=str(cif_obj.tenant_id),
                        system_auto_create=True
                    )
                    # tạo các dòng cấn trừ
                    bulk_info = []
                    # tìm bút toán của phiếu thu
                    for cif_je_item in JournalEntryItem.objects.filter(
                        journal_entry__je_transaction_app_code=cif_obj.get_model_code(),
                        journal_entry__je_transaction_id=str(cif_obj.id),
                        use_for_recon=True,
                        use_for_recon_type='cif-ar'
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
                                credit_app_code=cif_obj.get_model_code(),
                                credit_doc_id=str(cif_obj.id),
                                credit_doc_data={
                                    'id': str(cif_obj.id),
                                    'code': cif_obj.code,
                                    'title': cif_obj.title,
                                    'document_date': str(cif_obj.document_date),
                                    'posting_date': str(cif_obj.posting_date),
                                    'app_code': cif_obj.get_model_code()
                                } if cif_obj else {},
                                credit_account=cif_je_item.account,
                                credit_account_data={
                                    'id': str(cif_je_item.account_id),
                                    'acc_code': cif_je_item.account.acc_code,
                                    'acc_name': cif_je_item.account.acc_name,
                                    'foreign_acc_name': cif_je_item.account.foreign_acc_name
                                } if cif_je_item.account else {},
                                recon_total=cif_je_item.credit,
                                recon_balance=cif_je_item.credit,
                                recon_amount=cif_je_item.credit
                            )
                        )
                        # đối với từng bút toán của phiếu thu, tìm các bút toán của hóa đơn gắn với phiếu thu đó
                        for item in cif_obj.cash_inflow_item_cash_inflow.all():
                            ar_invoice_obj = item.ar_invoice
                            for ar_je_item in JournalEntryItem.objects.filter(
                                journal_entry__je_transaction_app_code=ar_invoice_obj.get_model_code(),
                                journal_entry__je_transaction_id=str(ar_invoice_obj.id),
                                use_for_recon=True,
                                use_for_recon_type='ar-cif'
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
                                        debit_app_code=ar_invoice_obj.get_model_code(),
                                        debit_doc_id=str(ar_invoice_obj.id),
                                        debit_doc_data={
                                            'id': str(ar_invoice_obj.id),
                                            'code': ar_invoice_obj.code,
                                            'title': ar_invoice_obj.title,
                                            'document_date': str(ar_invoice_obj.date_approved),
                                            'posting_date': str(ar_invoice_obj.date_approved),
                                            'app_code': ar_invoice_obj.get_model_code()
                                        } if ar_invoice_obj else {},
                                        debit_account=ar_je_item.account,
                                        debit_account_data={
                                            'id': str(ar_je_item.account_id),
                                            'acc_code': ar_je_item.account.acc_code,
                                            'acc_name': ar_je_item.account.acc_name,
                                            'foreign_acc_name': ar_je_item.account.foreign_acc_name
                                        } if ar_je_item.account else {},
                                        recon_total=cif_je_item.credit,
                                        recon_balance=cif_je_item.credit,
                                        recon_amount=cif_je_item.credit,
                                    )
                                )
                    ReconciliationItem.objects.bulk_create(bulk_info)
                    print('# Reconciliation created successfully!')
                    return True
                return False
        except Exception as err:
            logger.error(msg=f'[RECON] Error while creating Reconciliation: {err}')
            return False
