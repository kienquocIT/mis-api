# =============================================================================
# 1. DOCUMENT TYPE LIST (Loại chứng từ)
# Format: [ModuleID, TransactionKey, DjangoAppModel]
# =============================================================================
DOCUMENT_TYPE_LIST = [
    # --- BÁN HÀNG ---
    [0, 'DO_SALE', 'delivery.orderdeliverysub', ['COST', 'SALES']],
    [
        0,
        'SALES_INVOICE',
        'arinvoice.arinvoice',
        ['TOTAL', 'SALES', 'TAX', 'DISCOUNT', 'SURCHARGE', 'ROUNDING', 'EXPORT_TAX']
    ],
    [0, 'CASH_IN', 'financialcashflow.cashinflow', ['TOTAL', 'CASH', 'BANK']],
    # --- MUA HÀNG ---
    [1, 'GRN_PURCHASE', 'inventory.goodsreceipt', ['COST']],
    [
        1,
        'PURCHASE_INVOICE',
        'apinvoice.apinvoice',
        ['TOTAL', 'COST', 'TAX', 'DISCOUNT', 'SURCHARGE', 'ROUNDING', 'IMPORT_TAX']
    ],
    [1, 'CASH_OUT', 'financialcashflow.cashoutflow', ['TOTAL', 'CASH', 'BANK']],
]

ALLOWED_AMOUNT_SOURCES_MAP = {
    row[2]: row[3] for row in DOCUMENT_TYPE_LIST
}

POSTING_GROUP_TYPE_MAP = {
    'ITEM_GROUP': 'saledata.producttype',
    'PARTNER_GROUP': 'saledata.accounttype',
}

# =============================================================================
# 2. POSTING GROUP LIST (Nhóm định khoản)
# Dùng để tạo Master Data cho Dropdown chọn nhóm
# =============================================================================
POSTING_GROUP_LIST = [
    # --- NHÓM SẢN PHẨM (ITEM_GROUP) ---
    {'code': 'GOODS', 'title': 'Hàng hóa', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'FINISHED_GOODS', 'title': 'Thành phẩm', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'SEMI_FINISHED', 'title': 'Bán thành phẩm', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'MATERIAL', 'title': 'Nguyên vật liệu', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'TOOL', 'title': 'Công cụ - Dụng cụ', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'SERVICE', 'title': 'Dịch vụ', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'CONSIGNMENT', 'title': 'Hàng gửi đi bán', 'posting_group_type': 'ITEM_GROUP'},

    # --- NHÓM ĐỐI TÁC (PARTNER_GROUP) ---
    {'code': 'CUSTOMER', 'title': 'Khách hàng', 'posting_group_type': 'PARTNER_GROUP'},
    {'code': 'SUPPLIER', 'title': 'Nhà cung cấp', 'posting_group_type': 'PARTNER_GROUP'},
    {'code': 'PARTNER_OTHER', 'title': 'Đối tác khác', 'posting_group_type': 'PARTNER_GROUP'},
]

