# Management Information System API (MIS API)

---

### Platform:

- Python 3.11 LTS
- Django (Django==4.1.3)
- Django Rest Framework (djangorestframework==3.14.0) (viết tắt là DRF)
- JSON Web Token (djangorestframework-simplejwt==5.2.2)
- ...

---


### Docker Desktop for Windows
1. Hướng dẫn: https://docs.docker.com/desktop/install/windows-install/
2. Download: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
3. Sau khi cài đặt xong. Cài đặt compose: https://docs.docker.com/compose/install/#scenario-two-install-the-compose-plugin


### Cấu hình môi trường Dev
1. Python: 3.11
```text
Cài đặt python vào môi trường local của dev
Link download: 
- WinOS: https://www.python.org/ftp/python/3.11.2/python-3.11.2-amd64.exe
- MacOS: https://www.python.org/ftp/python/3.11.2/python-3.11.2-macos11.pkg
```
2. MySQL: 8.0
```text
Có 2 cách sử dụng:
1. [RECOMMEND] Sử dụng docker-compose tại {source}/builder/dev/ 
    - Cài đặt: 
        $ docker-compose up --build     # chạy command này tại thư mục {source}/builder/dev/ 
    
    - Thông tin server:
        NAME HOST DNS: 'db'
        HOST: '127.0.0.1'
        PORT: '3307'
        MYSQL_ROOT_PASSWORD: my_secret_password
        MYSQL_DATABASE: my_db
        MYSQL_USER: my_user
        MYSQL_PASSWORD: my_password
        + Dữ liệu của container này lưu tại: /c/DockerStorage/MySQLData/
        - Để truy cập vào mysql: Sử dụng hedies truy cập với (HOST, PORT, USER, PASSWORD) tương ứng (127.0.0.1, 3307, root, my_secret_password)
    
    Traceback:
        - Nếu đã chạy docker-compose build mà khởi động lại máy không kết nối source tới DB thì:
            B1: Khởi động docker
            B2: Mở git bash và thực hiện command "docker start db"
            B3: Sau đó chạy lại source 
        - Xóa thư mục chứa source SQL lỗi xóa bằng GUI Windows:
            B1: Mở git bash tại thư mục chứa source
            B2: Sử dụng lệnh rm -rf {tên folder cần xóa}
            
2. Cài đặt MySQL Server dưới local dev. 
    - Yêu cầu: MySQL 8.x
    - Tham khảo tại: https://dev.mysql.com/downloads/mysql/
    - Download tại: https://downloads.mysql.com/archives/get/p/23/file/mysql-8.0.31-winx64.zip
```
3. Rabbit: 3.9.28
```text
Có 2 cách sử dụng:
1. [RECOMMEND] Sử dụng docker-compose tại {source}/builder/dev/ 
    - Cài đặt: Nếu đã thực hiện cài đặt MySQL docker ở bước truớc thì không cần thực hiện. 
        $ docker-compose up --build     # chạy command này tại thư mục {source}/builder/dev/ 
    
    - Thông tin:
        NAME HOST DNS: 'queue'
        HOST: '127.0.0.1'
        PORT: '15673' (15672: port sử dụng để quản lý rabbit <-- không cần thiết sử dụng)
        USER: 'rabbitmq_user'
        PASSWORD: 'rabbitmq_passwd'
        
    Traceback:
        - Nếu đã chạy docker-compose build mà khởi động lại máy không kết nối source tới DB thì:
            B1: Khởi động docker
            B2: Mở git bash và thực hiện command "docker start queue"
            B3: Sau đó chạy lại source 
            
2. Cài đặt Rabbit Server dưới local dev:
    - Yêu cầu: RabbitMQ 3.9
    - Tham khảo và Download tại: https://www.rabbitmq.com/install-windows.html
```
4. Thêm các cấu hình vào local_settings để sử dụng. Copy đoạn dưới bỏ vào misapi/local_settings.py
```python
# Bật trạng thái debug khi run server source
DEBUG = True

# Bật trang API Docs
SHOW_API_DOCS = True
```
5. 

