from django.db import transaction
from apps.core.company.models import Company
from apps.accounting.accountingsettings.models import (
    ChartOfAccounts,
    AccountDetermination,
    AccountDeterminationSub
)
from apps.masterdata.saledata.models.price import Currency

TT200_DATA = {
    'account_chart_assets_table': {
        'acc_type': 1,
        'acc_code_list': [
            111, 1111, 1112, 1113,
            112, 1121, 1122, 1123,
            113, 1131, 1132,
            121, 1211, 1212, 1218,
            128, 1281, 1282, 1283, 1288,
            131,
            133, 1331, 1332,
            136, 1361, 1362, 1363, 1368,
            138, 1381, 1385, 1388,
            141,
            151,
            152,
            153, 1531, 1532, 1533, 1534,
            154,
            155, 1551, 1557,
            156, 1561, 1562, 1567,
            157,
            158,
            161, 1611, 1612,
            171,
            211, 2111, 2112, 2113, 2114, 2115, 2118,
            212, 2121, 2122,
            213, 2131, 2132, 2133, 2134, 2135, 2136, 2138,
            214, 2141, 2142, 2143, 2147,
            217,
            221,
            222,
            228, 2281, 2288,
            229, 2291, 2292, 2293, 2294,
            241, 2411, 2412, 2413,
            242,
            243,
            244
        ],
        'acc_name_list': [
            'Tiền mặt',
            'Tiền Việt Nam',
            'Ngoại tệ',
            'Vàng tiền tệ',
            'Tiền gửi Ngân hàng',
            'Tiền Việt Nam',
            'Ngoại tệ',
            'Vàng tiền tệ',
            'Tiền đang chuyển',
            'Tiền Việt Nam',
            'Ngoại tệ',
            'Chứng khoán kinh doanh',
            'Cổ phiếu',
            'Trái phiếu',
            'Chứng khoán và công cụ tài chính khác',
            'Đầu tư nắm giữ đến ngày đáo hạn',
            'Tiền gửi có kỳ hạn',
            'Trái phiếu',
            'Cho vay',
            'Các khoản đầu tư khác nắm giữ đến ngày đáo hạn',
            'Phải thu của khách hàng',
            'Thuế GTGT được khấu trừ',
            'Thuế GTGT được khấu trừ của hàng hóa, dịch vụ',
            'Thuế GTGT được khấu trừ của TSCĐ',
            'Phải thu nội bộ',
            'Vốn kinh doanh ở các đơn vị trực thuộc',
            'Phải thu nội bộ về chênh lệch tỷ giá',
            'Phải thu nội bộ về chi phí đi vay đủ điều kiện được vốn hóa',
            'Phải thu nội bộ khác',
            'Phải thu khác',
            'Tài sản thiếu chờ xử lý',
            'Phải thu về cổ phần hóa',
            'Phải thu khác',
            'Tạm ứng',
            'Hàng mua đang đi đường',
            'Nguyên liệu, vật liệu',
            'Công cụ, dụng cụ',
            'Công cụ, dụng cụ',
            'Bao bì luân chuyển',
            'Đồ dùng cho thuê',
            'Thiết bị, phụ tùng thay thế',
            'Chi phí sản xuất, kinh doanh dở dang',
            'Thành phẩm',
            'Thành phẩm nhập kho',
            'Thành phẩm bất động sản',
            'Hàng hóa',
            'Giá mua hàng hóa',
            'Chi phí thu mua hàng hóa',
            'Hàng hóa bất động sản',
            'Hàng gửi đi bán',
            'Hàng hóa kho bảo thuế',
            'Chi sự nghiệp',
            'Chi sự nghiệp năm trước',
            'Chi sự nghiệp năm nay',
            'Giao dịch mua bán lại trái phiếu chính phủ',
            'Tài sản cố định hữu hình',
            'Nhà cửa, vật kiến trúc',
            'Máy móc, thiết bị', 'Phương tiện vận tải, truyền dẫn',
            'Thiết bị, dụng cụ quản lý',
            'Cây lâu năm, súc vật làm việc và cho sản phẩm',
            'TSCĐ khác',
            'Tài sản cố định thuê tài chính',
            'TSCĐ hữu hình thuê tài chính',
            'TSCĐ vô hình thuê tài chính',
            'Tài sản cố định vô hình',
            'Quyền sử dụng đất',
            'Quyền phát hành',
            'Bản quyền, bằng sáng chế',
            'Nhãn hiệu, tên thương mại',
            'Chương trình phần mềm',
            'Giấy phép và giấy phép nhượng quyền',
            'TSCĐ vô hình khác',
            'Hao mòn tài sản cố định',
            'Hao mòn TSCĐ hữu hình',
            'Hao mòn TSCĐ thuê tài chính',
            'Hao mòn TSCĐ vô hình',
            'Hao mòn bất động sản đầu tư',
            'Bất động sản đầu tư',
            'Đầu tư vào công ty con',
            'Đầu tư vào công ty liên doanh, liên kết',
            'Đầu tư khác',
            'Cổ phiếu',
            'Đầu tư khác',
            'Dự phòng tổn thất tài sản',
            'Dự phòng giảm giá chứng khoán kinh doanh',
            'Dự phòng tổn thất đầu tư vào đơn vị khác',
            'Dự phòng phải thu khó đòi',
            'Dự phòng giảm giá hàng tồn kho',
            'Xây dựng cơ bản dở dang', 'Mua sắm TSCĐ',
            'Xây dựng cơ bản',
            'Sửa chữa lớn TSCĐ',
            'Chi phí trả trước',
            'Tài sản thuế thu nhập hoãn lại',
            'Cầm cố, thế chấp, ký quỹ, ký cược',
        ],
        'acc_foreign_name_list': [
            'Cash in hand', 'Vietnam dong', 'Foreign currency', 'Monetary gold',
            'Cash in bank', 'Vietnam dong', 'Foreign currency', 'Monetary gold',
            'Cash in transit', 'Vietnam dong', 'Foreign currency',
            'Securities trading', 'Stocks', 'Bonds', 'Securities and other financial instruments',
            'Other short - term investment', 'Term deposits', 'Bonds', 'Loan', 'Other short - term investment',
            'Accounts receivable - trade',
            'VAT deducted', 'VAT deduction of goods, services', 'VAT deduction of fixed assets',
            'Intercompany receivable', 'Investment in equity of subsidiaries', 'Internal receivable on rate differences', 'Internal receivable the borrowing costs eligible for capitalization', 'Other receivable from subsidiaries',
            'Other receivable', 'Shortage of assets awaiting resolution', 'Equitization receivable', 'Other receivable',
            'Advances',
            'Goods in transit',
            'Raw materials',
            'Tools and supplies', 'Tools and supplies', 'Packaging rotation', 'Tools for rent', 'Equipment spare parts',
            'Work in progress',
            'Finished goods', 'Finished goods', 'Finished real Estate',
            'Merchandise inventory', 'Price of goods', 'Purchasing expense', 'Real Estate',
            'Goods on consignment',
            'Goods of bonded warehouse',
            'Expenditures from subsidies of state budget', 'Last year', 'This year',
            'Traded purchase and resell government bonds',
            'Tangible fixed assets', 'Houses and architectural', 'Equipment & machines', 'Means of transport, conveyance equipment', 'Managerial equipment and instruments', 'Long term trees, working & killed animals', 'Other tangible fixed assets',
            'Financial leasing fixed assets', 'Tangible financial leasing fixed assets', 'Intangible financial leasing fixed assets',
            'Intangible fixed assets', 'Land using right', 'Distribution rights', 'Copyright, patents', 'Trademark', 'Software', 'License and right concession permits', 'Other intangible fixed assets',
            'Depreciation of fixed assets', 'Tangible fixed assets depreciation', 'Financial leasing fixed assets depreciation', 'Intangible fixed assets depreciation', 'Investment real estate depreciation',
            'Investment real estate',
            'Investment in equity of subsidiaries',
            'Joint venture capital contribution',
            'Other long term investments', 'Stocks', 'Other long-term investment',
            'Provision for assets', 'Provision for the diminution in value of short-term investments', 'Provision for decline in long term investments', 'Provision for bad debts', 'Provision for decline in inventory',
            'Construction in process', 'Fixed assets purchases', 'Construction in process', 'Major repair of fixed assets',
            'Prepaid expenses',
            'Deffered income tax assets',
            'Long term collateral & deposit',
        ]
    },
    'account_chart_liabilities_table': {
        'acc_type': 2,
        'acc_code_list': [
            331,
            333, 3331, 33311, 33312, 3332, 3333, 3334, 3335, 3336, 3337, 3338, 33381, 33382, 3339,
            334, 3341, 3348,
            335,
            336, 3361, 3362, 3363, 3368,
            337,
            338, 3381, 3382, 3383, 3384, 3385, 3386, 3387, 3388,
            341, 3411, 3412,
            343, 3431, 34311, 34312, 34313, 3432,
            344,
            347,
            352, 3521, 3522, 3523, 3524,
            353, 3531, 3532, 3533, 3534,
            356, 3561, 3562,
            357,
        ],
        'acc_name_list': [
            'Phải trả cho người bán',
            'Thuế và các khoản phải nộp Nhà nước',
            'Thuế giá trị gia tăng phải nộp',
            'Thuế GTGT đầu ra',
            'Thuế GTGT hàng nhập khẩu',
            'Thuế tiêu thụ đặc biệt',
            'Thuế xuất, nhập khẩu',
            'Thuế thu nhập doanh nghiệp',
            'Thuế thu nhập cá nhân',
            'Thuế tài nguyên',
            'Thuế nhà đất, tiền thuê đất',
            'Thuế bảo vệ môi trường và các loại thuế khác',
            'Thuế bảo vệ môi trường',
            'Các loại thuế khác',
            'Phí, lệ phí và các khoản phải nộp khác',
            'Phải trả người lao động',
            'Phải trả công nhân viên',
            'Phải trả người lao động khác',
            'Chi phí phải trả',
            'Phải trả nội bộ',
            'Phải trả nội bộ về vốn kinh doanh',
            'Phải trả nội bộ về chênh lệch tỷ giá',
            'Phải trả nội bộ về chi phí đi vay đủ điều kiện được vốn hóa',
            'Phải trả nội bộ khác',
            'Thanh toán theo tiến độ kế hoạch hợp đồng xây dựng',
            'Phải trả, phải nộp khác',
            'Tài sản thừa chờ giải quyết',
            'Kinh phí công đoàn',
            'Bảo hiểm xã hội',
            'Bảo hiểm y tế',
            'Phải trả về cổ phần hóa',
            'Bảo hiểm thất nghiệp',
            'Doanh thu chưa thực hiện',
            'Phải trả, phải nộp khác',
            'Vay và nợ thuê tài chính',
            'Các khoản đi vay',
            'Nợ thuê tài chính',
            'Trái phiếu phát hành',
            'Trái phiếu thường',
            'Mệnh giá trái phiếu',
            'Chiết khấu trái phiếu',
            'Phụ trội trái phiếu',
            'Trái phiếu chuyển đổi',
            'Nhận ký quỹ, ký cược',
            'Thuế thu nhập hoãn lại phải trả',
            'Dự phòng phải trả',
            'Dự phòng bảo hành sản phẩm hàng hóa',
            'Dự phòng bảo hành công trình xây dựng',
            'Dự phòng tái cơ cấu doanh nghiệp',
            'Dự phòng phải trả khác',
            'Quỹ khen thưởng, phúc lợi',
            'Quỹ khen thưởng',
            'Quỹ phúc lợi',
            'Quỹ phúc lợi đã hình thành TSCĐ',
            'Quỹ thưởng ban quản lý điều hành công ty',
            'Quỹ phát triển khoa học và công nghệ',
            'Quỹ phát triển khoa học và công nghệ',
            'Quỹ phát triển khoa học và công nghệ đã hình thành TSCĐ',
            'Quỹ bình ổn giá',
        ],
        'acc_foreign_name_list': [
            'Payable to seller',
            'Taxes and payable to state budget',
            'Value Added Tax',
            'VAT output',
            'VAT for imported goods',
            'Special consumption tax',
            'Import & export duties',
            'Profit tax',
            'Personal income tax',
            'Natural resource tax',
            'Land & housing tax, land rental charges',
            'Other taxes',
            'Invironmental protection tax',
            'Other taxes',
            'Fee & charge & other payables',
            'Payable to employees',
            'Payable to employees',
            'Payable to other employees',
            'Accruals',
            'Intercompany payable',
            'Internal payable on capital',
            'Internal payable on rate differences',
            'Internal pay the borrowing costs eligible for capitalization',
            'Other internal payable',
            'Construction contract progress payment due to customers',
            'Other payable',
            'Surplus assets awaiting for resolution',
            'Trade Union fees',
            'Social insurance',
            'Health insurance',
            'Privatization payable',
            'Unemployment insurance',
            'Unrealized turnover',
            'Other payable',
            'Borrowing and fincance lease liabilities',
            'Borrowing',
            'Finance lease liabilities',
            'Issued bond',
            'Bond face value',
            'Bond face value',
            'Bond discount',
            'Additional bond',
            'Bond discount',
            'Long-term deposits received',
            'Deferred income tax',
            'Provisions for payables',
            'Product warranty provision',
            'Construction warranty provision',
            'Corporate restructuring provision',
            'Other payables provision',
            'Bonus & welfare funds',
            'Bonus fund',
            'Welfare fund',
            'Welfare fund used to acquire fixed assets',
            'Reward fund for management and operating company',
            'Development of science and technology fund',
            'Development of science and technology fund',
            'Development of science and technology fund used to fixed assets',
            'Stabilitization fund',
        ],
    },
    'account_chart_owner_equity_table': {
        'acc_type': 3,
        'acc_code_list': [
            411, 4111, 41111, 41112, 4112, 4113, 4118,
            412,
            413, 4131, 4132,
            414,
            417,
            418,
            419,
            421, 4211, 4212,
            441,
            461, 4611, 4612,
            466,
        ],
        'acc_name_list': [
            'Vốn đầu tư của chủ sở hữu',
            'Vốn góp của chủ sở hữu',
            'Cổ phiếu phổ thông có quyền biểu quyết',
            'Cổ phiếu ưu đãi',
            'Thặng dư vốn cổ phần',
            'Quyền chọn chuyển đổi trái phiếu',
            'Vốn khác',
            'Chênh lệch đánh giá lại tài sản',
            'Chênh lệch tỷ giá hối đoái',
            'Chênh lệch tỷ giá do đánh giá lại các khoản mục tiền tệ có gốc ngoại tệ',
            'Chênh lệch tỷ giá hối đoái trong giai đoạn trước hoạt động',
            'Quỹ đầu tư phát triển',
            'Quỹ hỗ trợ sắp xếp doanh nghiệp',
            'Các quỹ khác thuộc vốn chủ sở hữu',
            'Cổ phiếu quỹ',
            'Lợi nhuận sau thuế chưa phân phối',
            'Lợi nhuận sau thuế chưa phân phối năm trước',
            'Lợi nhuận sau thuế chưa phân phối năm nay',
            'Nguồn vốn đầu tư xây dựng cơ bản',
            'Nguồn kinh phí sự nghiệp',
            'Nguồn kinh phí sự nghiệp năm trước',
            'Nguồn kinh phí sự nghiệp năm nay',
            'Nguồn kinh phí đã hình thành TSCĐ',
        ],
        'acc_foreign_name_list': [
            'Working capital',
            'Contributed legal capital',
            'Ordinary shares with voting rights',
            'Preference shares',
            'Share premium',
            'Conversion option bonds',
            'Other capital',
            'Differences upon asset revaluation',
            'Foreign exchange differences',
            'Foreign exchange differences revaluation at the end fiscal year',
            'Foreign exchange differences in period capital construction investment',
            'Investment & development funds',
            'Business arrangements support fund',
            'Other funds',
            'Treasury stock',
            'Undistributed earnings',
            'Previous year undistributed earnings',
            'This year undistributed earnings',
            'Construction investment fund',
            'Budget resources',
            'Precious year budget resources',
            'This year budget resources',
            'Budget resources used to acquire fixed assets',
        ]
    },
    'account_chart_revenue_table': {
        'acc_type': 4,
        'acc_code_list': [
            511, 5111, 5112, 5113, 5114, 5117, 5118, 515,
            521, 5211, 5212, 5213,
        ],
        'acc_name_list': [
            'Doanh thu bán hàng và cung cấp dịch vụ',
            'Doanh thu bán hàng hóa',
            'Doanh thu bán các thành phẩm',
            'Doanh thu cung cấp dịch vụ',
            'Doanh thu trợ cấp, trợ giá',
            'Doanh thu kinh doanh bất động sản đầu tư',
            'Doanh thu khác',
            'Doanh thu hoạt động tài chính',
            'Các khoản giảm trừ doanh thu',
            'Chiết khấu thương mại',
            'Hàng bán bị trả lại',
            'Giảm giá hàng bán',
        ],
        'acc_foreign_name_list': [
            'Sales',
            'Goods sale',
            'Finished product sale',
            'Turnover from service provision',
            'Subsidization sale',
            'Investment real estate sale',
            'Other sales',
            'Turnover from financial operations',
            'Deduction from income',
            'Sale discount',
            'Sale returns',
            'Devaluation of sale price',
        ]
    },
    'account_chart_costs_table': {
        'acc_type': 5,
        'acc_code_list': [
            611, 6111, 6112,
            621,
            622,
            623, 6231, 6232, 6233, 6234, 6237, 6238,
            627, 6271, 6272, 6273, 6274, 6277, 6278,
            631,
            632,
            635,
            641, 6411, 6412, 6413, 6414, 6415, 6417, 6418,
            642, 6421, 6422, 6423, 6424, 6425, 6426,
            6427,
            6428,
        ],
        'acc_name_list': [
            'Mua hàng',
            'Mua nguyên liệu, vật liệu',
            'Mua hàng hóa',
            'Chi phí nguyên liệu, vật liệu trực tiếp',
            'Chi phí nhân công trực tiếp',
            'Chi phí sử dụng máy thi công',
            'Chi phí nhân công',
            'Chi phí vật liệu',
            'Chi phí dụng cụ sản xuất',
            'Chi phí khấu hao máy thi công',
            'Chi phí dịch vụ mua ngoài',
            'Chi phí bằng tiền khác',
            'Chi phí sản xuất chung',
            'Chi phí nhân viên phân xưởng',
            'Chi phí vật liệu',
            'Chi phí dụng cụ sản xuất',
            'Chi phí khấu hao TSCĐ',
            'Chi phí dịch vụ mua ngoài',
            'Chi phí bằng tiền khác',
            'Giá thành sản xuất',
            'Giá vốn hàng bán',
            'Chi phí tài chính',
            'Chi phí bán hàng',
            'Chi phí nhân viên',
            'Chi phí vật liệu, bao bì',
            'Chi phí dụng cụ, đồ dùng',
            'Chi phí khấu hao TSCĐ',
            'Chi phí bảo hành',
            'Chi phí dịch vụ mua ngoài',
            'Chi phí bằng tiền khác',
            'Chi phí quản lý doanh nghiệp',
            'Chi phí nhân viên quản lý',
            'Chi phí vật liệu quản lý',
            'Chi phí đồ dùng văn phòng',
            'Chi phí khấu hao TSCĐ',
            'Thuế, phí và lệ phí',
            'Chi phí dự phòng',
            'Chi phí dịch vụ mua ngoài',
            'Chi phí bằng tiền khác',
        ],
        'acc_foreign_name_list': [
            'Purchase',
            'Raw materials purchase',
            'Goods purchase',
            'Direct raw materials cost',
            'Direct labor cost',
            'Executing machine using cost',
            'Labor cost',
            'Material cost',
            'Production tool cost',
            'Executing machine depreciation',
            'Outside purchasing services cost',
            'Other cost of cash',
            'General operation cost',
            'Employees cost',
            'Material cost',
            'Production tool cost',
            'Fixed asset depreciation',
            'Outside purchasing services cost',
            'Other cost of cash',
            'Production cost',
            'Cost of goods sold',
            'Financial activities expenses',
            'Selling expenses',
            'Employees cost',
            'Material, packing cost',
            'Tool cost',
            'Fixed asset depreciation',
            'Warranty cost',
            'Outside purchasing services cost',
            'Other cost of cash',
            'General & administration expenses',
            'Employees cost',
            'Tools cost',
            'Stationery cost',
            'Fixed asset depreciation',
            'Taxes, fees, charges',
            'Provision cost',
            'Outside purchasing services cost',
            'Other cost of cash',
        ]
    },
    'account_chart_other_income_table': {
        'acc_type': 6,
        'acc_code_list': [
            711
        ],
        'acc_name_list': [
            'Thu nhập khác'
        ],
        'acc_foreign_name_list': [
            'Other income'
        ]
    },
    'account_chart_other_expense_table': {
        'acc_type': 7,
        'acc_code_list': [
            811,
            821, 8211, 8212,
        ],
        'acc_name_list': [
            'Chi phí khác',
            'Chi phí thuế thu nhập doanh nghiệp',
            'Chi phí thuế TNDN hiện hành',
            'Chi phí thuế TNDN hoãn lại',
        ],
        'acc_foreign_name_list': [
            'Other expenses',
            'Business Income tax charge',
            'Current business income tax charge',
            'Deffered business income tax charge',
        ]
    },
    'account_chart_income_summary_table': {
        'acc_type': 8,
        'acc_code_list': [
            911
        ],
        'acc_name_list': [
            'Xác định kết quả kinh doanh'
        ],
        'acc_foreign_name_list': [
            'Evaluation of business results'
        ]
    }
}