# =============================================================================
# 3. GL MAPPING TEMPLATE (Bảng ánh xạ tài khoản mẫu)
# Dùng để map tài khoản cho từng nhóm khi khởi tạo
# =============================================================================
GL_MAPPING_TEMPLATE = {
    # --- ITEM GROUPS ---
    'GOODS': {
        'ASSET': '1561', 'COGS': '632', 'REVENUE': '5111', 'DONI': '13881', 'GRNI': '33881'
    },
    'FINISHED_GOODS': {
        'ASSET': '155', 'COGS': '632', 'REVENUE': '5112', 'DONI': '13881', 'GRNI': '33881'
    },
    'SEMI_FINISHED': {
        'ASSET': '154', 'COGS': '632', 'REVENUE': '5112', 'DONI': '13881', 'GRNI': '33881'
    },
    'MATERIAL': {
        'ASSET': '152', 'COGS': '632', 'REVENUE': '5111', 'DONI': '13881', 'GRNI': '33881'
    },
    'TOOL': {
        'ASSET': '153', 'COGS': '632', 'REVENUE': '5111', 'DONI': '13881', 'GRNI': '33881'
    },
    'SERVICE': {
        'ASSET': None, 'COGS': '632', 'REVENUE': '5113', 'DONI': '13881', 'GRNI': '33881'
    },
    'CONSIGNMENT': {
        'ASSET': '157', 'COGS': '632', 'REVENUE': '5111', 'DONI': '13881', 'GRNI': '33881'
    },

    # --- PARTNER GROUPS ---
    'CUSTOMER': {
        'RECEIVABLE': '131', 'TAX_OUT': '33311', 'CASH': '1111', 'BANK': '1121'
    },
    'SUPPLIER': {
        'PAYABLE': '331', 'TAX_IN': '1331', 'CASH': '1111', 'BANK': '1121'
    },
    'PARTNER_OTHER': {
        'RECEIVABLE': '1388', 'PAYABLE': '3388', 'TAX_OUT': '33311', 'CASH': '1111', 'BANK': '1121'
    },
}

