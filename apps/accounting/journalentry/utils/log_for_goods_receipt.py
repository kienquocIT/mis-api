import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import AccountDetermination, AccountDeterminationSub
from apps.accounting.journalentry.models import JournalEntry
from apps.sales.report.models import ReportStockLog


logger = logging.getLogger(__name__)


class JEForGoodsReceiptHandler:
    @classmethod
    def parse_je_line_data_old(cls, gr_obj):
        debit_rows_data = []
        credit_rows_data = []
        sum_cost = 0
        for gr_prd_obj in gr_obj.goods_receipt_product_goods_receipt.all():
            for gr_wh_obj in gr_prd_obj.goods_receipt_warehouse_gr_product.all():
                # lấy cost hiện tại của sp
                stock_log_item = ReportStockLog.objects.filter(
                    product=gr_prd_obj.product,
                    trans_code=gr_obj.code,
                    trans_id=str(gr_obj.id)
                ).first()
                cost = stock_log_item.value if stock_log_item else 0
                sum_cost += cost
                account_list = gr_prd_obj.product.get_product_account_deter_sub_data(
                    account_deter_foreign_title='Inventory account',
                    warehouse_id=gr_wh_obj.warehouse_id
                )
                if len(account_list) == 1:
                    debit_rows_data.append({
                        # (-) hàng hóa (mđ: 156)
                        'account': account_list[0],
                        'product_mapped': gr_prd_obj.product,
                        'business_partner': None,
                        'debit': cost,
                        'credit': 0,
                        'is_fc': False,
                        'taxable_value': 0,
                    })

        account_list = AccountDetermination.get_sub_items_data(
            tenant_id=gr_obj.tenant_id,
            company_id=gr_obj.company_id,
            foreign_title='Customer overpayment'
        )
        if len(account_list) == 1:
            credit_rows_data.append({
                # (+) nhập hàng chưa nhập hóa đơn (mđ: 33881)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': None,
                'debit': 0,
                'credit': sum_cost,
                'is_fc': False,
                'taxable_value': 0,
                'use_for_recon': True,
                'use_for_recon_type': 'gr-ap'
            })
        return debit_rows_data, credit_rows_data

    @classmethod
    def get_cost_from_stock_log(cls, transaction_obj, product):
        sum_value = 0
        for stock_log_item in ReportStockLog.objects.filter(
            product=product,
            trans_code=transaction_obj.code,
            trans_id=str(transaction_obj.id)
        ):
            sum_value += stock_log_item.value
        return sum_value

    @classmethod
    def parse_je_line_data(cls, gr_obj, transaction_key_list):
        """
        Hàm parse dữ liệu dựa trên RULES CONFIG
        """
        rules_list = AccountDeterminationSub.get_posting_lines(gr_obj.company_id, transaction_key_list)
        if not rules_list:
            logger.error(f"[JE] No Accounting Rules found for {transaction_key_list}")
            return None

        debit_rows_data = []
        credit_rows_data = []

        # 1. Duyệt qua từng dòng sản phẩm trong phiếu nhập
        for gr_prd_obj in gr_obj.goods_receipt_product_goods_receipt.all():
            for gr_wh_obj in gr_prd_obj.goods_receipt_warehouse_gr_product.all():
                # 2. Trong GD này chỉ cần cost. Tính Cost cho dòng này
                amount_source_data = {
                    'COST': cls.get_cost_from_stock_log(gr_obj, gr_prd_obj.product),
                }
                # 3. Áp dụng danh sách Rule cho dòng sản phẩm này
                for rule in rules_list:
                    # A. Tìm tài khoản theo rule này
                    account_mapped = rule.get_account_mapped(rule)
                    # B. Xác định số tiền (Dựa trên amount_source)
                    amount = rule.get_amount_base_on_amount_source(rule, **amount_source_data)
                    # C. Tạo dòng JE Line Data
                    line_data = {
                        'account': account_mapped,
                        'product_mapped': gr_prd_obj.product,
                        # Chỉ map product cho dòng Kho
                        'business_partner': None,
                        'debit': amount if rule.side == 'DEBIT' else 0,  # 0: Debit
                        'credit': amount if rule.side =='CREDIT' else 0,  # 1: Credit
                        'is_fc': False,
                        'taxable_value': 0,
                        # Logic Reconciliation (cho dòng 33881)
                        'use_for_recon': True if rule.role_key == 'GRNI' else False,
                        'use_for_recon_type': 'gr-ap' if rule.role_key == 'GRNI' else ''
                    }
                    # D. Phân loại Nợ/Có
                    if rule.side == 'DEBIT':
                        debit_rows_data.append(line_data)
                    else:
                        credit_rows_data.append(line_data)
        return debit_rows_data, credit_rows_data

    @classmethod
    def _create_single_je_line(cls, rule, amount, account, product=None, partner=None, desc_prefix=''):
        """ Helper tạo dict dữ liệu cho 1 dòng JE """
        return {
            'account': account,
            'product_mapped': product,  # Chỉ có giá trị nếu là Rule Line
            'business_partner': partner,  # Thường dùng cho Rule Header (Công nợ)
            'debit': amount if rule.side == 'DEBIT' else 0,
            'credit': amount if rule.side == 'CREDIT' else 0,
            'is_fc': False,
            'taxable_value': 0,
            # Logic Reconciliation
            'use_for_recon': True if rule.role_key in ['GRNI', 'PAYABLE', 'RECEIVABLE'] else False,
            'use_for_recon_type': 'gr-ap' if rule.role_key == 'GRNI' else '',  # Cần logic map type chuẩn hơn ở đây
            'description': f"{desc_prefix} {rule.description or ''}"
        }

    @classmethod
    def parse_je_line_data_sample(cls, transaction_obj, transaction_key_list):
        """
        Hàm parse dữ liệu Dynamic theo Rule Level (HEADER vs LINE)
        """
        # 1. Lấy tất cả Rules
        all_rules = AccountDeterminationSub.get_posting_lines(
            transaction_obj.company_id,
            transaction_key_list
        )

        if not all_rules:
            logger.error(f"[JE] No Rules found for {transaction_key_list}")
            return None, None

        # 2. Tách nhóm Rule
        header_rules = [rule for rule in all_rules if rule.rule_level == 'HEADER']
        line_rules = [rule for rule in all_rules if rule.rule_level == 'LINE']

        debit_rows_data = []
        credit_rows_data = []

        # ====================================================
        # PHẦN 1: XỬ LÝ HEADER RULES (Chạy 1 lần cho cả phiếu)
        # ====================================================
        if header_rules:
            # Chuẩn bị dữ liệu nguồn từ Header phiếu
            header_source_data = {
                'TOTAL': getattr(transaction_obj, 'total_value', 0),
                'CASH': getattr(transaction_obj, 'cash_value', 0),
                'BANK': getattr(transaction_obj, 'bank_value', 0),
                'TAX': getattr(transaction_obj, 'total_tax_amount', 0),
            }

            for rule in header_rules:
                # A. Tìm tài khoản
                account_mapped = rule.get_account_mapped(rule)
                if not account_mapped: continue

                # B. Lấy tiền
                amount = rule.get_amount_base_on_amount_source(rule, **header_source_data)
                if amount <= 0: continue

                # C. Tạo dòng
                partner = getattr(transaction_obj, 'supplier_mapped', getattr(transaction_obj, 'customer_mapped', None))

                line_data = cls._create_single_je_line(
                    rule, amount, account_mapped,
                    product=None,
                    partner=partner,
                    desc_prefix=f"[{transaction_obj.code}]"
                )

                # D. Append
                if rule.side == 'DEBIT':
                    debit_rows_data.append(line_data)
                else:
                    credit_rows_data.append(line_data)

        # ====================================================
        # PHẦN 2: XỬ LÝ LINE RULES (Chạy lặp qua từng dòng hàng)
        # ====================================================
        if line_rules:
            # Duyệt qua các dòng chi tiết của phiếu
            for gr_prd_obj in transaction_obj.goods_receipt_product_goods_receipt.all():
                for gr_wh_obj in gr_prd_obj.goods_receipt_warehouse_gr_product.all():
                    # 1. Chuẩn bị dữ liệu nguồn từ Dòng hàng (Line Item)
                    line_source_data = {
                        'COST': cls.get_cost_from_stock_log(transaction_obj, gr_prd_obj.product),
                        # 'SALES': gr_prd_obj.subtotal_amount, # Nếu là phiếu xuất
                        # 'DISCOUNT': gr_prd_obj.discount_amount
                    }
                    for rule in line_rules:
                        # A. Tìm tài khoản
                        account_mapped = rule.get_account_mapped(rule)
                        if not account_mapped: continue
                        # B. Lấy tiền
                        amount = rule.get_amount_base_on_amount_source(rule, **line_source_data)
                        if amount <= 0: continue
                        # C. Tạo dòng
                        # Line thường map Product, không cần map Partner (trừ khi cần tracking chi tiết)
                        line_data = cls._create_single_je_line(
                            rule, amount, account_mapped,
                            product=gr_prd_obj.product,
                            partner=None,
                            desc_prefix=f"[{gr_prd_obj.product.code}]"
                        )
                        # D. Append
                        if rule.side == 'DEBIT':
                            debit_rows_data.append(line_data)
                        else:
                            credit_rows_data.append(line_data)

        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, gr_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        try:
            with transaction.atomic():
                debit_rows_data, credit_rows_data = cls.parse_je_line_data(gr_obj, ['GRN_PURCHASE'])
                kwargs = {
                    'je_transaction_app_code': gr_obj.get_model_code(),
                    'je_transaction_id': str(gr_obj.id),
                    'je_transaction_data': {
                        'id': str(gr_obj.id),
                        'code': gr_obj.code,
                        'title': gr_obj.title,
                        'date_created': str(gr_obj.date_created),
                        'date_approved': str(gr_obj.date_approved),
                    },
                    'je_line_data': {
                        'debit_rows': debit_rows_data,
                        'credit_rows': credit_rows_data
                    }
                }
                JournalEntry.auto_create_journal_entry(gr_obj, **kwargs)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while creating Journal Entry: {err}')
            return None
