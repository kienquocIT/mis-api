import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import (
    JEPostingRule, JEDocData, JEDocumentType, JEGroupAssignment, JEGLAccountMapping
)
from apps.accounting.journalentry.models import JournalEntry
from apps.shared import DisperseModel

logger = logging.getLogger(__name__)


class JELogHandler:
    TRACKING_HIERARCHY_MAP = {
        'saledata.Product': ('product_product_types__product_type_id', 'saledata.ProductType'),
        'saledata.Account': ('account_account_types_mapped__account_type_id', 'saledata.AccountType'),
    }

    @classmethod
    def get_rules(cls, company_id, je_document_type):
        return JEPostingRule.objects.filter(
            company_id=company_id,
            je_document_type=je_document_type,
            is_delete=False
        ).select_related('fixed_account').order_by('priority') if je_document_type else []

    @classmethod
    def _resolve_lookup_account(cls, rule, data_item):
        """
        Logic tra cứu:
        1. Lấy thông tin từ Context JSON.
        2. Tìm Gán theo Đối tượng (Tracking) -> Leo thang (Hierarchy).
        3. Tìm Account mapped.
        """
        # Lấy dữ liệu từ JSON
        current_app = (data_item.context_data or {}).get('tracking_app')
        tracking_id = (data_item.context_data or {}).get('tracking_id')

        assignment = None

        if not current_app or not tracking_id:
            return None

        current_depth = 0
        candidate_ids = [tracking_id]
        while candidate_ids and current_depth < 2:  # 2 là max_depth
            # A. Tìm xem có gán nhóm cho đối tượng này không?
            assignment = JEGroupAssignment.objects.filter(
                company_id=rule.company_id,
                item_app=current_app,
                item_id__in=candidate_ids,
                is_delete=False
            ).first()

            if assignment:
                break  # tìm ra

            # B. Nếu không thấy, tra bản đồ để leo lên cấp cha (Lấy TẤT CẢ cha của TẤT CẢ con)
            parent_config = cls.TRACKING_HIERARCHY_MAP.get(current_app)
            if not parent_config or not parent_config[0]:
                break

            parent_related_name, parent_app_label = parent_config

            try:
                model_tracking = DisperseModel(app_model=current_app).get_model()
                if not model_tracking:
                    break

                parent_ids = model_tracking.objects.filter(
                    id__in=candidate_ids,
                    is_delete=False
                ).values_list(parent_related_name, flat=True)

                # Làm sạch list (bỏ None, bỏ trùng lặp)
                candidate_ids = list({uid for uid in parent_ids if uid})
                # Cập nhật app để vòng sau check bảng cha
                current_app = parent_app_label
                current_depth += 1
            except Exception as err:
                logger.error(msg=f"Error in tracking hierarchy: {err}")
                break

        # --- GIAI ĐOẠN 2: MAPPING RA TÀI KHOẢN ---
        if assignment:
            # Có Nhóm rồi -> Tra bảng Mapping với Role Key để lấy Tài khoản
            mapping = JEGLAccountMapping.objects.filter(
                company_id=rule.company_id,
                posting_group=assignment.posting_group,
                role_key=rule.role_key,  # VD: ASSET, COGS
                is_delete=False
            ).select_related('account').first()

            return mapping.account if mapping else None

        return None

    @classmethod
    def get_account(cls, rule_obj, data_item):
        # CASE 1: FIXED
        if rule_obj.account_source_type == 'FIXED':
            return rule_obj.fixed_account
        # CASE 2: LOOKUP
        if rule_obj.account_source_type == 'LOOKUP':
            return cls._resolve_lookup_account(rule_obj, data_item)
        return None

    @classmethod
    def create_single_je_line(cls, rule, value, account, data_item):
        """ Helper tạo dict dữ liệu cho 1 dòng JE """
        # 1. Xác định Loại đối soát (Recon Type), map từ Role Key sang Recon Type
        recon_map = {
            'GRNI': 'gr-ap',  # Nhập kho chưa hóa đơn (33881) <-> Hóa đơn mua
            'PAYABLE': 'ap-payment',  # Phải trả NCC (331) <-> Phiếu chi
            'RECEIVABLE': 'ar-payment',  # Phải thu KH (131) <-> Phiếu thu
            'DONI': 'deli-ar',  # Xuất kho chưa hóa đơn (13881) <-> Hóa đơn bán
        }
        recon_type = recon_map.get(rule.role_key, '')

        context_data = data_item.context_data or {}
        def get_tracking_id(app_code):
            tracking_app = context_data.get('tracking_app')
            tracking_id = context_data.get('tracking_id')
            return tracking_id if tracking_app == app_code else None

        return {
            'account': account,
            'product_mapped_id': get_tracking_id('saledata.Product'),
            'business_partner_id': get_tracking_id('saledata.Account'),
            'business_employee_id': get_tracking_id('hr.Employee'),
            'debit': value if rule.side == 'DEBIT' else 0,
            'credit': value if rule.side == 'CREDIT' else 0,
            'is_fc': False,
            'taxable_value': data_item.taxable_value if rule.role_key in ['TAX_IN', 'TAX_OUT'] else 0,
            # Logic Reconciliation (Đối soát)
            'use_for_recon': bool(recon_type),
            'use_for_recon_type': recon_type,
            'description': rule.description or ''
        }

    @classmethod
    def parse_je_line_data(cls, transaction_obj, je_document_type):
        """ Hàm parse dữ liệu từ JEDocData """
        transaction_key = je_document_type.code if je_document_type else None
        if not transaction_key:
            logger.error(msg='[JE] Can not found transaction_key.')
            return [], []

        # 1. Lấy Rules
        rules = cls.get_rules(transaction_obj.company_id, je_document_type)
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
                account = cls.get_account(rule, data_item)
                print(rule.account_source_type, data_item.context_data, ' --> ', account.acc_code if account else '')
                if not account:
                    continue
                # C. Tạo dòng
                line_data = cls.create_single_je_line(rule, value, account, data_item)
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
                    company_id=transaction_obj.company_id, app_code=app_code, is_auto_je=True, is_delete=False
                ).first()
                debit_rows_data, credit_rows_data = cls.parse_je_line_data(transaction_obj, je_document_type)
                if len(debit_rows_data) == 0 and len(credit_rows_data) == 0:
                    return False
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
        except Exception as err:
            logger.error(msg=f'[JE] Error while creating Journal Entry: {err}')
            return False