RULE_CONFIG = [
    # -------------------------------------------------------------------------
    # 1. CHIỀU BÁN HÀNG: XUẤT KHO (DO_SALE)
    # -------------------------------------------------------------------------
    {
        'transaction_key': 'DO_SALE',
        'foreign_title': 'Delivery Order (Unbilled)',
        'title': 'Xuất kho bán hàng (Chưa hóa đơn)',
        'account_determination_type': 2,
        'description': 'Ghi nhận Giá vốn (632/156) và Doanh thu tạm tính (13881/511)',  # <--- Mới thêm
        'rule_config': [
            # Line 1: Giá vốn hàng bán (632)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'COST',
                'role_key': 'COGS',
                'side': 'DEBIT',
                'rule_level': 'LINE',

                'fixed_account_code': '632',
                'order': 1,
                'description': 'Giá vốn hàng bán (632)'
            },
            # Line 2: Giảm kho hàng hóa (1561)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'COST',
                'role_key': 'ASSET',
                'side': 'CREDIT',
                'rule_level': 'LINE',

                'fixed_account_code': '1561',
                'order': 2,
                'description': 'Giảm kho hàng hóa (1561)'
            },
            # Line 3: Phải thu tạm tính (13881)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'SALES',
                'role_key': 'DONI',
                'side': 'DEBIT',
                'rule_level': 'LINE',

                'fixed_account_code': '13881',
                'order': 3,
                'description': 'Phải thu tạm tính/Chưa hóa đơn (13881)'
            },
            # Line 4: Doanh thu bán hàng (5111)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'SALES',
                'role_key': 'REVENUE',
                'side': 'CREDIT',
                'rule_level': 'LINE',

                'fixed_account_code': '5111',
                'order': 4,
                'description': 'Doanh thu bán hàng (5111)'
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 2. CHIỀU BÁN HÀNG: HÓA ĐƠN (SALES_INVOICE)
    # -------------------------------------------------------------------------
    {
        'transaction_key': 'SALES_INVOICE',
        'foreign_title': 'VAT AR Invoice',
        'title': 'Hóa đơn bán hàng GTGT',
        'account_determination_type': 0,
        'description': 'Đối trừ TK 13881, ghi nhận Thuế (33311) và Công nợ khách hàng (131)',  # <--- Mới thêm
        'rule_config': [
            # Line 1: Công nợ phải thu (131)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'TOTAL',
                'role_key': 'RECEIVABLE',
                'side': 'DEBIT',
                'rule_level': 'HEADER',

                'fixed_account_code': '131',
                'order': 1,
                'description': 'Phải thu khách hàng (131)'
            },
            # Line 2: Đối trừ trung gian (13881)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'SALES',
                'role_key': 'DONI',
                'side': 'CREDIT',
                'rule_level': 'LINE',

                'fixed_account_code': '13881',
                'order': 2,
                'description': 'Đối trừ hàng đã xuất (13881)'
            },
            # Line 3: Thuế GTGT đầu ra (33311)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'TAX',
                'role_key': 'TAX_OUT',
                'side': 'CREDIT',
                'rule_level': 'HEADER',

                'fixed_account_code': '33311',
                'order': 3,
                'description': 'Thuế GTGT đầu ra (33311)'
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 3. CHIỀU MUA HÀNG: NHẬP KHO (GRN_PURCHASE)
    # -------------------------------------------------------------------------
    {
        'transaction_key': 'GRN_PURCHASE',
        'foreign_title': 'Goods Receipt (Unbilled)',
        'title': 'Nhập kho mua hàng (Chưa hóa đơn)',
        'account_determination_type': 2,
        'description': 'Ghi tăng kho (156) và ghi nhận vào TK trung gian (33881)',  # <--- Mới thêm
        'rule_config': [
            # Line 1: Nhập kho (1561)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'COST',
                'role_key': 'ASSET',
                'side': 'DEBIT',
                'rule_level': 'LINE',

                'fixed_account_code': '1561',
                'order': 1,
                'description': 'Nhập kho hàng hóa (1561)'
            },
            # Line 2: Phải trả tạm tính (33881)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'COST',
                'role_key': 'GRNI',
                'side': 'CREDIT',
                'rule_level': 'LINE',

                'fixed_account_code': '33881',
                'order': 2,
                'description': 'Phải trả tạm tính (33881)'
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 4. CHIỀU MUA HÀNG: HÓA ĐƠN (PURCHASE_INVOICE)
    # -------------------------------------------------------------------------
    {
        'transaction_key': 'PURCHASE_INVOICE',
        'foreign_title': 'VAT AP Invoice',
        'title': 'Hóa đơn mua hàng GTGT',
        'account_determination_type': 1,
        'description': 'Đối trừ TK 33881, ghi nhận Thuế (1331) và Công nợ phải trả (331)',  # <--- Mới thêm
        'rule_config': [
            # Line 1: Đối trừ trung gian (33881)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'COST',
                'role_key': 'GRNI',
                'side': 'DEBIT',
                'rule_level': 'LINE',

                'fixed_account_code': '33881',
                'order': 1,
                'description': 'Đối trừ hàng về chưa hóa đơn (33881)'
            },
            # Line 2: Thuế GTGT đầu vào (1331)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'TAX',
                'role_key': 'TAX_IN',
                'side': 'DEBIT',
                'rule_level': 'HEADER',

                'fixed_account_code': '1331',
                'order': 2,
                'description': 'Thuế GTGT đầu vào (1331)'
            },
            # Line 3: Phải trả người bán (331)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'TOTAL',
                'role_key': 'PAYABLE',
                'side': 'CREDIT',
                'rule_level': 'HEADER',

                'fixed_account_code': '331',
                'order': 3,
                'description': 'Phải trả người bán (331)'
            },
        ]
    },

    # -------------------------------------------------------------------------
    # 5. THANH TOÁN (PAYMENT_VOUCHER)
    # -------------------------------------------------------------------------
    {
        'transaction_key': 'PAYMENT_VOUCHER',
        'foreign_title': 'Payment Voucher (Mixed)',
        'title': 'Phiếu chi / Ủy nhiệm chi',
        'account_determination_type': 1,
        'description': 'Thanh toán công nợ (Tiền mặt + Ngân hàng)',  # <--- Mới thêm
        'rule_config': [
            # Line 1: Giảm nợ phải trả (331)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'TOTAL',
                'role_key': 'PAYABLE',
                'side': 'DEBIT',
                'rule_level': 'HEADER',

                'fixed_account_code': '331',
                'order': 1,
                'description': 'Giảm nợ phải trả NCC (331)'
            },
            # Line 2: Chi tiền mặt (1111)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'CASH',
                'role_key': 'CASH',
                'side': 'CREDIT',
                'rule_level': 'HEADER',

                'fixed_account_code': '1111',
                'order': 2,
                'description': 'Chi tiền mặt (1111)'
            },
            # Line 3: Chi tiền ngân hàng (1121)
            {
                'account_source_type': 'FIXED',
                'amount_source': 'BANK',
                'role_key': 'BANK',
                'side': 'CREDIT',
                'rule_level': 'HEADER',

                'fixed_account_code': '1121',
                'order': 3,
                'description': 'Chi tiền gửi ngân hàng (1121)'
            }
        ]
    }
]


