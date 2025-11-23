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


class AccountingMasterData:
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
        Tạo bộ định khoản mặc định (Default Rules).
        Cập nhật: Tách riêng Fixed Assets (Type 3).
        """
        try:
            company_obj = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return False

        CONFIG_DATA = [
            # ====================================================
            # NHÓM 0: BÁN HÀNG (SALES) - Type 0
            # ====================================================
            # --- Doanh thu ---
            ('Rev Merchandise', 'SALE_REVENUE', '', 0, 'Doanh thu bán hàng hóa', '5111',
             'Ghi nhận doanh thu bán hàng hóa (thương mại).',
             'Xuất hóa đơn bán 10 chiếc điện thoại iPhone, đơn giá 20tr/cái. Ghi Có 5111: 200tr.'),

            ('Rev Service', 'SALE_REVENUE', 'SERV', 0, 'Doanh thu dịch vụ', '5113',
             'Ghi nhận doanh thu từ việc cung cấp dịch vụ.',
             'Xuất hóa đơn phí dịch vụ tư vấn, lắp đặt, bảo trì. Ghi Có 5113: 5tr.'),

            ('Rev Finished Goods', 'SALE_REVENUE', 'FG', 0, 'Doanh thu thành phẩm', '5112',
             'Ghi nhận doanh thu bán thành phẩm do công ty tự sản xuất.',
             'Bán lô bàn ghế gỗ do xưởng mộc của cty sản xuất ra. Ghi Có 5112: 50tr.'),

            ('Rev Scrap', 'SALE_REVENUE', 'SCRAP', 0, 'Doanh thu bán phế liệu', '711',
             'Ghi nhận thu nhập từ bán phế liệu, rác thải kho.',
             'Bán thanh lý bìa carton, sắt vụn thu hồi từ kho. Ghi Có 711: 500k.'),

            # --- Giảm trừ doanh thu ---
            ('Sales Deduction', 'SALE_DEDUCTION', '', 0, 'Các khoản giảm trừ chung', '521',
             'Tài khoản tổng hợp ghi nhận các khoản làm giảm doanh thu.',
             'Giảm giá chung trên tổng giá trị đơn hàng cho đại lý cấp 1. Ghi Nợ 521.'),

            ('Sales Discount', 'SALE_DISCOUNT', '', 0, 'Chiết khấu thương mại', '5211',
             'Chiết khấu cho khách hàng do mua số lượng lớn.',
             'Khách mua đạt doanh số 1 tỷ, chiết khấu 2% trên hóa đơn. Ghi Nợ 5211: 20tr.'),

            ('Sales Return Rev', 'SALE_RETURN', '', 0, 'Hàng bán bị trả lại', '5212',
             'Ghi giảm doanh thu khi khách hàng trả lại hàng đã mua.',
             'Khách trả lại 1 chiếc điện thoại bị lỗi màn hình. Ghi Nợ 5212: 20tr.'),

            # --- Thuế ---
            ('Output VAT', 'SALE_VAT_OUT', '', 0, 'Thuế GTGT đầu ra', '33311',
             'Thuế GTGT phải nộp nhà nước khi bán hàng.',
             'Hóa đơn bán ra 100tr, thuế suất 10%. Ghi Có 33311: 10tr.'),

            ('Export Duty', 'SALE_DUTY_EXP', '', 0, 'Thuế xuất khẩu', '3333',
             'Thuế xuất khẩu phải nộp khi bán hàng ra nước ngoài.',
             'Xuất khẩu lô hàng đi Mỹ trị giá 1 tỷ, thuế XK 5%. Ghi Có 3333: 50tr.'),

            # --- Công nợ & Thanh toán ---
            ('Receivables', 'SALE_RECEIVABLE', '', 0, 'Phải thu khách hàng', '131',
             'Ghi nhận công nợ phải thu khách hàng.',
             'Bán hàng chưa thu tiền cho Công ty A. Ghi Nợ 131 (Chi tiết đối tượng Cty A).'),

            ('Payment Cash', 'PAYMENT_MEANS', 'CASH', 0, 'Thu Tiền mặt', '1111',
             'Khách hàng thanh toán bằng tiền mặt nhập quỹ.',
             'Khách lẻ mua hàng tại cửa hàng trả tiền mặt 500k. Ghi Nợ 1111: 500k.'),

            ('Payment Bank', 'PAYMENT_MEANS', 'BANK', 0, 'Thu Chuyển khoản', '1121',
             'Khách hàng thanh toán qua ngân hàng (Báo Có).',
             'Khách hàng chuyển khoản thanh toán công nợ vào Vietcombank. Ghi Nợ 1121.'),

            # --- Nghiệp vụ đặc biệt ---
            ('Uninvoiced AR', 'SALE_UNINVOICED', '', 0, 'Giao hàng chưa xuất HĐ', '13881',
             'Đã giao hàng, ghi nhận doanh thu tạm nhưng chưa xuất hóa đơn.',
             'Ngày 31/12 xuất kho giao hàng, ngày 02/01 mới xuất HĐ. Ngày 31/12 ghi Nợ 13881 / Có 511.'),

            ('Customer Deposit', 'SALE_DEPOSIT', '', 0, 'Khách hàng đặt cọc', '3387',
             'Nhận tiền đặt cọc trước của khách hàng.',
             'Khách hàng chuyển khoản cọc trước 30% giá trị hợp đồng. Ghi Có 3387.'),

            ('Underpayment', 'SALE_UNDERPAY', '', 0, 'Khách trả thiếu', '1388',
             'Xử lý số tiền lẻ khách hàng trả thiếu (giá trị nhỏ).',
             'Hóa đơn 1.000.500đ, khách chuyển khoản tròn 1.000.000đ. Treo 500đ vào Nợ 1388.'),

            ('Overpayment', 'SALE_OVERPAY', '', 0, 'Khách trả thừa', '3388',
             'Xử lý số tiền thừa khách hàng trả dư.',
             'Hóa đơn 500k, khách chuyển nhầm 600k. Treo 100k thừa vào Có 3388 để trả lại hoặc trừ lần sau.'),

            # --- Tỷ giá (Bán) ---
            ('FX Gain Realized', 'FX_REALIZED', 'GAIN', 0, 'Lãi tỷ giá thực thu', '515',
             'Chênh lệch lãi tỷ giá khi thu tiền hàng xuất khẩu.',
             'Lúc bán tỷ giá 23.000, lúc khách trả tiền tỷ giá lên 24.000. Ghi Có 515 (Lãi).'),

            ('FX Loss Realized', 'FX_REALIZED', 'LOSS', 0, 'Lỗ tỷ giá thực thu', '635',
             'Chênh lệch lỗ tỷ giá khi thu tiền hàng xuất khẩu.',
             'Lúc bán tỷ giá 24.000, lúc khách trả tiền tỷ giá xuống 23.000. Ghi Nợ 635 (Lỗ).'),

            # ====================================================
            # NHÓM 1: MUA HÀNG (PURCHASING) - Type 1
            # ====================================================
            ('Payables', 'PURCHASE_PAYABLE', '', 1, 'Phải trả người bán', '331',
             'Ghi nhận công nợ phải trả nhà cung cấp.',
             'Mua hàng chưa thanh toán của NCC Samsung. Ghi Có 331 (Đối tượng Samsung).'),

            ('Advance to Vendor', 'PURCHASE_ADVANCE', '', 1, 'Trả trước cho người bán', '331',
             'Ứng trước tiền hàng cho nhà cung cấp.',
             'Chuyển khoản tạm ứng 50% tiền hàng cho NCC trước khi giao hàng. Ghi Nợ 331.'),

            ('Input VAT', 'PURCHASE_VAT_IN', '', 1, 'Thuế GTGT được khấu trừ', '1331',
             'Thuế GTGT đầu vào trên hóa đơn mua hàng.',
             'Hóa đơn mua máy tính 22tr (đã gồm VAT). Ghi Nợ 1331: 2tr.'),

            ('GR/IR Clearing', 'PURCHASE_GR_IR', '', 1, 'Nhập hàng chưa về HĐ', '33881',
             'Tài khoản trung gian GR/IR (Goods Receipt / Invoice Receipt).',
             'Hàng về kho ngày 25 (Nợ 156/Có 33881). Hóa đơn về ngày 28 (Nợ 33881/Có 331).'),

            ('Purchase Cost', 'PURCHASE_EXPENSE', '', 1, 'Chi phí thu mua', '1562',
             'Chi phí vận chuyển, bốc xếp liên quan trực tiếp đến mua hàng.',
             'Trả tiền xe ba gác chở hàng về kho 500k. Ghi Nợ 1562 (để phân bổ cộng vào giá vốn hàng).'),

            ('Purchase Discount', 'PURCHASE_DISCOUNT', '', 1, 'Chiết khấu thanh toán', '515',
             'Được hưởng chiết khấu thanh toán do trả tiền sớm.',
             'Điều khoản thanh toán trong 5 ngày giảm 1%. Ghi nhận phần được giảm vào Có 515.'),

            ('Purchase Service', 'PURCHASE_SERVICE', '', 1, 'Dịch vụ mua ngoài', '6427',
             'Mua dịch vụ dùng ngay cho bộ phận quản lý (không nhập kho).',
             'Thanh toán tiền điện, nước, internet văn phòng. Ghi Nợ 6427 (CP Dịch vụ mua ngoài).'),

            ('FX Gain Payment', 'FX_PAYMENT', 'GAIN', 1, 'Lãi tỷ giá thanh toán', '515',
             'Lãi tỷ giá khi thanh toán tiền cho NCC nước ngoài.',
             'Lúc mua tỷ giá 24.000, lúc trả tiền tỷ giá 23.500. Ghi Có 515.'),

            ('FX Loss Payment', 'FX_PAYMENT', 'LOSS', 1, 'Lỗ tỷ giá thanh toán', '635',
             'Lỗ tỷ giá khi thanh toán tiền cho NCC nước ngoài.',
             'Lúc mua tỷ giá 23.000, lúc trả tiền tỷ giá 24.000. Ghi Nợ 635.'),

            # ====================================================
            # NHÓM 2: KHO (INVENTORY) - Type 2
            # ====================================================
            # --- Tài sản kho (Nợ 15x) ---
            ('Inv Merchandise', 'INV_ASSET', '', 2, 'Hàng hóa', '1561',
             'Giá trị hàng hóa thương mại nhập kho (TK 1561).',
             'Nhập kho 50 cái Laptop Dell để bán thương mại. Ghi Nợ 1561.'),

            ('Inv Raw Material', 'INV_ASSET', 'RAW', 2, 'Nguyên vật liệu', '152',
             'Giá trị nguyên liệu nhập kho để sản xuất.',
             'Nhập kho 5 tấn sắt để sản xuất khung bàn. Ghi Nợ 152.'),

            ('Inv Finished Goods', 'INV_ASSET', 'FG', 2, 'Thành phẩm', '1551',
             'Giá trị thành phẩm sản xuất xong nhập kho.',
             'Xưởng bàn giao 100 cái bàn hoàn chỉnh nhập kho. Ghi Nợ 1551.'),

            ('Inv Tools', 'INV_ASSET', 'TOOL', 2, 'Công cụ dụng cụ', '1531',
             'Giá trị công cụ, dụng cụ nhập kho chờ phân bổ.',
             'Nhập kho 10 cái máy khoan cầm tay. Ghi Nợ 1531.'),

            ('Inv Consignment', 'INV_ASSET', 'CONSIGN', 2, 'Hàng gửi đi bán', '157',
             'Giá trị hàng xuất kho gửi đại lý bán hộ (chưa ghi nhận giá vốn).',
             'Xuất kho 20 cái máy giặt gửi đại lý Điện Máy Xanh. Ghi Nợ 157 / Có 1561.'),

            # --- Giá vốn & Xuất kho (Có 15x) ---
            ('COGS', 'INV_COGS', '', 2, 'Giá vốn hàng bán', '632',
             'Ghi nhận giá vốn khi xuất kho bán hàng.',
             'Xuất bán 1 cái Laptop giá vốn 15tr. Ghi Nợ 632 / Có 1561.'),

            ('Return Stock', 'INV_RETURN', '', 2, 'Giá vốn hàng trả lại', '632',
             'Ghi giảm giá vốn khi nhập lại hàng khách trả (Ghi Có 632).',
             'Nhập lại kho cái Laptop khách trả. Ghi Nợ 1561 / Có 632.'),

            ('Scrap Issue', 'INV_SCRAP', '', 2, 'Xuất hủy/Phế liệu', '811',
             'Xuất kho tiêu hủy hàng hỏng hoặc mất mát.',
             'Hàng bị ngập nước hư hỏng hoàn toàn, xuất hủy. Ghi Nợ 811 / Có 1561.'),

            # --- Xuất dùng (Consumption) ---
            ('Consume Production', 'INV_CONSUME', 'PROD', 2, 'Xuất NVL cho sản xuất', '621',
             'Xuất nguyên vật liệu trực tiếp để sản xuất sản phẩm (TT200: 621).',
             'Xuất gỗ từ kho để đóng bàn. Ghi Nợ 621 / Có 152.'),

            ('Consume Dept', 'INV_CONSUME', 'DEPT', 2, 'Xuất dùng cho bộ phận', '6422',
             'Xuất CCDC/Vật liệu cho văn phòng hoặc quản lý dùng.',
             'Xuất Ram giấy A4 cho phòng Kế toán. Ghi Nợ 6422 / Có 1531.'),

            ('Consume Factory', 'INV_CONSUME', 'FACTORY', 2, 'Xuất dùng cho phân xưởng', '6272',
             'Xuất CCDC/Vật liệu cho phân xưởng dùng chung.',
             'Xuất dầu nhớt bảo dưỡng máy móc phân xưởng. Ghi Nợ 6272 / Có 152.'),

            # --- Kiểm kê & Khác ---
            ('Inv Gain', 'INV_ADJUST', 'GAIN', 2, 'Kiểm kê thừa', '3381',
             'Tài sản thừa chờ xử lý khi kiểm kê kho.',
             'Kiểm kho thấy thừa 5 cái ốc vít so với sổ sách. Ghi Nợ 152 / Có 3381.'),

            ('Inv Loss', 'INV_ADJUST', 'LOSS', 2, 'Kiểm kê thiếu', '1381',
             'Tài sản thiếu chờ xử lý khi kiểm kê kho.',
             'Kiểm kho thấy thiếu 1 bao xi măng. Ghi Nợ 1381 / Có 152.'),

            ('Revaluation Gain', 'INV_REVAL', 'GAIN', 2, 'Đánh giá lại kho', '412',
             'Chênh lệch tăng do đánh giá lại tài sản (cuối năm/góp vốn).',
             'Đánh giá lại tồn kho nguyên liệu tăng giá. Ghi Nợ 152 / Có 412.'),

            ('Transit', 'INV_TRANSIT', '', 2, 'Hàng mua đi đường', '151',
             'Hàng đã mua (nhận quyền sở hữu) nhưng cuối tháng chưa về nhập kho.',
             'Đã nhận hóa đơn, hàng đang trên tàu biển. Ghi Nợ 151 / Có 331.'),

            ('Prod Receipt Credit', 'PROD_OUTPUT', '', 2, 'Nhập kho thành phẩm', '154',
             'Tài khoản đối ứng (bên Có) khi nhập kho thành phẩm từ sản xuất.',
             'Nhập kho thành phẩm: Ghi Nợ 1551 / Có 154 (Chi phí SXKD dở dang).'),

            # ====================================================
            # NHÓM 3: TÀI SẢN CỐ ĐỊNH (FIXED ASSETS) - Type 3
            # ====================================================
            # --- Nguyên giá (Cost) ---
            ('Asset Tangible', 'ASSET_COST', 'TANGIBLE', 3, 'TSCĐ Hữu hình', '2111',
             'Nguyên giá Tài sản cố định hữu hình.',
             'Mua xe tải giao hàng trị giá 500tr. Ghi Nợ 2111: 500tr.'),

            ('Asset Intangible', 'ASSET_COST', 'INTANGIBLE', 3, 'TSCĐ Vô hình', '2131',
             'Nguyên giá Tài sản cố định vô hình.',
             'Mua bản quyền phần mềm ERP trị giá 200tr. Ghi Nợ 2131: 200tr.'),

            ('Asset Lease', 'ASSET_COST', 'LEASE', 3, 'TSCĐ Thuê tài chính', '2121',
             'Nguyên giá Tài sản cố định thuê tài chính.',
             'Nhận bàn giao dây chuyền sản xuất thuê tài chính. Ghi Nợ 2121.'),

            # --- Khấu hao lũy kế (Accumulated Depreciation) ---
            ('Depr Tangible', 'ASSET_DEPR', 'TANGIBLE', 3, 'Hao mòn TSCĐ HH', '2141',
             'Hao mòn lũy kế của Tài sản cố định hữu hình (Bên Có).',
             'Định kỳ trích khấu hao xe tải. Ghi Có 2141.'),

            ('Depr Intangible', 'ASSET_DEPR', 'INTANGIBLE', 3, 'Hao mòn TSCĐ VH', '2143',
             'Hao mòn lũy kế của Tài sản cố định vô hình (Bên Có).',
             'Định kỳ trích khấu hao phần mềm. Ghi Có 2143.'),

            ('Depr Lease', 'ASSET_DEPR', 'LEASE', 3, 'Hao mòn TSCĐ Thuê TC', '2142',
             'Hao mòn lũy kế của Tài sản cố định thuê tài chính (Bên Có).',
             'Định kỳ trích khấu hao dây chuyền thuê. Ghi Có 2142.'),

            # --- Chi phí khấu hao (Expense Account) ---
            ('Exp Depr Admin', 'ASSET_EXP', 'ADMIN', 3, 'CP Khấu hao QLDN', '6424',
             'Chi phí khấu hao tính vào bộ phận Quản lý doanh nghiệp.',
             'Khấu hao xe ô tô giám đốc, máy lạnh văn phòng. Ghi Nợ 6424.'),

            ('Exp Depr Sale', 'ASSET_EXP', 'SALE', 3, 'CP Khấu hao BH', '6414',
             'Chi phí khấu hao tính vào bộ phận Bán hàng.',
             'Khấu hao xe tải giao hàng, tủ kệ trưng bày. Ghi Nợ 6414.'),

            ('Exp Depr Prod', 'ASSET_EXP', 'PROD', 3, 'CP Khấu hao Sản xuất', '6274',
             'Chi phí khấu hao tính vào bộ phận Sản xuất chung.',
             'Khấu hao máy móc thiết bị nhà xưởng. Ghi Nợ 6274.'),

            # --- Thanh lý & XDCB ---
            ('Asset Sale Rev', 'ASSET_SALE_REV', '', 3, 'Thu nhập thanh lý', '711',
             'Thu nhập khác từ việc thanh lý, nhượng bán Tài sản cố định.',
             'Bán thanh lý xe cũ được 100 triệu đồng. Ghi Có 711.'),

            ('Asset Sale Loss', 'ASSET_SALE_LOSS', '', 3, 'Chi phí thanh lý (GTCL)', '811',
             'Giá trị còn lại của tài sản khi thanh lý, nhượng bán.',
             'Xe nguyên giá 1 tỷ, đã khấu hao 900tr. Xóa sổ giá trị còn lại 100tr vào Nợ 811.'),

            ('Asset AUC', 'ASSET_AUC', '', 3, 'XDCB dở dang', '2412',
             'Chi phí xây dựng, mua sắm tài sản chưa hoàn thành/chưa đưa vào sử dụng.',
             'Đang xây dựng nhà xưởng chưa hoàn công. Chi phí vật tư nhân công ghi Nợ 2412.'),
        ]

        with transaction.atomic():
            # Xóa dữ liệu cũ
            AccountDetermination.objects.filter(company=company_obj).delete()

            created_acc_deter_objs = {}
            bulk_subs = []

            default_criteria = {}
            default_search_rule = AccountDeterminationSub.generate_key_from_dict(default_criteria)
            default_priority = 0

            for (
                deter_fg_title, trans_key, trans_key_sub, deter_type, deter_vn_title, acc_code, deter_des, deter_exp
            ) in CONFIG_DATA:
                account = ChartOfAccounts.get_acc(company_obj, acc_code)
                if not account:
                    continue

                if trans_key not in created_acc_deter_objs:
                    acc_deter_obj = AccountDetermination.objects.create(
                        company=company_obj,
                        tenant=company_obj.tenant,
                        transaction_key=trans_key,
                        title=deter_vn_title,
                        foreign_title=deter_fg_title,
                        description=deter_des,
                        example=deter_exp,
                        account_determination_type=deter_type,
                        order=deter_type * 10,  # Sort: Sale=0, Buy=10, Inv=20, Asset=30
                    )
                    created_acc_deter_objs[trans_key] = acc_deter_obj
                else:
                    acc_deter_obj = created_acc_deter_objs[trans_key]

                bulk_subs.append(AccountDeterminationSub(
                    account_determination=acc_deter_obj,
                    transaction_key_sub=trans_key_sub,
                    description=deter_vn_title,
                    account_mapped=account,
                    account_mapped_data={
                        'id': str(account.id),
                        'acc_code': account.acc_code,
                        'acc_name': account.acc_name,
                        'foreign_acc_name': account.foreign_acc_name,
                    },
                    match_criteria=default_criteria,
                    search_rule=default_search_rule,
                    priority=default_priority
                ))

            AccountDeterminationSub.objects.bulk_create(bulk_subs)

        print(f'> Generated Account Determination for {company_obj.title}')
        return True


class AccountingRuleManager:
    """ Quản lý rule ngoại lệ và Reset hệ thống """

    @staticmethod
    def create_specific_rule(company_id, transaction_key, account_code, context_dict, modifier=''):
        try:
            company = Company.objects.get(id=company_id)
            acc_deter_obj = AccountDetermination.objects.get(company=company, transaction_key=transaction_key)
            acc_obj = ChartOfAccounts.get_acc(company, account_code)

            if not acc_obj: return False

            AccountDeterminationSub.objects.create(
                account_determination=acc_deter_obj,
                transaction_key_sub=modifier,
                description=f"Custom Rule for {context_dict}",
                account_mapped=acc_obj,
                account_mapped_data={
                    'id': str(acc_obj.id),
                    'acc_code': acc_obj.acc_code,
                    'acc_name': acc_obj.acc_name,
                    'foreign_acc_name': acc_obj.foreign_acc_name,
                },
                match_criteria=context_dict
            )
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    @staticmethod
    def delete_specific_rule(company_id, transaction_key, context_dict):
        key = AccountDeterminationSub.generate_key_from_dict(context_dict)
        AccountDeterminationSub.objects.filter(
            account_determination__company_id=company_id,
            account_determination__transaction_key=transaction_key,
            search_rule=key
        ).delete()
        return True

    @staticmethod
    def accounting_reset_default_200(company_id):
        print(f'--- START RESET ACCOUNTING FOR COMPANY ID {company_id} ---')
        AccountingMasterData.generate_account_200(company_id)
        AccountingMasterData.add_account_default_200(company_id)
        AccountingMasterData.generate_account_determination_200(company_id)
        print('--- RESET DONE :)) ---')
        return True
