from random import random, shuffle, randint
from unidecode import unidecode
from typing import Union
from uuid import UUID

import requests
from django.urls import reverse
from django.db import connection


class RandomNameVietnamese:
    first_name_storage_male = [
        "Anh", "An", "Bảo", "Bình", "Cường", "Chí", "Chiến", "Chung", "Danh", "Đạt", "Đức", "Dũng",
        "Giang", "Hải", "Hiệp", "Hoàng", "Hùng", "Huy", "Khải", "Khánh", "Khôi", "Khương", "Kiên",
        "Khoa", "Khuê", "Khúc", "Khương", "Lâm", "Lân", "Lập", "Lộc", "Long", "Minh", "Nam", "Nghĩa",
        "Nhan", "Nhân", "Nhu", "Nhựt", "Ninh", "Phát", "Phong", "Phú", "Phúc", "Phi", "Phiên", "Quân",
        "Quang", "Quốc", "Sơn", "Sang", "Sĩ", "Tài", "Tân", "Tạo", "Thái", "Thắng", "Thành", "Thiên",
        "Thuận", "Tiến", "Tín", "Tô", "Tùng", "Tường", "Tuyến", "Việt", "Vinh", "Vũ", "Xuân", "Yến",
        "Tuấn", "Nhật", "Đăng", "Đức", "Đại", "Điệp", "Đình", "Đoàn", "Đông", "Đức", "Đại", "Đăng",
        "Đại", "Đạt", "Đình", "Đôn", "Đức", "Đức", "Đăng", "Định", "Đồng", "Đức", "Đức", "Gia",
        "Hiếu", "Hoài", "Hòa", "Hưng", "Huy", "Khai", "Khang", "Khánh", "Khải", "Kiên"
    ]
    first_name_storage_female = [
        'Á', 'Ân', 'Ý', 'An', 'Bích', 'Băng', 'Bảo', 'Bạch', 'Bình', 'Bửu', 'Cát', 'Cẩm', 'Chi', 'Châu', 'Chu', 'Cúc',
        'Cúc', 'Cường', 'Cầm', 'Cẩm', 'Dung', 'Di', 'Duyên', 'Dạ', 'Dương', 'Dũng', 'Dư', 'Dạ', 'Dễ', 'Dỹ', 'Gia',
        'Giang', 'Giáng', 'Giao', 'Hoa', 'Huệ', 'Hiền', 'Hạ', 'Hải', 'Hạnh', 'Hường', 'Hằng', 'Hải', 'Hạt', 'Hợp',
        'Khanh', 'Khánh', 'Khâm', 'Khê', 'Khuê', 'Kim', 'Kiều', 'Kỳ', 'Lan', 'Linh', 'Liên', 'Lâm', 'Lệ', 'Lộc', 'Lạc',
        'Lực', 'Lụa', 'Ly', 'Lâm', 'Loan', 'Linh', 'Mai', 'Mỹ', 'Mạnh', 'Minh', 'Mị', 'Mỵ', 'Nghi', 'Nghĩa', 'Nhan',
        'Nhã', 'Nhi', 'Như', 'Nhung', 'Nhuận', 'Nguyên', 'Ngân', 'Ngọc', 'Ngà', 'Ngải', 'Ngần', 'Nữ', 'Oanh', 'Ôn',
        'Phi', 'Phong', 'Phúc', 'Phương', 'Phương', 'Phước', 'Quế', 'Quyên', 'Quỳnh', 'Quân', 'Sao', 'Sơn', 'Sương',
        'Sỹ', 'Sỹ', 'Tha', 'Thi', 'Thiện', 'Thoa', 'Thoa', 'Thu', 'Thuần', 'Thục', 'Thư', 'Thương', 'Thảo', 'Thắm',
        'Thủy', 'Thục', 'Thụy', 'Thạch', 'Tiên', 'Tiểu', 'Trang', 'Triều', 'Trinh', 'Trinh', 'Trà', 'Trâm', 'Trân',
        'Trúc', 'Trầm', 'Trầm', 'Tuyết', 'Tuệ', 'Tâm', 'Tú', 'Tùng', 'Tường', 'Tường', 'Tuyền', 'Tuyền', 'Thế', 'Thỏa'
    ]
    last_name_storage_male = [
        "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương",
        "Lý", "Đào", "Đoàn", "Vương", "Trịnh", "Đinh", "Lâm", "Tạ", "Tô", "Tôn", "Thạch", "Thi", "Tống", "Từ", "Ninh"
    ]
    middle_name_storage_male = [
        "Văn", "Đức", "Thanh", "Hữu", "Huy", "Minh", "Trung", "Quang", "Duy", "Ngọc", "Gia", "Nhật", "Việt", "Tùng",
        "Đình", "Đức", "Anh", "Hải", "Tiến", "Hoàng", "Tuấn", "Thành", "Công", "Sơn", "Thái", "Nam", "Bình", "Phúc",
        "Lâm", "Nguyên"
    ]
    middle_name_storage_female = [
        "Thị", "Ngọc", "Thuỳ", "Thùy", "Phương", "Thanh", "Kim", "Hồng", "Nguyệt", "Ngọc", "Bích", "Diễm", "Thu", "Hà",
        "Yến", "Tuyết", "Ánh", "Duyên", "Hoàng", "Lệ", "Mỹ", "Thư", "Nhung", "Gia", "Anh", "Lan", "Oanh", "Tâm", "Minh",
        "Thảo"
    ]
    gender = None  # 0: male, 1: female

    @staticmethod
    def get_two_or_three():
        arr = [
            2, 3, 2, 3, 2, 3, 2, 3, 2, 3,
            2, 3, 2, 3, 2, 3, 2, 3, 2, 3,
            2, 3, 2, 3, 2, 3, 2, 3, 2, 3,
            2, 3, 2, 3, 2, 3, 2, 3, 2, 3,
            2, 3, 2, 3, 2, 3, 2, 3, 2, 3,
        ]
        return arr[randint(0, len(arr) - 1)]

    def get_gender(self):
        array_gender = [
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
            0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
        ]
        self.gender = array_gender[randint(0, len(array_gender) - 1)]
        return self.gender

    def get_first_name(self):
        if self.gender == 0:
            return self.first_name_storage_male[randint(0, len(self.first_name_storage_male) - 1)]
        return self.first_name_storage_female[randint(0, len(self.first_name_storage_female) - 1)]

    def get_last_name(self):
        return self.last_name_storage_male[randint(0, len(self.last_name_storage_male) - 1)]

    def get_middle_name(self):
        if self.gender == 0:
            return self.middle_name_storage_male[randint(0, len(self.middle_name_storage_male) - 1)]
        return self.middle_name_storage_female[randint(0, len(self.middle_name_storage_female) - 1)]

    def generate_full_name(self):
        self.get_gender()
        return f'{self.get_last_name()} {self.get_first_name()}' if self.get_two_or_three() == 2 else f'{self.get_last_name()} {self.get_middle_name()} {self.get_first_name()}'

    def generate_full_name_split(self):
        self.get_gender()
        if self.get_two_or_three() == 2:
            return self.get_first_name(), None, self.get_last_name()
        return self.get_first_name(), self.get_middle_name(), self.get_last_name()

    @staticmethod
    def username_from_full_name(full_name):
        full_name = full_name.split()
        result = ''
        for idx in range(0, len(full_name)):
            if idx == 0:
                result += full_name[idx]
            else:
                result += full_name[idx][0]
        return unidecode(result)

    def create_user_data(self, company_current):
        self.get_gender()
        first_name, middle_name, last_name = self.generate_full_name_split()
        print(first_name, ' - ', middle_name, ' - ', last_name)
        if middle_name:
            last_name += ' ' + middle_name
        username = self.username_from_full_name(first_name + ' ' + last_name)
        return {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "password": "AD111111",
            "phone": "0987654321",
            "company_current": company_current,
            "email": "username@example.com"
        }

    def create_list_user(self, length, company_current):
        username_exist = []
        result = []
        for idx in range(0, length):
            while True:
                data = self.create_user_data(company_current)
                if data['username'] not in username_exist:
                    result.append(data)
                    username_exist.append(data['username'])
                    break
        return result


