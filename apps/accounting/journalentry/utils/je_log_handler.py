import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import JEPostingRule, JEDocData, JEDocumentType
from apps.accounting.journalentry.models import JournalEntry


logger = logging.getLogger(__name__)


class JELogHandler:
    @classmethod
    def get_rules(cls, company_id, transaction_key):
        je_document_type_obj = JEDocumentType.objects.filter(code=transaction_key, is_auto_je=True).first()
        if je_document_type_obj:
            return JEPostingRule.objects.filter(
                company_id=company_id,
                je_document_type=je_document_type_obj,
            ).select_related('fixed_account').order_by('priority')
        return []

    @classmethod
    def get_account(cls, rule_obj):
        if rule_obj.account_source_type == 'FIXED':
            return rule_obj.fixed_account
        # Nếu sau này có LOOKUP/DYNAMIC thì code thêm ở đây
        return None

    @classmethod
    def create_single_je_line(cls, rule, value, taxable_value, account, data_item):
        """ Helper tạo dict dữ liệu cho 1 dòng JE """
        # 1. Xác định Loại đối soát (Recon Type), map từ Role Key sang Recon Type
        recon_map = {
            'GRNI': 'gr-ap',  # Nhập kho chưa hóa đơn (33881) <-> Hóa đơn mua
            'PAYABLE': 'ap-payment',  # Phải trả NCC (331) <-> Phiếu chi
            'RECEIVABLE': 'ar-payment',  # Phải thu KH (131) <-> Phiếu thu
            'DONI': 'deli-ar',  # Xuất kho chưa hóa đơn (13881) <-> Hóa đơn bán
        }
        recon_type = recon_map.get(rule.role_key, '')

        return {
            'account': account,
            'product_mapped_id': data_item.tracking_id if data_item.tracking_by == 'product' else None,
            'business_partner_id': data_item.tracking_id if data_item.tracking_by == 'account' else None,
            'business_employee_id': data_item.tracking_id if data_item.tracking_by == 'employee' else None,
            'debit': value if rule.side == 'DEBIT' else 0,
            'credit': value if rule.side == 'CREDIT' else 0,
            'is_fc': False,
            'taxable_value': taxable_value if rule.role_key in ['TAX_IN', 'TAX_OUT'] else 0,
            # Logic Reconciliation (Đối soát)
            'use_for_recon': bool(recon_type),
            'use_for_recon_type': recon_type,
            'description': rule.description or ''
        }

    @classmethod
    def parse_je_line_data(cls, transaction_obj, transaction_key):
        """ Hàm parse dữ liệu từ JEDocData """
        # 1. Lấy Rules
        rules = cls.get_rules(transaction_obj.company_id, transaction_key)
        if not rules:
            logger.error("[JE] No Rules found for %s", transaction_key)
            return [], []

        # 2. Lấy Data (Dữ liệu thô từ bảng trung gian)
        doc_data_list = list(JEDocData.get_amount_source_doc_data(transaction_obj.id))

        if not doc_data_list:
            logger.error("[JE] No JEDocData found for Doc ID %s. Please push data first.", transaction_obj.id)
            return [], []

        debit_rows_data = []
        credit_rows_data = []

        # 3. ENGINE MATCHING: Duyệt qua từng Rule để tìm Data phù hợp
        for rule in rules:
            # LỌC DỮ LIỆU: Tìm các dòng trong JEDocData khớp với Rule nà
            matched_data = [
                d for d in doc_data_list
                if d.rule_level == rule.rule_level and d.amount_source == rule.amount_source
            ]
            # Với mỗi mẩu dữ liệu tìm được -> Tạo 1 dòng hạch toán
            for data_item in matched_data:
                # A. Lấy giá trị tiền (Đã có sẵn trong JEDocData)
                value = float(data_item.value)
                if value <= 0:
                    continue
                # B. Tìm tài khoản
                account = cls.get_account(rule)
                if not account:
                    continue
                # C. Tạo dòng
                line_data = cls.create_single_je_line(rule, value, data_item.taxable_value, account, data_item,)
                # D. Phân loại Nợ/Có
                if rule.side == 'DEBIT':
                    debit_rows_data.append(line_data)
                else:
                    credit_rows_data.append(line_data)

        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, transaction_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        try:
            with transaction.atomic():
                app_code = transaction_obj.get_model_code()
                je_document_type = JEDocumentType.objects.filter(
                    company_id=transaction_obj.company_id, app_code=app_code
                ).first()
                transaction_key = je_document_type.code if je_document_type else None
                if transaction_key:
                    debit_rows_data, credit_rows_data = cls.parse_je_line_data(transaction_obj, transaction_key)
                    kwargs = {
                        'je_transaction_app_code': app_code,
                        'je_transaction_id': str(transaction_obj.id),
                        'je_transaction_data': {
                            'id': str(transaction_obj.id),
                            'code': transaction_obj.code,
                            'title': transaction_obj.title,
                            'date_created': str(transaction_obj.date_created),
                            'date_approved': str(transaction_obj.date_approved),
                        },
                        'je_line_data': {
                            'debit_rows': debit_rows_data,
                            'credit_rows': credit_rows_data
                        }
                    }
                    JournalEntry.auto_create_journal_entry(transaction_obj, **kwargs)
                    return True
                logger.error(msg='[JE] Can not found transaction_key.')
        except Exception as err:
            logger.error(msg=f'[JE] Error while creating Journal Entry: {err}')
            return None
