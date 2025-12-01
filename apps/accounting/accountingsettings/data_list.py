APP_LIST = [
    # Sales
    [0, 'DO_SALE', 'delivery.orderdeliverysub'],
    [0, 'SALE_INVOICE', 'arinvoice.arinvoice'],
    [0, 'CASH_IN', 'financialcashflow.cashinflow'],
    # purchase
    [1, 'GRN_PURCHASE', 'inventory.goodsreceipt'],
    [1, 'PURCHASE_INVOICE', 'apinvoice.apinvoice'],
    [0, 'CASH_OUT', 'financialcashflow.cashoutflow'],
    # inventory
    # asset
]

POSTING_RULE_APP_LIST = [
    # -------------------------------------------------------------------------
    # 1. XUẤT KHO BÁN HÀNG (DO_SALE)
    # Đặc điểm: Toàn bộ là LINE (vì hạch toán theo từng mặt hàng)
    # Thứ tự: Giá vốn (Nợ->Có) rồi đến Doanh thu (Nợ->Có)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'DO_SALE',
        'posting_rule_list': [
            # Cụm 1: Giá vốn (Nợ 632 / Có 156)
            {
                'rule_level': 'LINE',
                'priority': 10,
                'role_key': 'COGS',
                'side': 'DEBIT',
                'amount_source': 'COST',
                'account_source_type': 'FIXED', 'fixed_account_code': '632',
                'description': 'Giá vốn hàng bán (632)',
            },
            {
                'rule_level': 'LINE',
                'priority': 20,
                'role_key': 'ASSET',
                'side': 'CREDIT',
                'amount_source': 'COST',
                'account_source_type': 'FIXED', 'fixed_account_code': '1561',
                'description': 'Giảm kho hàng hóa (1561)',
            },
            # Cụm 2: Doanh thu (Nợ 13881 / Có 511)
            {
                'rule_level': 'LINE',
                'priority': 30,
                'role_key': 'DONI',
                'side': 'DEBIT',
                'amount_source': 'SALES',
                'account_source_type': 'FIXED', 'fixed_account_code': '13881',
                'description': 'Phải thu tạm tính (13881)',
            },
            {
                'rule_level': 'LINE',
                'priority': 40,
                'role_key': 'REVENUE',
                'side': 'CREDIT',
                'amount_source': 'SALES',
                'account_source_type': 'FIXED', 'fixed_account_code': '5111',
                'description': 'Doanh thu bán hàng (5111)',
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 2. HÓA ĐƠN BÁN HÀNG (SALES_INVOICE)
    # Quy tắc: Nợ (Header) -> Có (Header: Thuế) -> Có (Line: Doanh thu)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'SALES_INVOICE',
        'posting_rule_list': [
            # 1. Nợ: Phải thu (HEADER) - Tổng tiền
            {
                'rule_level': 'HEADER',
                'priority': 10,
                'role_key': 'RECEIVABLE',
                'side': 'DEBIT',
                'amount_source': 'TOTAL',
                'account_source_type': 'FIXED', 'fixed_account_code': '131',
                'description': 'Phải thu khách hàng (131)',
            },
            # 2. Có: Thuế (HEADER) - Ưu tiên Header trước Line
            {
                'rule_level': 'HEADER',
                'priority': 20,
                'role_key': 'TAX_OUT',
                'side': 'CREDIT',
                'amount_source': 'TAX',
                'account_source_type': 'FIXED', 'fixed_account_code': '33311',
                'description': 'Thuế GTGT đầu ra (33311)',
            },
            # 3. Có: Đối trừ Doanh thu (LINE) - Chi tiết từng dòng
            {
                'rule_level': 'LINE',
                'priority': 30,
                'role_key': 'DONI',
                'side': 'CREDIT',
                'amount_source': 'SALES',
                'account_source_type': 'FIXED', 'fixed_account_code': '13881',
                'description': 'Đối trừ hàng đã xuất (13881)',
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 3. NHẬP KHO MUA HÀNG (GRN_PURCHASE)
    # Đặc điểm: Toàn bộ là LINE (chi tiết từng mặt hàng nhập)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'GRN_PURCHASE',
        'posting_rule_list': [
            {
                'rule_level': 'LINE',
                'priority': 10,
                'role_key': 'ASSET',
                'side': 'DEBIT',
                'amount_source': 'COST',
                'account_source_type': 'FIXED', 'fixed_account_code': '1561',
                'description': 'Nhập kho hàng hóa (1561)',
            },
            {
                'rule_level': 'LINE',
                'priority': 20,
                'role_key': 'GRNI',
                'side': 'CREDIT',
                'amount_source': 'COST',
                'account_source_type': 'FIXED', 'fixed_account_code': '33881',
                'description': 'Phải trả tạm tính (33881)',
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 4. HÓA ĐƠN MUA HÀNG (PURCHASE_INVOICE)
    # Quy tắc: Nợ (Header: Thuế) -> Nợ (Line: Hàng) -> Có (Header: Công nợ)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'PURCHASE_INVOICE',
        'posting_rule_list': [
            # 1. Nợ: Thuế (HEADER) - Ưu tiên Header trước
            {
                'rule_level': 'HEADER',
                'priority': 10,
                'role_key': 'TAX_IN',
                'side': 'DEBIT',
                'amount_source': 'TAX',
                'account_source_type': 'FIXED', 'fixed_account_code': '1331',
                'description': 'Thuế GTGT đầu vào (1331)',
            },
            # 2. Nợ: Đối trừ hàng về (LINE)
            {
                'rule_level': 'HEADER',
                'priority': 20,
                'role_key': 'GRNI',
                'side': 'DEBIT',
                'amount_source': 'COST',
                'account_source_type': 'FIXED', 'fixed_account_code': '33881',
                'description': 'Đối trừ hàng về chưa hóa đơn (33881)',
            },
            # 3. Có: Phải trả (HEADER)
            {
                'rule_level': 'HEADER',
                'priority': 30,
                'role_key': 'PAYABLE',
                'side': 'CREDIT',
                'amount_source': 'TOTAL',
                'account_source_type': 'FIXED', 'fixed_account_code': '331',
                'description': 'Phải trả người bán (331)',
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 5. PHIẾU CHI (CASH_OUT)
    # Đặc điểm: Toàn bộ là HEADER (vì không chi tiết theo dòng hàng)
    # Quy tắc: Nợ trước -> Có sau
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'CASH_OUT',
        'posting_rule_list': [
            # 1. Nợ: Giảm phải trả (HEADER)
            {
                'rule_level': 'HEADER',
                'priority': 10,
                'role_key': 'PAYABLE',
                'side': 'DEBIT',
                'amount_source': 'TOTAL',
                'account_source_type': 'FIXED', 'fixed_account_code': '331',
                'description': 'Giảm nợ phải trả NCC (331)',
            },
            # 2. Có: Tiền mặt (HEADER)
            {
                'rule_level': 'HEADER',
                'priority': 20,
                'role_key': 'CASH',
                'side': 'CREDIT',
                'amount_source': 'CASH',
                'account_source_type': 'FIXED', 'fixed_account_code': '1111',
                'description': 'Chi tiền mặt (1111)',
            },
            # 3. Có: Tiền gửi (HEADER)
            {
                'rule_level': 'HEADER',
                'priority': 30,
                'role_key': 'BANK',
                'side': 'CREDIT',
                'amount_source': 'BANK',
                'account_source_type': 'FIXED', 'fixed_account_code': '1121',
                'description': 'Chi tiền gửi ngân hàng (1121)',
            },
        ]
    },
]