class RandomDepartment:
    data_storage = [
        "Phòng Kinh doanh",
        "Phòng Marketing",
        "Phòng Tài chính",
        "Phòng Kế toán",
        "Phòng Nhân sự",
        "Phòng Kỹ thuật",
        "Phòng Nghiên cứu và Phát triển",
        "Phòng Hành chính",
        "Phòng Thiết kế",
        "Phòng Sản xuất",
        "Phòng Điều hành",
        "Phòng Dịch vụ khách hàng",
        "Phòng Hỗ trợ kỹ thuật",
        "Phòng Kiểm soát chất lượng",
        "Phòng Quản lý chất lượng",
        "Phòng An ninh",
        "Phòng Truyền thông",
        "Phòng Tuyển dụng",
        "Phòng Đào tạo",
        "Phòng Tổ chức và Hành chính",
        "Phòng Hợp đồng",
        "Phòng Thanh tra",
        "Phòng Phát triển kinh doanh",
        "Phòng Bảo vệ",
        "Phòng Sản phẩm",
        "Phòng Bán hàng",
        "Phòng Thị trường",
        "Phòng Dự án",
        "Phòng Xây dựng"
    ]

    def generate(self):
        return self.data_storage[randint(0, len(self.data_storage) - 1)]


class RandomPosition:
    position_list = [
        "Chủ tịch",
        "Phó Chủ tịch",
        "Tổng Giám đốc",
        "Phó Tổng Giám đốc",
        "Giám đốc điều hành",
        "Giám đốc kinh doanh",
        "Trưởng phòng kinh doanh",
        "Trưởng phòng marketing",
        "Trưởng phòng nhân sự",
        "Trưởng phòng tài chính",
        "Trưởng phòng sản xuất",
        "Trưởng phòng kỹ thuật",
        "Trưởng phòng nghiên cứu và phát triển",
        "Trưởng phòng dịch vụ khách hàng",
        "Trưởng phòng hỗ trợ kỹ thuật",
        "Trưởng phòng an ninh",
        "Trưởng phòng quản lý chất lượng",
        "Trưởng phòng kiểm soát chất lượng",
        "Trưởng phòng truyền thông",
        "Trưởng phòng hành chính",
        "Trưởng phòng thiết kế",
        "Giám đốc điều hành sản xuất",
        "Giám đốc tài chính",
        "Giám đốc marketing",
        "Giám đốc nghiên cứu và phát triển",
        "Giám đốc sản xuất",
        "Giám đốc kỹ thuật",
        "Giám đốc hành chính",
        "Giám đốc hỗ trợ kỹ thuật",
        "Giám đốc chất lượng",
        "Giám đốc mua hàng",
        "Giám đốc bán hàng",
        "Trưởng nhóm kinh doanh",
        "Trưởng nhóm marketing",
        "Trưởng nhóm nhân sự",
        "Trưởng nhóm tài chính",
        "Trưởng nhóm sản xuất",
        "Trưởng nhóm kỹ thuật",
        "Trưởng nhóm nghiên cứu và phát triển",
        "Trưởng nhóm dịch vụ khách hàng",
        "Trưởng nhóm hỗ trợ kỹ thuật",
        "Trưởng nhóm an ninh",
        "Trưởng nhóm quản lý chất lượng",
        "Trưởng nhóm kiểm soát chất lượng",
        "Trưởng nhóm truyền thông",
        "Trưởng nhóm hành chính",
        "Trưởng nhóm thiết kế",
        "Nhà phân phối",
        "Nhà bán hàng",
        "Chuyên viên kinh doanh",
        "Chuyên viên marketing",
        "Chuyên viên nhân sự",
        "Chuyên viên tài chính",
        "Chuyên viên sản xuất",
        "Chuyên viên kỹ thuật",
        "Chuyên viên nghiên cứu và phát triển",
        "Chuyên viên dịch vụ khách hàng",
        "Chuyên viên hỗ trợ kỹ thuật",
        "Chuyên viên an ninh",
        "Chuyên viên quản lý chất lượng",
        "Chuyên viên kiểm soát chất lượng",
        "Chuyên viên truyền thông",
        "Chuyên viên hành chính",
        "Chuyên viên thiết kế",
        "Chuyên viên mua hàng",
        "Chuyên viên bán hàng",
        "Chuyên viên chăm sóc khách hàng",
        "Chuyên viên kỹ thuật viễn thông",
        "Chuyên viên chất lượng sản phẩm",
        "Chuyên viên quản lý rủi ro",
        "Chuyên viên quản trị mạng",
        "Chuyên viên phân tích kinh doanh",
        "Chuyên viên phát triển phần mềm",
        "Chuyên viên bảo trì máy móc",
        "Chuyên viên vận hành máy móc",
        "Chuyên viên sản xuất điện tử",
        "Chuyên viên sản xuất nước giải khát",
        "Chuyên viên sản xuất thực phẩm",
        "Chuyên viên sản xuất thuốc",
        "Chuyên viên kinh doanh ngoại thương",
        "Chuyên viên xuất nhập khẩu",
        "Chuyên viên quản lý đào tạo",
        "Chuyên viên đảm bảo chất lượng",
        "Chuyên viên tư vấn kinh doanh",
        "Chuyên viên tư vấn đầu tư",
        "Chuyên viên tư vấn tài chính",
        "Chuyên viên tư vấn luật",
        "Chuyên viên phân tích tài chính",
        "Chuyên viên tư vấn bảo hiểm",
        "Chuyên viên dịch thuật",
        "Chuyên viên dịch công chứng",
        "Chuyên viên thiết kế đồ họa",
        "Chuyên viên thiết kế website",
        "Chuyên viên thiết kế phần mềm",
        "Chuyên viên thiết kế sản phẩm",
        "Chuyên viên điều hành tour",
        "Chuyên viên đặt phòng khách sạn",
        "Chuyên viên chăm sóc sức khỏe",
        "Chuyên viên chăm sóc da",
        "Chuyên viên chăm sóc tóc",
        "Chuyên viên chăm sóc móng",
        "Chuyên viên y tế",
        "Chuyên viên dược phẩm",
        "Chuyên viên xét nghiệm",
        "Chuyên viên chẩn đoán hình ảnh",
        "Chuyên viên nha khoa",
        "Chuyên viên phẫu thuật",
        "Chuyên viên khám bệnh",
        "Chuyên viên chăm sóc người già",
        "Chuyên viên chăm sóc trẻ em",
        "Chuyên viên phát triển sản phẩm",
        "Chuyên viên phân phối sản phẩm",
        "Chuyên viên quản lý dự án",
        "Chuyên viên phân tích dữ liệu",
        "Chuyên viên thiết kế mạch điện",
        "Chuyên viên thiết kế hệ thống điện",
        "Chuyên viên thiết kế hệ thống viễn thông",
        "Chuyên viên phát triển ứng dụng di động",
        "Chuyên viên bảo mật thông tin",
        "Chuyên viên quản lý cơ sở dữ liệu",
        "Chuyên viên quản lý hệ thống",
        "Chuyên viên giám sát an ninh",
        "Chuyên viên phát triển sản phẩm mới",
        "Chuyên viên định giá tài sản",
        "Chuyên viên tư vấn tài sản",
        "Chuyên viên hợp đồng",
        "Chuyên viên tài chính ngân hàng",
        "Chuyên viên kế toán",
        "Chuyên viên kế toán thuế",
        "Chuyên viên tài chính doanh nghiệp",
        "Chuyên viên tài chính cá nhân",
        "Chuyên viên chứng khoán",
        "Chuyên viên đầu tư chứng khoán",
        "Chuyên viên đầu tư tài chính",
        "Chuyên viên quản lý tài sản",
        "Chuyên viên quản lý danh mục đầu tư",
        "Chuyên viên quản lý rủi ro tài chính",
        "Chuyên viên phân tích chứng khoán",
        "Chuyên viên tư vấn định hướng nghề nghiệp",
        "Chuyên viên xử lý dữ liệu",
        "Chuyên viên quản lý sản xuất",
        "Chuyên viên phân tích thị trường",
        "Chuyên viên tư vấn sản phẩm tài chính",
        "Chuyên viên quản lý quan hệ khách hàng",
        "Chuyên viên quản lý kênh phân phối",
        "Chuyên viên kiểm soát chi phí",
        "Chuyên viên quản lý nhân sự",
        "Chuyên viên tuyển dụng",
        "Chuyên viên đào tạo",
        "Chuyên viên phát triển nhân sự",
        "Chuyên viên bảo vệ lao động",
        "Chuyên viên quản lý thu mua",
        "Chuyên viên quản lý kho",
        "Chuyên viên quản lý vận chuyển",
        "Chuyên viên sản xuất thủ công",
        "Chuyên viên quản lý chất lượng sản phẩm",
        "Chuyên viên kiểm soát sản xuất",
        "Chuyển viên phát triển bền vững",
        "Chuyên viên quản lý tài nguyên",
    ]

    def generate(self):
        return self.position_list[randint(0, len(self.position_list) - 1)]


