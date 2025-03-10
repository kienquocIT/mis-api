from apps.accounting.accountingsettings.models import *
from apps.accounting.accountingsettings.utils import *
from apps.core.company.models import Company
from apps.masterdata.saledata.models import WareHouse, ProductType, Product


class AccountingMasterData:
    @staticmethod
    def generate_account_200():
        """ Tạo các tài khoản kế toản (TT200) """
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
        list_table_data = {
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
        for company in Company.objects.all():
            level1_bulk_create = []
            level2_bulk_create = []
            level3_bulk_create = []
            for table in list_table:
                len1 = len(list_table_data[table]['acc_code_list'])
                len2 = len(list_table_data[table]['acc_name_list'])
                len3 = len(list_table_data[table]['acc_foreign_name_list'])
                if len1 != len2 or len2 != len3 or len1 != len3:
                    print(f'WRONG DATA {len1} != {len2} != {len3}')
                    return False
                else:
                    order = 0
                    for i in range(len(list_table_data[table]['acc_code_list'])):
                        if len(str(list_table_data[table]['acc_code_list'][i])) == 3:
                            item = ChartOfAccounts(
                                order=order,
                                acc_code=list_table_data[table]['acc_code_list'][i],
                                acc_name=list_table_data[table]['acc_name_list'][i],
                                foreign_acc_name=list_table_data[table]['acc_foreign_name_list'][i],
                                acc_type=list_table_data[table]['acc_type'],
                                company=company,
                                tenant=company.tenant,
                                level=len(str(list_table_data[table]['acc_code_list'][i])) - 2,
                                is_default=True
                            )
                            level1_bulk_create.append(item)
                        elif len(str(list_table_data[table]['acc_code_list'][i])) == 4:
                            item = ChartOfAccounts(
                                order=order,
                                parent_account=level1_bulk_create[-1],
                                acc_code=list_table_data[table]['acc_code_list'][i],
                                acc_name=list_table_data[table]['acc_name_list'][i],
                                foreign_acc_name=list_table_data[table]['acc_foreign_name_list'][i],
                                acc_type=list_table_data[table]['acc_type'],
                                company=company,
                                tenant=company.tenant,
                                level=len(str(list_table_data[table]['acc_code_list'][i])) - 2,
                                is_default=True
                            )
                            level1_bulk_create[-1].has_child = True
                            level2_bulk_create.append(item)
                        elif len(str(list_table_data[table]['acc_code_list'][i])) == 5:
                            item = ChartOfAccounts(
                                order=order,
                                parent_account=level2_bulk_create[-1],
                                acc_code=list_table_data[table]['acc_code_list'][i],
                                acc_name=list_table_data[table]['acc_name_list'][i],
                                foreign_acc_name=list_table_data[table]['acc_foreign_name_list'][i],
                                acc_type=list_table_data[table]['acc_type'],
                                company=company,
                                tenant=company.tenant,
                                level=len(str(list_table_data[table]['acc_code_list'][i])) - 2,
                                is_default=True
                            )
                            level2_bulk_create[-1].has_child = True
                            level3_bulk_create.append(item)
                        order += 1
            ChartOfAccounts.objects.filter(company=company, tenant=company.tenant).delete()
            ChartOfAccounts.objects.bulk_create(level1_bulk_create)
            ChartOfAccounts.objects.bulk_create(level2_bulk_create)
            ChartOfAccounts.objects.bulk_create(level3_bulk_create)
            ChartOfAccounts.objects.filter(has_child=False).update(is_account=True)
            print(f'Done for {company.title}')
        print('Done :))')
        return True

    @staticmethod
    def add_account_default():
        # thêm 13881: Giao hàng nhưng chưa xuất hóa đơn bán hàng
        ChartOfAccounts.add_account(
            parent_acc_type=1,
            parent_acc_code=1388,
            new_acc_code=13881,
            new_acc_name='Giao hàng nhưng chưa xuất hóa đơn bán hàng',
            new_foreign_acc_name='Delivered but no AR Invoice yet'
        )
        print('Done :))')
        return True

    @staticmethod
    def generate_default_account_determination_200():
        """ Xác định các tài khoản kế toán mặc định (TT200) """
        for company in Company.objects.all():
            account_mapped_data_sale = [
                {
                    'foreign_title': 'Receivables from domestic customers',
                    'title': 'Phải thu khách hàng trong nước',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='131').first()
                    ]
                },
                {
                    'foreign_title': 'Receivables from foreign customers',
                    'title': 'Phải thu khách hàng nước ngoài',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='131').first()
                    ]
                },
                {
                    'foreign_title': 'Checks received from customers',
                    'title': 'Séc nhận được từ khách hàng',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='131').first()
                    ]
                },
                {
                    'foreign_title': 'Cash in hand received from customers',
                    'title': 'Tiền mặt thu từ khách hàng',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='1111').first()
                    ]
                },
                {
                    'foreign_title': 'Cash in bank received from customers',
                    'title': 'Tiền khách hàng chuyển khoản',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='1121').first()
                    ]
                },
                {
                    'foreign_title': 'Sales tax',
                    'title': 'Thuế GTGT bán hàng',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='3331').first()
                    ]
                },
                {
                    'foreign_title': 'Customer underpayment',
                    'title': 'Khách hàng thanh toán thiếu',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='13881').first()
                    ]
                },
                {
                    'foreign_title': 'Customer overpayment',
                    'title': 'Khách hàng thanh toán thừa',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='3388').first()
                    ]
                },
                {
                    'foreign_title': 'Customer deposit offset',
                    'title': 'Bù trừ đặt cọc khách hàng',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='3387').first()
                    ]
                },
                {
                    'foreign_title': 'Exchange rate difference when actually collected. Gain',
                    'title': 'Lãi chênh lệch tỷ giá khi thực thu',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='515').first()
                    ]
                },
                {
                    'foreign_title': 'Exchange rate difference when actually collected. Loss',
                    'title': 'Lỗ chênh lệch tỷ giá khi thực thu',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='635').first()
                    ]
                },
                {
                    'foreign_title': 'Domestic sales revenue',
                    'title': 'Doanh thu bán hàng trong nước',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='511').first()
                    ]
                },
                {
                    'foreign_title': 'Foreign sales revenue',
                    'title': 'Doanh thu bán hàng nước ngoài',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='511').first()
                    ]
                },
                {
                    'foreign_title': 'Deduction from income',
                    'title': 'Giảm trừ doanh thu',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='521').first()
                    ]
                },
            ]
            account_mapped_data_purchasing = [
                {
                    'foreign_title': 'Payable to domestic suppliers',
                    'title': 'Phải trả nhà cung cấp trong nước',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='331').first()
                    ]
                },
                {
                    'foreign_title': 'Payable to foreign suppliers',
                    'title': 'Phải trả nhà cung cấp nước ngoài',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='331').first()
                    ]
                },
                {
                    'foreign_title': 'Exchange rate difference when paid. Gain',
                    'title': 'Lãi chênh lệch tỷ giá khi thanh toán',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='515').first()
                    ]
                },
                {
                    'foreign_title': 'Exchange rate difference when paid. Loss',
                    'title': 'Lỗ chênh lệch tỷ giá khi thanh toán',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='635').first()
                    ]
                },
                {
                    'foreign_title': 'Expense account',
                    'title': 'Tài khoản chi phí',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='641').first()
                    ]
                },
                {
                    'foreign_title': 'Purchase discount',
                    'title': 'Giảm giá mua hàng',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='521').first()
                    ]
                },
            ]
            account_mapped_data_inventory = [
                {
                    'foreign_title': 'Inventory account',
                    'title': 'Tài khoản hàng tồn kho',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='156').first()
                    ]
                },
                {
                    'foreign_title': 'Cost of goods sold',
                    'title': 'Giá vốn hàng bán',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='632').first()
                    ]
                },
                {
                    'foreign_title': 'Sales returns Aaccount',
                    'title': 'Tài khoản hàng bán bị trả lại',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='521').first()
                    ]
                },
                {
                    'foreign_title': 'Goods in transit',
                    'title': 'Hàng mua đang trên đường',
                    'account': [
                        ChartOfAccounts.objects.filter(company=company, tenant=company.tenant, acc_code='151').first()
                    ]
                }
            ]

            for item in account_mapped_data_sale + account_mapped_data_purchasing + account_mapped_data_inventory:
                if None in item.get('account', []):
                    print(f'Create data failed in {company.title}: None in account list')
                    return False
                if len(item.get('account', [])) != 1:
                    print(f'Create data failed in {company.title}: Account list length is not single')
                    return False
            bulk_info = []
            bulk_info_sub = []
            for order, item in enumerate(account_mapped_data_sale):
                main_obj = DefaultAccountDetermination(
                    company=company,
                    tenant=company.tenant,
                    order=order,
                    title=item.get('title', ''),
                    foreign_title=item.get('foreign_title', ''),
                    default_account_determination_type=0
                )
                bulk_info.append(main_obj)
                for account in item.get('account', []):
                    bulk_info_sub.append(
                        DefaultAccountDeterminationSub(
                            default_acc_deter=main_obj,
                            account_mapped=account,
                            account_mapped_data={
                                'id': str(account.id),
                                'acc_code': account.acc_code,
                                'acc_name': account.acc_name,
                                'foreign_acc_name': account.foreign_acc_name
                            }
                        )
                    )
            for order, item in enumerate(account_mapped_data_purchasing):
                main_obj = DefaultAccountDetermination(
                    company=company,
                    tenant=company.tenant,
                    order=order,
                    title=item.get('title', ''),
                    foreign_title=item.get('foreign_title', ''),
                    default_account_determination_type=1
                )
                bulk_info.append(main_obj)
                for account in item.get('account', []):
                    bulk_info_sub.append(
                        DefaultAccountDeterminationSub(
                            default_acc_deter=main_obj,
                            account_mapped=account,
                            account_mapped_data={
                                'id': str(account.id),
                                'acc_code': account.acc_code,
                                'acc_name': account.acc_name,
                                'foreign_acc_name': account.foreign_acc_name
                            }
                        )
                    )
            for order, item in enumerate(account_mapped_data_inventory):
                main_obj = DefaultAccountDetermination(
                    company=company,
                    tenant=company.tenant,
                    order=order,
                    title=item.get('title', ''),
                    foreign_title=item.get('foreign_title', ''),
                    default_account_determination_type=2
                )
                bulk_info.append(main_obj)
                for account in item.get('account', []):
                    bulk_info_sub.append(
                        DefaultAccountDeterminationSub(
                            default_acc_deter=main_obj,
                            account_mapped=account,
                            account_mapped_data={
                                'id': str(account.id),
                                'acc_code': account.acc_code,
                                'acc_name': account.acc_name,
                                'foreign_acc_name': account.foreign_acc_name
                            }
                        )
                    )
            DefaultAccountDetermination.objects.filter(company=company, tenant=company.tenant).delete()
            DefaultAccountDetermination.objects.bulk_create(bulk_info)
            DefaultAccountDeterminationSub.objects.bulk_create(bulk_info_sub)
            print(f'Done for {company.title}')
        print('Done :))')
        return True