# =============================================================================
# 4. POSTING RULE LIST (Quy tắc hạch toán)
# Cấu hình Nợ/Có cho từng loại chứng từ
# =============================================================================
POSTING_RULE_LIST = [
    # -------------------------------------------------------------------------
    # 1. XUẤT KHO BÁN HÀNG (DO_SALE)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'DO_SALE',
        'posting_rule_list': [
            # Giá vốn (Nợ) -> LOOKUP (Để phân biệt 632 hàng hóa/thành phẩm/dịch vụ)
            {
                'rule_level': 'LINE', 'priority': 10, 'role_key': 'COGS', 
                'side': 'DEBIT', 'amount_source': 'COST',
                'account_source_type': 'LOOKUP', # <--- LOOKUP
                'description': 'Giá vốn hàng bán',
            },
            # Giảm kho (Có) -> LOOKUP (Để phân biệt 1561/155)
            {
                'rule_level': 'LINE', 'priority': 20, 'role_key': 'ASSET', 
                'side': 'CREDIT', 'amount_source': 'COST',
                'account_source_type': 'LOOKUP', # <--- LOOKUP
                'description': 'Giảm kho hàng hóa',
            },
            # Phải thu tạm (Nợ) -> FIXED (Luôn treo 13881)
            {
                'rule_level': 'LINE', 'priority': 30, 'role_key': 'DONI',
                'side': 'DEBIT', 'amount_source': 'SALES',
                'account_source_type': 'FIXED', 'fixed_account_code': '13881',
                'description': 'Phải thu tạm tính (13881)',
            },
            # Doanh thu (Có) -> LOOKUP (Để phân biệt 5111/5112/5113)
            {
                'rule_level': 'LINE', 'priority': 40, 'role_key': 'REVENUE',
                'side': 'CREDIT', 'amount_source': 'SALES',
                'account_source_type': 'LOOKUP', # <--- LOOKUP
                'description': 'Doanh thu bán hàng',
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 2. HÓA ĐƠN BÁN HÀNG (SALES_INVOICE)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'SALES_INVOICE',
        'posting_rule_list': [
            # Phải thu (Nợ) -> FIXED (131) - Hoặc LOOKUP nếu muốn tách 1311/1312
            {
                'rule_level': 'HEADER', 'priority': 10, 'role_key': 'RECEIVABLE',
                'side': 'DEBIT', 'amount_source': 'TOTAL',
                'account_source_type': 'FIXED', 'fixed_account_code': '131',
                'description': 'Phải thu khách hàng (131)',
            },
            # Thuế đầu ra (Có) -> FIXED (33311)
            {
                'rule_level': 'HEADER', 'priority': 20, 'role_key': 'TAX_OUT',
                'side': 'CREDIT', 'amount_source': 'TAX',
                'account_source_type': 'FIXED', 'fixed_account_code': '33311',
                'description': 'Thuế GTGT đầu ra (33311)',
            },
            # Đối trừ Doanh thu tạm (Có) -> FIXED (13881)
            {
                'rule_level': 'LINE', 'priority': 30, 'role_key': 'DONI',
                'side': 'CREDIT', 'amount_source': 'SALES',
                'account_source_type': 'FIXED', 'fixed_account_code': '13881',
                'description': 'Đối trừ hàng đã xuất (13881)',
            },
            # Chiết khấu (Nợ) -> FIXED (521)
            {
                'rule_level': 'LINE', 'priority': 40, 'role_key': 'SALES_DEDUCTION',
                'side': 'DEBIT', 'amount_source': 'DISCOUNT',
                'account_source_type': 'FIXED', 'fixed_account_code': '5211',
                'description': 'Chiết khấu thương mại theo dòng',
            },
            # Thuế Xuất khẩu (Có) -> FIXED (3333)
            # {
            #     'rule_level': 'HEADER', 'priority': 50, 'role_key': 'TAX_EXPORT',
            #     'side': 'CREDIT', 'amount_source': 'EXPORT_TAX',
            #     'account_source_type': 'FIXED', 'fixed_account_code': '3333',
            #     'description': 'Thuế Xuất khẩu (3333)',
            # },
        ]
    },

    # -------------------------------------------------------------------------
    # 3. NHẬP KHO MUA HÀNG (GRN_PURCHASE)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'GRN_PURCHASE',
        'posting_rule_list': [
            # Tăng kho (Nợ) -> LOOKUP (1561/152...)
            {
                'rule_level': 'LINE', 'priority': 10, 'role_key': 'ASSET',
                'side': 'DEBIT', 'amount_source': 'COST',
                'account_source_type': 'LOOKUP', # <--- LOOKUP
                'description': 'Nhập kho hàng hóa',
            },
            # Phải trả tạm (Có) -> FIXED (33881)
            {
                'rule_level': 'LINE', 'priority': 20, 'role_key': 'GRNI',
                'side': 'CREDIT', 'amount_source': 'COST',
                'account_source_type': 'FIXED', 'fixed_account_code': '33881',
                'description': 'Phải trả tạm tính (33881)',
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 4. HÓA ĐƠN MUA HÀNG (PURCHASE_INVOICE)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'PURCHASE_INVOICE',
        'posting_rule_list': [
            # Phải trả (Có) -> FIXED (331)
            {
                'rule_level': 'HEADER', 'priority': 10, 'role_key': 'PAYABLE',
                'side': 'CREDIT', 'amount_source': 'TOTAL',
                'account_source_type': 'FIXED', 'fixed_account_code': '331',
                'description': 'Phải trả người bán',
            },
            # Thuế đầu vào (Nợ) -> FIXED (1331)
            {
                'rule_level': 'HEADER', 'priority': 20, 'role_key': 'TAX_IN',
                'side': 'DEBIT', 'amount_source': 'TAX',
                'account_source_type': 'FIXED', 'fixed_account_code': '1331',
                'description': 'Thuế GTGT đầu vào',
            },
            # Đối trừ nợ tạm (Nợ) -> FIXED (33881)
            {
                'rule_level': 'LINE', 'priority': 30, 'role_key': 'GRNI',
                'side': 'DEBIT', 'amount_source': 'COST',
                'account_source_type': 'FIXED', 'fixed_account_code': '33881',
                'description': 'Đối trừ hàng về chưa hóa đơn',
            },
            # Thuế Nhập khẩu (Có) -> FIXED (3333 - Phải nộp NN)
            # {
            #     'rule_level': 'HEADER', 'priority': 40, 'role_key': 'TAX_IMPORT',
            #     'side': 'CREDIT', 'amount_source': 'IMPORT_TAX',
            #     'account_source_type': 'FIXED', 'fixed_account_code': '3333',
            #     'description': 'Thuế Nhập khẩu phải nộp (3333)',
            # },
            # Thuế Nhập khẩu (Nợ) -> LOOKUP (ASSET - Cộng vào giá trị Kho)
            # {
            #     'rule_level': 'HEADER', 'priority': 41, 'role_key': 'ASSET',
            #     'side': 'DEBIT', 'amount_source': 'IMPORT_TAX',
            #     'account_source_type': 'LOOKUP', # Tự tìm theo nhóm SP để nợ 156/152/211
            #     'description': 'Thuế Nhập khẩu (Cộng vào kho)',
            # },
            # Phụ phí mua hàng (Nợ) -> LOOKUP (ASSET - Cộng vào kho) hoặc FIXED 1562
            # {
            #     'rule_level': 'HEADER', 'priority': 50, 'role_key': 'ASSET',
            #     'side': 'DEBIT', 'amount_source': 'SURCHARGE',
            #     'account_source_type': 'LOOKUP', # Hoặc chọn FIXED 1562 nếu muốn
            #     'description': 'Phụ phí mua hàng',
            # },
            # Làm tròn (Nợ) -> FIXED (811 - Chi phí khác)
            # {
            #     'rule_level': 'HEADER', 'priority': 60, 'role_key': 'OTHER_EXPENSE',
            #     'side': 'DEBIT', 'amount_source': 'ROUNDING',
            #     'account_source_type': 'FIXED', 'fixed_account_code': '811',
            #     'description': 'Chênh lệch làm tròn',
            # },
        ]
    },

    # -------------------------------------------------------------------------
    # 5. PHIẾU CHI (CASH_OUT)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'CASH_OUT',
        'posting_rule_list': [
            # Giảm phải trả (Nợ) -> FIXED (331)
            {
                'rule_level': 'HEADER', 'priority': 10, 'role_key': 'PAYABLE',
                'side': 'DEBIT', 'amount_source': 'TOTAL',
                'account_source_type': 'FIXED', 'fixed_account_code': '331',
                'description': 'Giảm nợ phải trả NCC',
            },
            # Tiền mặt (Có) -> FIXED (1111)
            {
                'rule_level': 'HEADER', 'priority': 20, 'role_key': 'CASH',
                'side': 'CREDIT', 'amount_source': 'CASH',
                'account_source_type': 'FIXED', 'fixed_account_code': '1111',
                'description': 'Chi tiền mặt',
            },
            # Tiền gửi (Có) -> FIXED (1121)
            {
                'rule_level': 'HEADER', 'priority': 30, 'role_key': 'BANK',
                'side': 'CREDIT', 'amount_source': 'BANK',
                'account_source_type': 'FIXED', 'fixed_account_code': '1121',
                'description': 'Chi tiền gửi ngân hàng',
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 6. PHIẾU THU (CASH_IN)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'CASH_IN',
        'posting_rule_list': [
            # Tăng Tiền mặt (Nợ) -> FIXED (1111)
            {
                'rule_level': 'HEADER', 'priority': 10, 'role_key': 'CASH',
                'side': 'DEBIT', 'amount_source': 'CASH',
                'account_source_type': 'FIXED', 'fixed_account_code': '1111',
                'description': 'Thu tiền mặt',
            },
            # Tăng Tiền gửi (Nợ) -> FIXED (1121)
            {
                'rule_level': 'HEADER', 'priority': 20, 'role_key': 'BANK',
                'side': 'DEBIT', 'amount_source': 'BANK',
                'account_source_type': 'FIXED', 'fixed_account_code': '1121',
                'description': 'Thu tiền gửi ngân hàng',
            },
            # Giảm Phải thu (Có) -> FIXED (131)
            {
                'rule_level': 'HEADER', 'priority': 30, 'role_key': 'RECEIVABLE',
                'side': 'CREDIT', 'amount_source': 'TOTAL',
                'account_source_type': 'FIXED', 'fixed_account_code': '131',
                'description': 'Thu tiền khách hàng',
            },
        ]
    },
]