### Khởi động source code
1. Khởi chạy celery nhận và thực hiện task
```text
a. Không sử dụng và thực thi task real-time --> thay đổi cấu hình settings: CELERY_TASK_ALWAYS_EAGER = True # changed
b. Sử dụng queue:
    B1: Mở terminal (với shell path là git bash)
    B2: command: celery -A misapi worker --loglevel=INFO
        Windows: celery -A misapi worker --loglevel=INFO --pool=solo
    B3: Muốn dừng phải dùng ctrl + C (task không tự động load lại khi sửa đổi)
```   
2. Khởi chạy source code:
```text
a. Sử dụng run của pycharm + cấu hình interpreter sử dụng python local dev.
b. Sử dụng command: python manage.py runserver 8000
```
3. Vào Task Manager -> tab Startup -> Enable Docker: Để docker tự khởi động khi mở máy.
4. 


---

### Tuân thủ các quy tắc:

- RESTful API
- Authenticate với JWT (Access Token và Refresh Token)
- Coding Convention - Quy tắc code tuân thủ PEP8 và sử dụng Pylint để check.
- Mọi application đều đưa vào folder apps. Folder dùng chung mọi app là "shared"
- Sử dụng các hàm dùng chung phải thêm vào __init__ của shared - KHÔNG ĐƯỢC SỬ DỤNG IMPORT FILE CON CỦA SHARED
- VD dùng đúng: from apps.shared import mask_view ✔
- VD dùng sai: ~~from apps.shared.decorator import maskview~~

---

### Models: MySQL + ORM Django (Object Relational Mapping)

1. **Thiết kế DB luôn phải được LEADER review và duyệt trước khi được apply vào sử dụng**
2. Thiết kế models cho chức năng phải theo nguyên tắc tối ưu truy vấn và ràng buộc dữ liệu tốt
3. Luôn sử dụng UUID4 cho ID của từng bảng
4. Kế thừa từ các lớp model abstract trong apps.shared.models: MasterDataAbstractModel
5. *deleted* BaseModel: sử dụng cho các models dùng chung không có filter mặc định theo tenant như user, plan, country,...
6. TenantModel: Sử dụng cho các models dùng trong hệ thống ngoài thư mục apps/core có chứa filter mặc định tenant và
   mode
7. *deleted* TenantCoreModel: Sử dụng cho các models nằm trong thư mục core, có chứa filter mặc định theo tenant
8. M2MModel: Sử dụng cho các models Many To Many.
9. Trong từng models được kế thừa từ shared.models sẽ có các manager truy vấn dữ liệu khác nhau: objects, object_normal,
   object_global, object_private, object_team tùy theo từng yêu cầu mà sử dụng

---

### URLs: Tuân thủ quy tắc RESTful về đường dẫn điều hướng.

Mẫu: METHOD {path} (METHOD: GET, POST, PUT, DELETE | path: đường dẫn đến view)

1. Tên path luôn luôn phải trùng với tên class view mà nó sử dụng.
2. GET api/users : dùng để lấy dữ liệu về danh sách
2. POST api/users : dùng để tạo một dữ liệu mới
3. GET api/user/1 : dùng để lấy dữ liệu chi tiết theo ID - ở đây ID là 1
4. PUT api/user/1 : dùng để cập nhật dữ liệu cho 1 dữ liệu đã tạo trước đó - ở đây ID là 1
5. DELETE api/user/1 : dùng để xóa một dữ liệu đã có trong kho dữ liệu theo ID - ở đây ID là 1

```python
from django.urls import path

from apps.core.hr.views.employee import EmployeeList, EmployeeDetail

urlpatterns = [
    path('employees', EmployeeList.as_view(), name='EmployeeList'),  # GET, POST
    path("employee/<str:pk>", EmployeeDetail.as_view(), name="EmployeeDetail"),  # GET, PUT, DELETE
]
```

