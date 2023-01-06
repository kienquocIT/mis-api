# Management Information System API (MIS API)

---

### Platform:

- Python 3.11 LTS
- Django (Django==4.1.3)
- Django Rest Framework (djangorestframework==3.14.0) (viết tắt là DRF)
- JSON Web Token (djangorestframework-simplejwt==5.2.2)
- ...

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
4. Kế thừa từ các lớp model abstract trong apps.shared.models: BaseModel, TenantModel, TenantCoreModel, M2MModel
5. BaseModel: sử dụng cho các models dùng chung không có filter mặc định theo tenant như user, plan, country,...
6. TenantModel: Sử dụng cho các models dùng trong hệ thống ngoài thư mục apps/core có chứa filter mặc định tenant và
   mode
7. TenantCoreModel: Sử dụng cho các models nằm trong thư mục core, có chứa filter mặc định theo tenant
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

1. Sử dụng khung class view của DRF: Kế thừa từ BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin --> cos thể extends từ các class này để custom thêm
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


class CompanyList(BaseListMixin, BaseCreateMixin): # Kế thừa (extend) từ lớp mixin cơ bản
    """
    Company List:
        GET: List
        POST: Create a new
    """
    queryset = Company.object_normal.all()  # required | query hỗ trợ truy vấn dữ liệu
    serializer_list = CompanyListSerializer # required | serializer hỗ trợ phân tích dữ liệu GET danh sách
    serializer_create = CompanyCreateSerializer # required | serializer hỗ trợ tạo dữ liệu POST tạo
    serializer_detail = CompanyListSerializer # required | serializer hỗ trợ phân tích dữ liệu sau khi tạo thành công
    list_hidden_field = ['tenant_id'] # default [] | hỗ trợ filter mặc định các trường trong danh sách (xem thêm ở class mixin)
    create_hidden_field = ['tenant_id'] # default [] | hỗ trợ thêm vào hàm serializer.save(**{data_extras}) để lưu xuống DB 
    
    @swagger_auto_schema(
        operation_summary="Company list",
        operation_description="Company list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='') # hỗ trợ kiểm tra trung gian trước khi vào view
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create Company",
        operation_description="Create new Company",
        request_body=CompanyCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    
# @mask_view(login_require=True, auth_require=True, code_perm='')
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
    serializer_class = EmployeeDetailSerializer
    serializer_update = EmployeeUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Employee detail",
        operation_description="Get employee detail by ID",
    )
    def get(self, request, *args, **kwargs):
        self.serializer_class = EmployeeDetailSerializer
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
