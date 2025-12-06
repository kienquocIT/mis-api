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

# Danh sách các Nhóm định khoản cần tạo
POSTING_GROUP_LIST = [
    # --- ITEM GROUPS ---
    {'code': 'GOODS', 'title': 'Hàng hóa', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'FINISHED_GOODS', 'title': 'Thành phẩm', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'SEMI_FINISHED', 'title': 'Bán thành phẩm', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'MATERIAL', 'title': 'Nguyên vật liệu', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'TOOL', 'title': 'Công cụ - Dụng cụ', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'SERVICE', 'title': 'Dịch vụ', 'posting_group_type': 'ITEM_GROUP'},
    {'code': 'CONSIGNMENT', 'title': 'Hàng gửi đi bán', 'posting_group_type': 'ITEM_GROUP'},

    # --- PARTNER GROUPS ---
    {'code': 'CUSTOMER_VN', 'title': 'Khách hàng Nội địa', 'posting_group_type': 'PARTNER_GROUP'},
    {'code': 'CUSTOMER_FOREIGN', 'title': 'Khách hàng Nước ngoài', 'posting_group_type': 'PARTNER_GROUP'},
    {'code': 'CUSTOMER_RETAIL', 'title': 'Khách lẻ / Vãng lai', 'posting_group_type': 'PARTNER_GROUP'},
    {'code': 'SUPPLIER_VN', 'title': 'Nhà cung cấp Nội địa', 'posting_group_type': 'PARTNER_GROUP'},
    {'code': 'SUPPLIER_FOREIGN', 'title': 'Nhà cung cấp Nước ngoài', 'posting_group_type': 'PARTNER_GROUP'},
    {'code': 'EMPLOYEE', 'title': 'Nhân viên', 'posting_group_type': 'PARTNER_GROUP'},
]

# Template mapping tài khoản chi tiết cho từng nhóm
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
    'CUSTOMER_VN': {
        'RECEIVABLE': '131', 'TAX_OUT': '33311', 'CASH': '1111', 'BANK': '1121'
    },
    'CUSTOMER_FOREIGN': {
        'RECEIVABLE': '131', 'TAX_OUT': '33311', 'CASH': '1112', 'BANK': '1122'
    },
    'CUSTOMER_RETAIL': {
        'RECEIVABLE': '131', 'TAX_OUT': '33311', 'CASH': '1111', 'BANK': '1121'
    },
    'SUPPLIER_VN': {
        'PAYABLE': '331', 'TAX_IN': '1331', 'CASH': '1111', 'BANK': '1121'
    },
    'SUPPLIER_FOREIGN': {
        'PAYABLE': '331', 'TAX_IN': '1331', 'CASH': '1112', 'BANK': '1122'
    },
    'EMPLOYEE': {
        'PAYABLE': '334', 'RECEIVABLE': '141'
    }
}