---

### Views: Sử dụng class view kế thừa từ mixins - sử dụng hàm của class là tên method (get, post, put, delete)

1. Sử dụng khung class view của DRF: Kế thừa từ BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin,
   BaseDestroyMixin --> cos thể extends từ các class này để custom thêm
2. Sử dụng @swagger_auto_schema trên hàm của class view để tự động generate API Docs

```python
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.hr.mixins import HRListMixin, HRCreateMixin, HRUpdateMixin, HRRetrieveMixin
from apps.core.hr.models import Employee
from apps.core.hr.serializers.employee_serializers import (
    EmployeeListSerializer, EmployeeCreateSerializer,
    EmployeeDetailSerializer, EmployeeUpdateSerializer
)

from apps.core.company.models import Company
from apps.core.company.serializers import CompanyCreateSerializer, CompanyListSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin


class CompanyList(BaseListMixin, BaseCreateMixin):  # Kế thừa (extend) từ lớp mixin cơ bản
    """
    Company List:
        GET: List
        POST: Create a new
    """
    queryset = Company.objects.all()  # required | query hỗ trợ truy vấn dữ liệu
    serializer_list = CompanyListSerializer  # required | serializer hỗ trợ phân tích dữ liệu GET danh sách
    serializer_create = CompanyCreateSerializer  # required | serializer hỗ trợ tạo dữ liệu POST tạo
    serializer_detail = CompanyListSerializer  # required | serializer hỗ trợ phân tích dữ liệu sau khi tạo thành công
    list_hidden_field = [
        'tenant_id']  # default [] | hỗ trợ filter mặc định các trường trong danh sách (xem thêm ở class mixin)
    create_hidden_field = [
        'tenant_id']  # default [] | hỗ trợ thêm vào hàm serializer.save(**{data_extras}) để lưu xuống DB 

    @swagger_auto_schema(
        operation_summary="Company list",
        operation_description="Company list",
    )
    @mask_view(login_require=True, auth_require=False)  # hỗ trợ kiểm tra trung gian trước khi vào view
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Company",
        operation_description="Create new Company",
        request_body=CompanyCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# @mask_view(login_require=True, auth_require=False)
# 1. login_require: Yêu cầu đã đăng nhập (token còn hạn sử dụng - định danh người dùng) --> Đảm bảo lúc chạy view request.user là đã xác thực
# 2. auth_require: Yêu cầu kiểm tra quyền trước khi vào view (bắt buộc login_require = True khi dùng option này)
# 3. code_perm: mã để kiểm tra quyền ==> Đang được phát triển


class EmployeeDetail(
    HRRetrieveMixin,
    HRUpdateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.select_related(
        "user",
    )
    serializer_detail = EmployeeDetailSerializer
    serializer_update = EmployeeUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Employee detail",
        operation_description="Get employee detail by ID",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update employee",
        operation_description="Update employee information by ID",
        request_body=EmployeeUpdateSerializer,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
```

---

### Các cách để sử dụng raise Exception trong Python (phương thức raise sẽ dừng process đang thực thi để trả về một lỗi)

1. Đăng nhập hết hạn

```python
from rest_framework.exceptions import PermissionDenied

raise PermissionDenied
```

2. Không có quyền truy cập

```python
from rest_framework.exceptions import AuthenticationFailed

raise AuthenticationFailed
```

3.

---

Đề nghị tuân thủ nghiêm ngặt các quy định - mọi quy định nằm ngoài rules phải được thoải thuận với team dev để đưa ra
hướng giải quyết và được ghi chú ở đay!

---

### Using environment trong môi trường sản xuất sản phẩm cho khách hàng.

1. Database:

```properties
DB_NAME='my_db'
DB_USER='my-user'
DB_PASSWORD='my-password'
DB_HOST='127.0.0.1'
DB_PORT='3306'
```

```python
# ==> USING FOR PRODUCTION WHEN SET ENVIRONMENT VARIABLE (sensitive information) <===
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'), 'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```