class MockupDataDB:
    account_id_list: list[Union[UUID, str]] = []
    account_data: dict = {}
    role_id_list: list[Union[UUID, str]] = []
    role_data: dict = {}
    level_group_data: dict = {}
    group_id_list: list[Union[UUID, str]] = []
    employee_data: dict = {}

    def parse_url(self, url):
        return f'http://{self.host}:{self.port}/{url}'

    def __init__(self, host, port, tenant_id=None, company_id=None):
        self.host = host
        self.port = port
        self.tenant_id = tenant_id
        self.company_id = company_id

        self.tenant_code = 'MTS4'
        self.username = 'admin'
        self.password = '111111'
        self.login_data = {}
        self.token_access = None

    @property
    def headers(self):
        return {'Authorization': 'Bearer ' + self.token_access}

    def __call__(self, *args, **kwargs):
        id_new_tenant = self.call_new_tenant()
        print('id_new_tenant:', id_new_tenant)
        if id_new_tenant:
            login_data = self.call_login()
            print('login_data: ', login_data)
            if login_data:
                print('call_create_account: ', self.call_create_account(15))
                print('call_create_role: ', self.call_create_role(5))
                print('call_create_level_group: ', self.call_create_level_group(5))
                print('call_create_group: ', self.call_create_group())
                print('call_create_employee: ', self.call_create_employee())
        connection.close()

    def call_new_tenant(self):
        if not self.tenant_id:
            admin_first_name, admin_middle, admin_last_name = RandomNameVietnamese().generate_full_name_split()
            if admin_middle:
                admin_last_name = f'{admin_last_name} {admin_middle}'
            resp = requests.post(
                url=self.parse_url(reverse('NewTenant')),
                json={
                    'tenant_data': {
                        'title': 'Cong Ty TNHH Minh Tam Solution',
                        'code': self.tenant_code,
                        'sub_domain': self.tenant_code.lower(),
                        'representative_fullname': admin_last_name + ' ' + admin_first_name,
                        'representative_phone_number': '+84987654321',
                        'user_request_created': {
                            'id': 'c0d18110-84eb-458b-b17d-2b6a390d1e2f',
                            'full_name': 'admin',
                            'email': '',
                            'phone': None
                        },
                        'auto_create_company': True,
                        'company_quality_max': 5,
                        'plan': {}
                    },
                    'create_admin': True,
                    'create_employee': True,
                    'plan_data': [
                        {
                            'title': 'Personal',
                            'code': 'personal',
                            'quantity': 10,
                            'date_active': '2023-03-28 '
                                           '18:15:00',
                            'date_end': '2030-03-28 '
                                        '18:15:00',
                            'is_limited': True,
                            'purchase_order':
                                'PO-20203-0001'
                        }, {
                            'title': 'Sale', 'code': 'sale',
                            'quantity': None,
                            'date_active': '2023-03-28 18:15:00',
                            'date_end': '2030-03-28 18:15:00',
                            'is_limited': False,
                            'purchase_order': 'PO-20203-0001'
                        }, {
                            'title': 'HRM', 'code': 'hrm',
                            'quantity': 50,
                            'date_active': '2023-03-28 18:15:00',
                            'date_end': '2030-03-28 18:15:00',
                            'is_limited': True,
                            'purchase_order': 'PO-20203-0001'
                        }
                    ],
                    'user_data': {
                        'first_name': admin_first_name, 'last_name': admin_last_name, 'email': 'admin@mts.com.vn',
                        'phone': '+84987654321', 'username': 'admin', 'password': '111111'
                    }
                }
            )
            if resp.status_code == 200:
                self.tenant_id = resp.json()['result']['id']
                return self.tenant_id
            return None
        return self.tenant_id

    def call_login(self):
        if self.tenant_id:
            resp = requests.post(
                url=self.parse_url(reverse('AuthLogin')),
                json={'username': self.username, 'password': self.password, 'tenant_code': self.tenant_code}
            )
            if resp.status_code == 200:
                self.login_data = resp.json()['result']
                self.company_id = resp.json()['result']['company_current']['id']
                self.token_access = resp.json()['result']['token']['access_token']
                return self.login_data
        return None

    def call_create_company(self):
        if not self.company_id:
            if self.tenant_id and self.login_data:
                ...
            return None
        return self.company_id

    def call_create_account(self, length):
        for user_data in RandomNameVietnamese().create_list_user(length, company_current=self.company_id):
            resp = requests.post(
                url=self.parse_url(reverse('UserList')),
                json=user_data,
                headers=self.headers
            )
            if resp.status_code == 201:
                self.account_id_list.append(resp.json()['result']['id'])
                self.account_data[resp.json()['result']['id']] = resp.json()['result']
        return self.account_id_list

    def call_create_role(self, length):
        if self.token_access:
            for idx in range(0, length):
                while True:
                    title = RandomDepartment().generate()
                    if title not in self.role_data:
                        data = {
                            "title": title,
                            "abbreviation": RandomNameVietnamese().username_from_full_name(title),
                            "employees": []
                        }
                        resp = requests.post(
                            url=self.parse_url(reverse('RoleList')),
                            json=data,
                            headers=self.headers
                        )
                        if resp.status_code == 201:
                            self.role_id_list.append(resp.json()['result']['id'])
                            self.role_data[title] = data
                        break
            return self.role_id_list
        return None

    def call_create_level_group(self, length):
        if self.token_access:
            result = []
            for idx in range(0, length):
                first_m = RandomPosition().generate()
                second_m = RandomPosition().generate()
                result.append(
                    {
                        "level": idx,
                        "description": unidecode(first_m + ' ' + second_m),
                        "first_manager_description": first_m,
                        "second_manager_description": second_m
                    }
                )
            resp = requests.post(
                url=self.parse_url(reverse('GroupLevelList')),
                json={'group_level_data': result},
                headers=self.headers
            )
            if resp.status_code == 201:
                resp = requests.get(
                    url=self.parse_url(reverse('GroupLevelList')),
                    headers=self.headers
                )
                if resp.status_code == 200:
                    for x in resp.json()['result']:
                        self.level_group_data[x['id']] = x
                return self.level_group_data
        return None

    def call_create_group(self):
        for id_level, data_level in self.level_group_data.items():
            data = {
                "group_level": id_level,
                # "parent_n": None,
                "title": data_level['first_manager_description'],
                "code": unidecode(data_level['first_manager_description']),
                "description": "string",
                "group_employee": [],
                "first_manager": self.login_data['employee_current']['id'],
                "first_manager_title": data_level['first_manager_description'],
                # "second_manager": None,
                "second_manager_title": data_level['second_manager_description']
            }
            resp = requests.post(
                url=self.parse_url(reverse('GroupList')),
                json=data,
                headers=self.headers
            )
            if resp.status_code == 201:
                self.group_id_list.append(resp.json()['result']['id'])
        return self.group_id_list

    def call_create_employee(self):
        for idx_user, data in self.account_data.items():
            data = {
                "user": idx_user,
                "first_name": data['first_name'],
                "last_name": data['last_name'],
                "email": data['email'],
                "phone": data['phone'],
                "date_joined": "2023-03-28T19:46:44.361Z",
                "dob": "2000-03-28",
                "plan_app": [
                    {
                        "plan": "4e082324-45e2-4c27-a5aa-e16a758d5627",
                        "application": [
                            "828b785a-8f57-4a03-9f90-e0edf96560d7",
                            "4e48c863-861b-475a-aa5e-97a4ed26f294",
                        ],
                        "license_used": 1,
                        "license_quantity": 10
                    }
                ],
                "group": self.group_id_list[randint(0, len(self.group_id_list) - 1)] if len(
                    self.group_id_list
                ) > 0 else None,
                "role": [
                    self.role_id_list[randint(0, len(self.role_id_list) - 1)]
                ] if len(self.role_id_list) > 0 else []
            }
            resp = requests.post(
                url=self.parse_url(reverse('EmployeeList')),
                json=data,
                headers=self.headers,
            )
            if resp.status_code == 201:
                self.employee_data[resp.json()['result']['id']] = resp.json()['result']
        return self.employee_data
