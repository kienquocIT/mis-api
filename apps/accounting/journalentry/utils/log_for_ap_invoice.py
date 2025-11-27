import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import AccountDetermination, AccountDeterminationSub
from apps.accounting.journalentry.models import JournalEntry
from apps.sales.report.models import ReportStockLog


logger = logging.getLogger(__name__)


class JEForAPInvoiceHandler:
    @classmethod
    def parse_je_line_data_old(cls, ap_invoice_obj):
        debit_rows_data = []
        credit_rows_data = []
        sum_cost = 0
        for item in ap_invoice_obj.ap_invoice_goods_receipts.all():
            goods_receipt_obj = item.goods_receipt_mapped
            for gr_prd_obj in goods_receipt_obj.goods_receipt_product_goods_receipt.all():
                # lấy cost lúc nhập của sp
                stock_log_item = ReportStockLog.objects.filter(
                    product=gr_prd_obj.product,
                    trans_code=goods_receipt_obj.code,
                    trans_id=str(goods_receipt_obj.id)
                ).first()
                cost = stock_log_item.value if stock_log_item else 0
                sum_cost += cost

        account_list = AccountDetermination.get_sub_items_data(
            tenant_id=ap_invoice_obj.tenant_id,
            company_id=ap_invoice_obj.company_id,
            foreign_title='Customer overpayment'
        )
        if len(account_list) == 1:
            debit_rows_data.append({
                # (-) nhập hàng chưa nhập hóa đơn (mđ: 33881)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': None,
                'debit': sum_cost,
                'credit': 0,
                'is_fc': False,
                'taxable_value': 0,
                'use_for_recon': True,
                'use_for_recon_type': 'ap-gr'
            })

        account_list = AccountDetermination.get_sub_items_data(
            tenant_id=ap_invoice_obj.tenant_id,
            company_id=ap_invoice_obj.company_id,
            foreign_title='Payable to suppliers'
        )
        if len(account_list) == 1:
            credit_rows_data.append({
                # (+) phải trả cho NCC (mđ: 331)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': ap_invoice_obj.supplier_mapped,
                'debit': 0,
                'credit': ap_invoice_obj.sum_after_tax_value,
                'is_fc': False,
                'taxable_value': 0,
                'use_for_recon': True,
                'use_for_recon_type': 'ap-cof'
            })

        account_list = AccountDetermination.get_sub_items_data(
            tenant_id=ap_invoice_obj.tenant_id,
            company_id=ap_invoice_obj.company_id,
            foreign_title='Purchases tax'
        )
        if len(account_list) == 1:
            debit_rows_data.append({
                # (-) thuế GTGT đầu vào (mđ: 1331)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': None,
                'debit': ap_invoice_obj.sum_tax_value,
                'credit': 0,
                'is_fc': False,
                'taxable_value': ap_invoice_obj.sum_after_tax_value,
            })

        return debit_rows_data, credit_rows_data

    @staticmethod
    def get_cost_from_stock_log(ap_invoice_obj):
        sum_cost = 0
        for item in ap_invoice_obj.ap_invoice_goods_receipts.all():
            goods_receipt_obj = item.goods_receipt_mapped
            for gr_prd_obj in goods_receipt_obj.goods_receipt_product_goods_receipt.all():
                for stock_log_item in ReportStockLog.objects.filter(
                    product=gr_prd_obj.product,
                    trans_code=goods_receipt_obj.code,
                    trans_id=str(goods_receipt_obj.id)
                ):
                    sum_cost += stock_log_item.value
        return sum_cost

    @classmethod
    def parse_je_line_data(cls, ap_invoice_obj, transaction_key):
        """ Hàm parse dữ liệu dựa trên RULES CONFIG ('PURCHASE_INVOICE') """
        rules_list = AccountDeterminationSub.get_posting_lines(ap_invoice_obj.company_id, transaction_key)
        if not rules_list:
            logger.error(f"[JE] No Accounting Rules found for {transaction_key}")
            return None

        debit_rows_data = []
        credit_rows_data = []

        amount_source_data = {
            'COST': cls.get_cost_from_stock_log(ap_invoice_obj),  # Tổng giá trị hàng nhập (Clear 33881)
            'TAX': ap_invoice_obj.sum_tax_value,  # Tiền thuế GTGT
            'TOTAL': ap_invoice_obj.sum_after_tax_value  # Tổng tiền thanh toán (Công nợ 331)
        }
        # 2. Duyệt qua danh sách Rule (Không cần duyệt sản phẩm vì Invoice hạch toán tổng)
        for rule in rules_list:
            # A. Tìm tài khoản theo rule này
            account_mapped = rule.get_account_mapped(rule)
            # B. Xác định số tiền (Dựa trên amount_source)
            amount = rule.get_amount_base_on_amount_source(rule, **amount_source_data)
            # C. Tạo dòng JE Line Data
            line_data = {
                'account': account_mapped,
                'product_mapped': None,
                # Logic Partner: Chỉ dòng 'PAYABLE' (331) mới cần map NCC để theo dõi công nợ
                'business_partner': ap_invoice_obj.supplier_mapped if rule.role_key == 'PAYABLE' else None,
                'debit': amount if rule.side == 'DEBIT' else 0,  # 0: Debit
                'credit': amount if rule.side == 'CREDIT' else 0,  # 1: Credit
                'is_fc': False,
                'taxable_value': ap_invoice_obj.sum_after_tax_value if rule.role_key == 'TAX_IN' else 0,
                # Logic Reconciliation (Đối soát)
                # GRNI (33881): Cần đối soát với Goods Receipt (ap-gr)
                # PAYABLE (331): Cần đối soát với Payment (ap-cof)
                'use_for_recon': True if rule.role_key in ['GRNI', 'PAYABLE'] else False,
                'use_for_recon_type': 'ap-gr' if rule.role_key == 'GRNI' else ('ap-cof' if rule.role_key == 'PAYABLE' else '')
            }
            # D. Phân loại Nợ/Có
            if rule.side == 'DEBIT':
                debit_rows_data.append(line_data)
            else:
                credit_rows_data.append(line_data)
        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, ap_invoice_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        try:
            with transaction.atomic():
                debit_rows_data, credit_rows_data = cls.parse_je_line_data(ap_invoice_obj, 'PURCHASE_INVOICE')
                kwargs = {
                    'je_transaction_app_code': ap_invoice_obj.get_model_code(),
                    'je_transaction_id': str(ap_invoice_obj.id),
                    'je_transaction_data': {
                        'id': str(ap_invoice_obj.id),
                        'code': ap_invoice_obj.code,
                        'title': ap_invoice_obj.title,
                        'date_created': str(ap_invoice_obj.date_created),
                        'date_approved': str(ap_invoice_obj.date_approved),
                    },
                    'je_line_data': {
                        'debit_rows': debit_rows_data,
                        'credit_rows': credit_rows_data
                    }
                }
                JournalEntry.auto_create_journal_entry(ap_invoice_obj, **kwargs)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while creating Journal Entry: {err}')
            return None