2. Celery:

```python
# .env
MSG_QUEUE_HOST=host_name
MSG_QUEUE_PORT=sv_port
MSG_QUEUE_API_PORT=sv_api_port
MSG_QUEUE_USER=user
MSG_QUEUE_PASSWORD=passwd
MSG_QUEUE_BROKER_VHOST=vhost
```

3. Cache

```properties
CACHE_HOST='127.0.0.1'
CACHE_PORT='11211'
CACHE_OPTION='{"no_delay": true, "ignore_exc": true, "max_pool_size": 4, "use_pooling": true}'
```

```python
import os
import json

CACHE_HOST = os.environ.get("MSG_QUEUE_HOST")
CACHE_PORT = os.environ.get("MSG_QUEUE_PORT")
CACHE_OPTION = os.environ.get("CACHE_OPTION")
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': f'{CACHE_HOST}:{CACHE_PORT}',
        'OPTIONS': json.loads(CACHE_OPTION)
    }
}
```

4.~~ 


---
# UNITTEST

Để hiểu rõ hơn về việc sử dụng Unittest trong Django REST Framework (DRF), ta có thể xem xét ví dụ sau:

Giả sử ta có một ứng dụng DRF đơn giản để quản lý danh sách sản phẩm, trong đó có một model Product và một serializer tương ứng để chuyển đổi giữa đối tượng Product và các định dạng dữ liệu như JSON. Ta muốn viết các test để đảm bảo rằng serializer hoạt động đúng và API endpoint trả về đúng dữ liệu.

