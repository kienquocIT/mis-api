import logging
from django.db import transaction
from apps.accounting.journalentry.models import JournalEntryItem
from apps.sales.reconciliation.models import Reconciliation, ReconciliationItem


logger = logging.getLogger(__name__)


class ReconForAPInvoiceHandler:
    @classmethod
    def auto_create_recon_doc(cls, ap_invoice_obj):
        """ Tạo phiếu cấn trừ tự động """
        try:
            with transaction.atomic():
                recon_obj = Reconciliation.objects.create(
                    recon_type=1,
                    title=f"Reconciliation for {ap_invoice_obj.code}",
                    business_partner=ap_invoice_obj.supplier_mapped,
                    business_partner_data={
                        'id': str(ap_invoice_obj.supplier_mapped_id),
                        'code': ap_invoice_obj.supplier_mapped.code,
                        'name': ap_invoice_obj.supplier_mapped.name,
                    } if ap_invoice_obj.supplier_mapped else {},
                    posting_date=str(ap_invoice_obj.posting_date),
                    document_date=str(ap_invoice_obj.document_date),
                    system_status=3,
                    company_id=str(ap_invoice_obj.company_id),
                    tenant_id=str(ap_invoice_obj.tenant_id),
                    system_auto_create=True
                )

                # tạo các dòng cấn trừ
                bulk_info = []
                # tìm bút toán của hóa đơn
                for ap_je_item in JournalEntryItem.objects.filter(
                    journal_entry__je_transaction_app_code=ap_invoice_obj.get_model_code(),
                    journal_entry__je_transaction_id=str(ap_invoice_obj.id),
                    use_for_recon=True,
                    use_for_recon_type='ap-gr'
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
                            debit_app_code=ap_invoice_obj.get_model_code(),
                            debit_doc_id=str(ap_invoice_obj.id),
                            debit_doc_data={
                                'id': str(ap_invoice_obj.id),
                                'code': ap_invoice_obj.code,
                                'title': ap_invoice_obj.title,
                                'document_date': str(ap_invoice_obj.document_date),
                                'posting_date': str(ap_invoice_obj.posting_date),
                                'app_code': ap_invoice_obj.get_model_code()
                            } if ap_invoice_obj else {},
                            debit_account=ap_je_item.account,
                            debit_account_data={
                                'id': str(ap_je_item.account_id),
                                'acc_code': ap_je_item.account.acc_code,
                                'acc_name': ap_je_item.account.acc_name,
                                'foreign_acc_name': ap_je_item.account.foreign_acc_name
                            } if ap_je_item.account else {},
                            recon_total=ap_je_item.debit,
                            recon_balance=ap_je_item.debit,
                            recon_amount=ap_je_item.debit
                        )
                    )
                    # đối với từng bút toán của hóa đơn, tìm các bút toán của phiếu nhập hàng gắn với hóa đơn đó
                    for item in ap_invoice_obj.ap_invoice_goods_receipts.all():
                        goods_receipt_obj = item.goods_receipt_mapped
                        for deli_je_item in JournalEntryItem.objects.filter(
                            journal_entry__je_transaction_app_code=goods_receipt_obj.get_model_code(),
                            journal_entry__je_transaction_id=str(goods_receipt_obj.id),
                            use_for_recon=True,
                            use_for_recon_type='gr-ap'
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
                                    credit_app_code=goods_receipt_obj.get_model_code(),
                                    credit_doc_id=str(goods_receipt_obj.id),
                                    credit_doc_data={
                                        'id': str(goods_receipt_obj.id),
                                        'code': goods_receipt_obj.code,
                                        'title': goods_receipt_obj.title,
                                        'document_date': str(goods_receipt_obj.date_approved),
                                        'posting_date': str(goods_receipt_obj.date_approved),
                                        'app_code': goods_receipt_obj.get_model_code()
                                    } if goods_receipt_obj else {},
                                    credit_account=deli_je_item.account,
                                    credit_account_data={
                                        'id': str(deli_je_item.account_id),
                                        'acc_code': deli_je_item.account.acc_code,
                                        'acc_name': deli_je_item.account.acc_name,
                                        'foreign_acc_name': deli_je_item.account.foreign_acc_name
                                    } if deli_je_item.account else {},
                                    recon_total=ap_je_item.debit,
                                    recon_balance=ap_je_item.debit,
                                    recon_amount=ap_je_item.debit,
                                )
                            )
                ReconciliationItem.objects.bulk_create(bulk_info)
                print('# Reconciliation created successfully!')
                return True
        except Exception as err:
            logger.error(msg=f'[RECON] Error while creating Reconciliation: {err}')
            return False
