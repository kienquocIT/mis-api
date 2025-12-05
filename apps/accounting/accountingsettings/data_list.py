DOCUMENT_TYPE_LIST = [
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

POSTING_RULE_LIST = [
    # =========================================================================
    # NHÓM 1: BÁN HÀNG (SALES CYCLE)
    # Flow: DO_SALE (Treo 13881) -> SALE_INVOICE (Clear 13881, Ghi 131)
    # =========================================================================

    # 1.1. XUẤT KHO BÁN HÀNG (DO_SALE)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'DO_SALE',
        'posting_rule_list': [
            # --- Cụm 1: Giá vốn (Nợ 632 / Có 156) ---
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
            # --- Cụm 2: Doanh thu tạm (Nợ 13881 / Có 511) ---
            {
                'rule_level': 'LINE',
                'priority': 30,
                'role_key': 'DONI',  # Delivery Order Not Invoiced
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

    # 1.2. HÓA ĐƠN BÁN HÀNG (SALE_INVOICE)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'SALE_INVOICE',
        'posting_rule_list': [
            # 1. Nợ: Phải thu (HEADER - Tổng tiền thanh toán)
            {
                'rule_level': 'HEADER',
                'priority': 10,
                'role_key': 'RECEIVABLE',
                'side': 'DEBIT',
                'amount_source': 'TOTAL',
                'account_source_type': 'FIXED', 'fixed_account_code': '131',
                'description': 'Phải thu khách hàng (131)',
            },

            # 2. Có: Thuế (HEADER - Tổng thuế)
            {
                'rule_level': 'HEADER',
                'priority': 20,
                'role_key': 'TAX_OUT',
                'side': 'CREDIT',
                'amount_source': 'TAX',
                'account_source_type': 'FIXED', 'fixed_account_code': '33311',
                'description': 'Thuế GTGT đầu ra (33311)',
            },

            # 3. Có: Đối trừ Doanh thu tạm (LINE - Chi tiết từng dòng)
            # [CHỐT]: Dùng LINE để khớp với DO_SALE
            {
                'rule_level': 'LINE',
                'priority': 30,
                'role_key': 'DONI',
                'side': 'CREDIT',
                'amount_source': 'SALES',  # Lấy Net Amount từng dòng
                'account_source_type': 'FIXED', 'fixed_account_code': '13881',
                'description': 'Đối trừ hàng đã xuất (13881)',
            },
        ]
    },

    # =========================================================================
    # NHÓM 2: MUA HÀNG (PURCHASE CYCLE)
    # Flow: GRN (Treo 33881) -> INVOICE (Clear 33881, Ghi 331)
    # =========================================================================

    # 2.1. NHẬP KHO MUA HÀNG (GRN_PURCHASE)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'GRN_PURCHASE',
        'posting_rule_list': [
            # 1. Nợ: Tăng kho (LINE)
            {
                'rule_level': 'LINE',
                'priority': 10,
                'role_key': 'ASSET',
                'side': 'DEBIT',
                'amount_source': 'COST',
                'account_source_type': 'FIXED', 'fixed_account_code': '1561',
                'description': 'Nhập kho hàng hóa (1561)',
            },
            # 2. Có: Nợ tạm tính (LINE - Chi tiết để khớp Invoice sau này)
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

    # 2.2. HÓA ĐƠN MUA HÀNG (PURCHASE_INVOICE)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'PURCHASE_INVOICE',
        'posting_rule_list': [
            # 1. Nợ: Đối trừ nợ tạm (LINE - Chi tiết từng dòng)
            # [CHỐT]: Dùng LINE để khớp với GRN_PURCHASE
            {
                'rule_level': 'LINE',
                'priority': 10,
                'role_key': 'GRNI',
                'side': 'DEBIT',
                'amount_source': 'COST',  # Engine sẽ tìm các dòng LINE có COST trong JEDocData
                'account_source_type': 'FIXED', 'fixed_account_code': '33881',
                'description': 'Đối trừ hàng về chưa hóa đơn',
            },

            # 2. Nợ: Thuế (HEADER - Tổng thuế)
            {
                'rule_level': 'HEADER',
                'priority': 20,
                'role_key': 'TAX_IN',
                'side': 'DEBIT',
                'amount_source': 'TAX',
                'account_source_type': 'FIXED', 'fixed_account_code': '1331',
                'description': 'Thuế GTGT đầu vào',
            },

            # 3. Có: Phải trả (HEADER - Tổng phải trả)
            {
                'rule_level': 'HEADER',
                'priority': 30,
                'role_key': 'PAYABLE',
                'side': 'CREDIT',
                'amount_source': 'TOTAL',
                'account_source_type': 'FIXED', 'fixed_account_code': '331',
                'description': 'Phải trả người bán',
            },
        ]
    },

    # =========================================================================
    # NHÓM 3: TIỀN TỆ (CASH & BANK)
    # =========================================================================

    # 3.1. PHIẾU CHI (CASH_OUT)
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

    # -------------------------------------------------------------------------
    # 3.2. PHIẾU THU (CASH_IN)
    # Nghiệp vụ: Thu tiền khách hàng (Nợ 111, 112 / Có 131)
    # -------------------------------------------------------------------------
    {
        'je_doc_type': 'CASH_IN',
        'posting_rule_list': [
            # 1. Nợ: Tăng Tiền mặt (HEADER)
            {
                'rule_level': 'HEADER',
                'priority': 10,
                'role_key': 'CASH',
                'side': 'DEBIT', # <--- Nợ (Tiền tăng)
                'amount_source': 'CASH', # Lấy số tiền mặt thực thu
                'account_source_type': 'FIXED', 'fixed_account_code': '1111',
                'description': 'Thu tiền mặt',
            },
            # 2. Nợ: Tăng Tiền gửi (HEADER)
            {
                'rule_level': 'HEADER',
                'priority': 20,
                'role_key': 'BANK',
                'side': 'DEBIT', # <--- Nợ (Tiền tăng)
                'amount_source': 'BANK', # Lấy số tiền chuyển khoản thực thu
                'account_source_type': 'FIXED', 'fixed_account_code': '1121',
                'description': 'Thu tiền gửi ngân hàng',
            },
            # 3. Có: Giảm Phải thu (HEADER)
            {
                'rule_level': 'HEADER',
                'priority': 30,
                'role_key': 'RECEIVABLE',
                'side': 'CREDIT', # <--- Có (Giảm nợ phải thu)
                'amount_source': 'TOTAL', # Tổng tiền thu được (Cash + Bank)
                'account_source_type': 'FIXED', 'fixed_account_code': '131',
                'description': 'Thu tiền khách hàng (Giảm nợ)',
            },
        ]
    },
]

POSTING_GROUP_LIST = [
    # =========================================================================
    # 1. NHÓM SẢN PHẨM / VẬT TƯ (ITEM_GROUP)
    # Mục đích: Định tuyến vào các TK 156, 155, 152, 153, 5111, 5112, 5113...
    # =========================================================================
    {
        'code': 'GOODS',
        'title': 'Hàng hóa',  # Mua đi bán lại (1561)
        'posting_group_type': 'ITEM_GROUP',
    },
    {
        'code': 'FINISHED_GOODS',
        'title': 'Thành phẩm',  # Tự sản xuất (155)
        'posting_group_type': 'ITEM_GROUP',
    },
    {
        'code': 'SEMI_FINISHED',  # Bổ sung
        'title': 'Bán thành phẩm',  # Dở dang (154)
        'posting_group_type': 'ITEM_GROUP',
    },
    {
        'code': 'MATERIAL',
        'title': 'Nguyên vật liệu',  # Nguyên liệu sx (152)
        'posting_group_type': 'ITEM_GROUP',
    },
    {
        'code': 'TOOL',
        'title': 'Công cụ - Dụng cụ',  # Phân bổ dần (153)
        'posting_group_type': 'ITEM_GROUP',
    },
    {
        'code': 'SERVICE',
        'title': 'Dịch vụ',  # [FIX] Sửa lại title thành Dịch vụ (Không kho, 5113)
        'posting_group_type': 'ITEM_GROUP',
    },
    {
        'code': 'CONSIGNMENT',  # Bổ sung
        'title': 'Hàng gửi đi bán',  # Ký gửi đại lý (157)
        'posting_group_type': 'ITEM_GROUP',
    },

    # =========================================================================
    # 2. NHÓM ĐỐI TÁC (PARTNER_GROUP)
    # Mục đích: Định tuyến vào các TK 131, 331 (Nội địa/Ngoại tệ)
    # =========================================================================

    # --- KHÁCH HÀNG (Dùng cho 131) ---
    {
        'code': 'CUSTOMER_VN',
        'title': 'Khách hàng Nội địa',  # 1311
        'posting_group_type': 'PARTNER_GROUP',
    },
    {
        'code': 'CUSTOMER_FOREIGN',  # Bổ sung
        'title': 'Khách hàng Nước ngoài',  # 1312 (Theo dõi ngoại tệ)
        'posting_group_type': 'PARTNER_GROUP',
    },
    {
        'code': 'CUSTOMER_RETAIL',  # Bổ sung
        'title': 'Khách lẻ / Vãng lai',  # Thường không theo dõi chi tiết công nợ lâu dài
        'posting_group_type': 'PARTNER_GROUP',
    },

    # --- NHÀ CUNG CẤP (Dùng cho 331) ---
    {
        'code': 'SUPPLIER_VN',  # Bổ sung
        'title': 'Nhà cung cấp Nội địa',  # 3311
        'posting_group_type': 'PARTNER_GROUP',
    },
    {
        'code': 'SUPPLIER_FOREIGN',  # Bổ sung
        'title': 'Nhà cung cấp Nước ngoài',  # 3312 (Nhập khẩu)
        'posting_group_type': 'PARTNER_GROUP',
    },

    # --- NHÂN VIÊN (Dùng cho 141 - Tạm ứng) ---
    {
        'code': 'EMPLOYEE',  # Bổ sung
        'title': 'Nhân viên',
        'posting_group_type': 'PARTNER_GROUP',
    },
]

GL_MAPPING_TEMPLATE = {
    # --- ITEM GROUPS ---
    'GOODS': { # Hàng hóa
        'ASSET': '1561', 'COGS': '632', 'REVENUE': '5111',
        'DONI': '13881', 'GRNI': '33881'
    },
    'FINISHED_GOODS': { # Thành phẩm
        'ASSET': '155', 'COGS': '632', 'REVENUE': '5112', # DT bán thành phẩm
        'DONI': '13881', 'GRNI': '33881'
    },
    'SEMI_FINISHED': { # Bán thành phẩm
        'ASSET': '154', 'COGS': '632', 'REVENUE': '5112',
        'DONI': '13881', 'GRNI': '33881'
    },
    'MATERIAL': { # Nguyên vật liệu
        'ASSET': '152', 'COGS': '632', 'REVENUE': '5111', # Thường ít bán NVL, nếu bán ghi vào 511 hoặc 711
        'DONI': '13881', 'GRNI': '33881'
    },
    'TOOL': { # CCDC
        'ASSET': '153', 'COGS': '632', 'REVENUE': '5111',
        'DONI': '13881', 'GRNI': '33881'
    },
    'SERVICE': { # Dịch vụ (Không kho)
        'ASSET': None, # Không có TK kho
        'COGS': '632', 'REVENUE': '5113', # DT Dịch vụ
        'DONI': '13881', 'GRNI': '33881'
    },
    'CONSIGNMENT': { # Hàng gửi bán
        'ASSET': '157', 'COGS': '632', 'REVENUE': '5111',
        'DONI': '13881', 'GRNI': '33881'
    },

    # --- PARTNER GROUPS ---
    'CUSTOMER_VN': {
        'RECEIVABLE': '131', 'TAX_OUT': '33311', 'CASH': '1111', 'BANK': '1121'
    },
    'CUSTOMER_FOREIGN': {
        'RECEIVABLE': '131', 'TAX_OUT': '33311', 'CASH': '1112', 'BANK': '1122' # Ngoại tệ
    },
    'SUPPLIER_VN': {
        'PAYABLE': '331', 'TAX_IN': '1331', 'CASH': '1111', 'BANK': '1121'
    },
    'SUPPLIER_FOREIGN': {
        'PAYABLE': '331', 'TAX_IN': '1331', 'CASH': '1112', 'BANK': '1122'
    },
    'EMPLOYEE': {
        'PAYABLE': '334', # Phải trả người lao động
        'RECEIVABLE': '141' # Tạm ứng
    }
}