class AccountingScripts:
    @staticmethod
    def push_default_account_determination_200():
        """ Đẩy các tài khoản kế toán xác định mặc định (TT200) vào KHO - PRODUCT TYPE - PRODUCT """
        for warehouse_obj in WareHouse.objects.all():
            AccountDeterminationForWarehouseHandler.create_account_determination_for_warehouse(warehouse_obj)
        for product_type_obj in ProductType.objects.all():
            AccountDeterminationForProductTypeHandler.create_account_determination_for_product_type(product_type_obj)
        for product_obj in Product.objects.all():
            AccountDeterminationForProductHandler.create_account_determination_for_product(product_obj)
        print(f'Done :))')
        return True

    @staticmethod
    def allow_account_determination_can_change_account(account_deter_foreign_title):
        """ Cho phép thay đổi TK xác định """
        for warehouse_obj in WareHouse.objects.all():
            warehouse_obj.wh_account_deter_warehouse_mapped.filter(
                foreign_title=account_deter_foreign_title
            ).update(can_change_account=True)
        for product_type_obj in ProductType.objects.all():
            product_type_obj.prd_type_account_deter_product_type_mapped.filter(
                foreign_title=account_deter_foreign_title
            ).update(can_change_account=True)
        for product_obj in Product.objects.all():
            product_obj.prd_account_deter_product_mapped.filter(
                foreign_title=account_deter_foreign_title
            ).update(can_change_account=True)
        print(f'Done :))')
        return True

    @staticmethod
    def allow_or_disallow_all(can_change):
        """ Cho phép change tất cả | tắt tất cả: param 'can_change' """
        for warehouse_obj in WareHouse.objects.all():
            warehouse_obj.wh_account_deter_warehouse_mapped.all().update(can_change_account=can_change)
        for product_type_obj in ProductType.objects.all():
            product_type_obj.prd_type_account_deter_product_type_mapped.all().update(can_change_account=can_change)
        for product_obj in Product.objects.all():
            product_obj.prd_account_deter_product_mapped.all().update(can_change_account=can_change)
        print(f'Done :))')
        return True