class AccountScript:
    """
    Class khởi tạo dữ liệu gốc (Master Data).
    """

    @staticmethod
    def generate_account_200(company_id):
        """ Tạo cây tài khoản kế toán chuẩn TT200 """
        try:
            company_obj = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return False

        # Lấy data từ biến hằng số (đã tách file hoặc để chung)
        list_table = [
            'account_chart_assets_table',
            'account_chart_liabilities_table',
            'account_chart_owner_equity_table',
            'account_chart_revenue_table',
            'account_chart_costs_table',
            'account_chart_other_income_table',
            'account_chart_other_expense_table',
            'account_chart_income_summary_table'
        ]

        with transaction.atomic():
            ChartOfAccounts.objects.filter(company=company_obj).delete()
            primary_currency_obj = Currency.objects.filter_on_company(is_primary=True).first()

            acc_map = {}
            current_order = 0

            for table_key in list_table:
                t_data = TT200_DATA.get(table_key)
                if not t_data: continue

                codes = t_data['acc_code_list']
                names = t_data['acc_name_list']

                for idx, code in enumerate(codes):
                    code_str = str(code)
                    level = len(code_str) - 3

                    parent_obj = None
                    if level > 0:
                        for k in range(1, len(code_str)):
                            potential_parent_code = code_str[:-k]
                            if len(potential_parent_code) < 3: break
                            if int(potential_parent_code) in acc_map:
                                parent_obj = acc_map[int(potential_parent_code)]
                                if not parent_obj.has_child:
                                    parent_obj.has_child = True
                                    parent_obj.is_account = False
                                    parent_obj.save()
                                break

                    new_acc = ChartOfAccounts.objects.create(
                        order=current_order,
                        acc_code=code,
                        acc_name=names[idx],
                        foreign_acc_name=t_data['acc_foreign_name_list'][idx] if idx < len(
                            t_data['acc_foreign_name_list']) else '',
                        acc_type=t_data['acc_type'],
                        company=company_obj,
                        tenant=company_obj.tenant,
                        level=level,
                        is_account=True,
                        currency_mapped=primary_currency_obj,
                        currency_mapped_data={
                            'id': str(primary_currency_obj.id),
                            'abbreviation': primary_currency_obj.abbreviation,
                            'title': primary_currency_obj.title,
                            'rate': primary_currency_obj.rate
                        } if primary_currency_obj else {},
                        is_default=True,
                        has_child=False,
                        parent_account=parent_obj
                    )
                    acc_map[code] = new_acc
                    current_order += 1

        print(f'> Generated chart of account for {company_obj.title} (TT200)')
        return True

    @staticmethod
    def add_account_default_200(company_id):
        """ Thêm các tài khoản đặc thù (Custom Accounts) """
        company_obj = Company.objects.get(id=company_id)

        # 13881: Giao hàng chưa xuất hóa đơn
        ChartOfAccounts.add_account(
            company=company_obj, parent_acc_type=1, parent_acc_code=1388,
            new_acc_code=13881, new_acc_name='Giao hàng chưa xuất HĐ',
            new_foreign_acc_name='Delivered not invoiced'
        )
        # 33881: Nhập hàng chưa có hóa đơn (GR/IR)
        ChartOfAccounts.add_account(
            company=company_obj, parent_acc_type=2, parent_acc_code=3388,
            new_acc_code=33881, new_acc_name='Nhập hàng chưa có HĐ',
            new_foreign_acc_name='Goods receipt not invoiced'
        )
        return True

    @staticmethod
    def generate_account_determination_200(company_id):
        """
        Tạo bộ định khoản mặc định (Default Rules) theo TT200.
        """
        try:
            company_obj = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return False

        with transaction.atomic():
            AccountDetermination.objects.filter(company_id=company_id).delete()
            bulk_sub_create = []
            for order, item in enumerate(RULE_CONFIG):
                rule_config = item.pop('rule_config')
                deter_obj = AccountDetermination.objects.create(
                    tenant=company_obj.tenant,
                    company=company_obj,
                    order=order,
                    **item
                )
                for rule in rule_config:
                    fixed_account_code = rule.pop('fixed_account_code')
                    rule['order'] = rule.get('order') * 10
                    fixed_account_obj = ChartOfAccounts.get_acc(company_id, fixed_account_code)
                    bulk_sub_create.append(AccountDeterminationSub(
                        account_determination=deter_obj,
                        fixed_account=fixed_account_obj,
                        **rule
                    ))
            if bulk_sub_create:
                AccountDeterminationSub.objects.bulk_create(bulk_sub_create)
        print(f'> Successfully initialized Accounting Rules for {company_obj.title}')
        return True

    @staticmethod
    def accounting_reset_default_200(company_id):
        """ Quản lý rule ngoại lệ và Reset hệ thống """
        print(f'--- START RESET ACCOUNTING FOR COMPANY ID {company_id} ---')
        AccountScript.generate_account_200(company_id)
        AccountScript.add_account_default_200(company_id)
        AccountScript.generate_account_determination_200(company_id)
        print('--- RESET DONE :)) ---')
        return True
