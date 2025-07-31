import logging
from django.db import transaction
from apps.accounting.journalentry.models import JournalEntryItem
from apps.sales.reconciliation.models import Reconciliation, ReconciliationItem


logger = logging.getLogger(__name__)


class ReconForCOFHandler:
    @classmethod
    def auto_create_recon_doc(cls, cof_obj):
        """ Tạo phiếu cấn trừ tự động """
        try:
            with transaction.atomic():
                if cof_obj.has_ap_invoice_value > 0:
                    business_partner = cof_obj.customer or cof_obj.supplier
                    recon_obj = Reconciliation.objects.create(
                        recon_type=1,
                        title=f"Reconciliation for {cof_obj.code}",
                        business_partner=business_partner,
                        business_partner_data={
                            'id': str(business_partner.id),
                            'code': business_partner.code,
                            'name': business_partner.name,
                        },
                        posting_date=str(cof_obj.posting_date),
                        document_date=str(cof_obj.document_date),
                        system_status=3,
                        employee_created_id=str(cof_obj.employee_created_id),
                        employee_inherit_id=str(cof_obj.employee_inherit_id),
                        company_id=str(cof_obj.company_id),
                        tenant_id=str(cof_obj.tenant_id),
                        system_auto_create=True
                    )
                    # tạo các dòng cấn trừ
                    bulk_info = []
                    # tìm bút toán của phiếu chi
                    for cof_je_item in JournalEntryItem.objects.filter(
                        journal_entry__je_transaction_app_code=cof_obj.get_model_code(),
                        journal_entry__je_transaction_id=str(cof_obj.id),
                        use_for_recon=True,
                        use_for_recon_type='cof-ap'
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
                                debit_app_code=cof_obj.get_model_code(),
                                debit_doc_id=str(cof_obj.id),
                                debit_doc_data={
                                    'id': str(cof_obj.id),
                                    'code': cof_obj.code,
                                    'title': cof_obj.title,
                                    'document_date': str(cof_obj.document_date),
                                    'posting_date': str(cof_obj.posting_date),
                                    'app_code': cof_obj.get_model_code()
                                } if cof_obj else {},
                                debit_account=cof_je_item.account,
                                debit_account_data={
                                    'id': str(cof_je_item.account_id),
                                    'acc_code': cof_je_item.account.acc_code,
                                    'acc_name': cof_je_item.account.acc_name,
                                    'foreign_acc_name': cof_je_item.account.foreign_acc_name
                                } if cof_je_item.account else {},
                                recon_total=cof_je_item.debit,
                                recon_balance=cof_je_item.debit,
                                recon_amount=cof_je_item.debit
                            )
                        )
                        # đối với từng bút toán của phiếu chi, tìm các bút toán của hóa đơn gắn với phiếu chi đó
                        for item in cof_obj.cash_outflow_item_cash_outflow.all():
                            ap_invoice_obj = item.ap_invoice
                            for ar_je_item in JournalEntryItem.objects.filter(
                                journal_entry__je_transaction_app_code=ap_invoice_obj.get_model_code(),
                                journal_entry__je_transaction_id=str(ap_invoice_obj.id),
                                use_for_recon=True,
                                use_for_recon_type='ap-cof'
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
                                        credit_app_code=ap_invoice_obj.get_model_code(),
                                        credit_doc_id=str(ap_invoice_obj.id),
                                        credit_doc_data={
                                            'id': str(ap_invoice_obj.id),
                                            'code': ap_invoice_obj.code,
                                            'title': ap_invoice_obj.title,
                                            'document_date': str(ap_invoice_obj.date_approved),
                                            'posting_date': str(ap_invoice_obj.date_approved),
                                            'app_code': ap_invoice_obj.get_model_code()
                                        } if ap_invoice_obj else {},
                                        credit_account=ar_je_item.account,
                                        credit_account_data={
                                            'id': str(ar_je_item.account_id),
                                            'acc_code': ar_je_item.account.acc_code,
                                            'acc_name': ar_je_item.account.acc_name,
                                            'foreign_acc_name': ar_je_item.account.foreign_acc_name
                                        } if ar_je_item.account else {},
                                        recon_total=cof_je_item.debit,
                                        recon_balance=cof_je_item.debit,
                                        recon_amount=cof_je_item.debit,
                                    )
                                )
                    ReconciliationItem.objects.bulk_create(bulk_info)
                    print('# Reconciliation created successfully!')
                    return True
                return False
        except Exception as err:
            logger.error(msg=f'[RECON] Error while creating Reconciliation: {err}')
            return False