Trước tiên, ta cần khai báo một số package và import các thư viện cần thiết:

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
```

Sau đó, ta có thể viết các test như sau:
```python
class ProductTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product_data = {'name': 'Product 1', 'description': 'This is product 1', 'price': 10.0}
        self.response = self.client.post('/products/', self.product_data, format='json')

    def test_create_product(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, self.product_data['name'])

    def test_get_product_list(self):
        response = self.client.get('/products/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_product(self):
        product = Product.objects.get()
        response = self.client.get('/products/{}/'.format(product.id), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_product(self):
        product = Product.objects.get()
        new_data = {'name': 'Product 1 - updated', 'description': 'This is an updated product', 'price': 20.0}
        response = self.client.put('/products/{}/'.format(product.id), new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get().name, new_data['name'])

    def test_delete_product(self):
        product = Product.objects.get()
        response = self.client.delete('/products/{}/'.format(product.id), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
```

Trong ví dụ này, ta đã tạo ra một APIClient để gửi các request HTTP đến API endpoint của ứng dụng, sau đó sử dụng các phương thức của TestCase như setUp() và assertEqual() để thực hiện các test.

Trong setUp(), ta đã tạo một đối tượng sản phẩm Product mới bằng cách gọi phương thức POST đến API endpoint /products/, và lưu lại response để kiểm tra xem sản phẩm đã được tạo thành công hay chưa.

Trong các phương thức test, ta sử dụng các phương thức khác của APIClient như `get

---
## Cách áp dụng WF cho chức năng:
#### API
```python
# serializer.py
from apps.core.workflow.tasks import decorator_run_workflow

class XCreateSerializer(serializers.ModelSerializer):
    system_status = serializers.ChoiceField(
        choices=[0, 1],
        help_text='0: draft, 1: created',
        default=0,
    )

     class Meta:
        ...
        fields = (..., "system_status")

    @decorator_run_workflow
    def create(self, validated_data):
        ...
        instance = X.objects.create(**validated_data)
        ...
        return instance

class XDetailSerializer(serializers.ModelSerializer):
    class Meta:
        ...
        fields = (..., "workflow_runtime_id")
```
```python
# views.py
from .serializers import XCreateSerializer, XDetailSerializer

class XList(BaseCreateMixin): # noqa
    serializer_create = XCreateSerializer
    serializer_detail = XDetailSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', 'employee_modified_id']

    ....

class XDetail(BaseRetrieveMixin, BaseUpdateMixin):
    serializer_detail = XDetailSerializer
    update_hidden_field = ['employee_modified_id']

```
```python
# apps\shared\constant.py
MAP_FIELD_TITLE = {
    'saledata.contact': 'fullname',
    'saledata.account': 'name',
    '{app_label}.{model name}': 'title', # trường đại diện để lấy dữ liệu hiển thị title
}

```
---
#### MEDIA CLOUD Config
<p style="font-weight: bold;color: red;">JSON trong value của .env luôn sử dunng `"`, không được sử dụng `'`.</p>

```text
# .env
MEDIA_PREFIX_SITE=prod
MEDIA_DOMAIN=http://127.0.0.1:8881/api
MEDIA_SECRET_TOKEN_API={KEY_MAP_WITH_SETTING_MEDIA_CLOUD_SV}
```
---

#### Media cloud get check file
 
UI upload file --> tới Media Cloud --> trả về {file_id} --> thêm {file_id} vào body post
--> API lấy giá trị {file_media} gọi đến MediaForceAPI.get_file_check --> kiểm tra trả về
   1. True: --> **Tạo records trong API Files để lưu trữ** và liên kết với các models khác theo M2M
   2. False: --> Trả lỗi cho người dùng 

```python
from apps.shared.media_cloud_apis import MediaForceAPI

media_file_id = "eefbf700763e49c3bbb7d7bb250dbc69"
employee_id = "5ba531cceead4220a5ebe5f01d5d1bb1"

MediaForceAPI.get_file_check(media_file_id=media_file_id, media_user_id=employee_obj.media_user_id)

# return
# (bool, result)
#   1. True: Success, False: Errors
#   2. Result of True: {
#       'id': 'eefbf700-763e-49c3-bbb7-d7bb250dbc69', 
#       'name': 'avt.gif', 
#       'descriptions': '', 
#       'date_created': '2023-07-10 10:02:18', 
#       'date_modified': '2023-07-10 10:02:18', 
#       'file_name': 'avt.gif', 
#       'file_size': 930108, 
#       'file_type': 'gif', 
#       'file_tags': '', 
#       'belong_folder': 'c4e05d24-9ae0-4a1e-9af1-111a33a431df', 
#       'api_file_id': None, 
#       'api_app_code': None, 
#       'linked_date': None, 
#       'un_linked_date': None
#       }
#   3. Result of Errors: {
#             errors: {}
#       }
```

---

#### Media check from Model Files

1. Check exist: Files.check_media_file()
2. Create new: Files.regis_media_file()
---

#### Phân Quyền
** Mọi quyền hành sẽ được gộp lại (merge) để thành quyền cao nhất nếu trùng lặp về loại quyền và khác quy mô.

I. Quyền mặc định
1. [TENANT] Đối với is_admin_tenant:
   - Công Ty: List, Detail, Create, Edit, Destroy, Overview
   - Công Ty & Người Dùng: Thêm, Xóa

2. [COMPANY] Đối với is_admin:
   - Công Ty: List, Detail, Create, Edit
   - Người dùng: List, Detail, Create, Edit, Destroy
   - Nhân viên: List, Detail, Create, Edit, Destroy

II. Quick Setup (Cấu hình nhanh)
1. Simple: Sử dụng cho nhân viên bình thường
   -  Task: List, Detail, Create, Edit, Delete | Owner
   - 
2. Administror: Sử dụng cho người quản trị
   - Workflow: List, Detail, Create, Edit, Destroy
   - 
3. HR Manager: Sử dụng cho người quản trị nhân sự
   - Vai Trò: List, Detail, Create, Edit, Delete | company
   - Phòng Ban: List, Detail, Create, Edit, Delete | company
   - 
4. Warehouse Manager: Sử dụng cho người quản trị kho bãi hàng hóa
   - Warehouse: List, Detail, Create, Edit, Delete | company
   - 
5. 

---