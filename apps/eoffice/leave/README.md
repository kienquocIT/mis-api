# Ứng dụng Quản lý Nghỉ phép (Leave Management)

## Tổng quan
quản lý toàn bộ quy trình nghỉ phép của nhân viên, bao gồm cấu hình loại nghỉ phép, quản lý số dư phép năm, 
đăng ký nghỉ phép và theo dõi lịch sử sử dụng.

## Cấu trúc thư mục

```
apps/eoffice/leave/
├── __init__.py
├── admin.py                 # Cấu hình Django admin
├── apps.py                  # Cấu hình ứng dụng Django
├── filters.py               # Bộ lọc cho API
├── leave_util.py            # Tiện ích hỗ trợ
├── mixins.py               # Các mixin class
├── tasks.py                # Celery tasks
├── tests.py                # Unit tests
├── urls.py                 # Định tuyến URL
├── models/                 # Các model dữ liệu
│   ├── __init__.py
│   ├── config.py           # Models cấu hình nghỉ phép
│   └── leave_request.py    # Models đơn nghỉ phép
├── serializers/            # Django REST Framework serializers
│   ├── __init__.py
│   ├── config.py           # Serializers cho cấu hình
│   └── leave_request.py    # Serializers cho đơn nghỉ phép
└── views/                  # API Views
    ├── __init__.py
    ├── config.py           # Views cấu hình nghỉ phép
    └── leave_request.py    # Views đơn nghỉ phép
```

## Models Chính

### 1. Cấu hình nghỉ phép (models/config.py)

#### LeaveConfig
- Cấu hình nghỉ phép cho từng công ty
- Quan hệ OneToOne với Company

#### LeaveType
- Các loại nghỉ phép (phép năm, ốm đau, thai sản, v.v.)
- Thuộc tính:
  - `paid_by`: Ai trả lương (1=Công ty, 2=BHXH, 3=Không lương)
  - `balance_control`: Có quản lý số dư hay không
  - `is_check_expiration`: Kiểm tra hết hạn
  - `no_of_paid`: Số ngày được hưởng
  - `prev_year`: Số tháng được chuyển sang năm sau

#### WorkingCalendarConfig
- Cấu hình lịch làm việc theo tuần
- Lưu trữ JSON thời gian làm việc từng ngày

#### WorkingYearConfig & WorkingHolidayConfig
- Cấu hình năm làm việc và ngày lễ

### 2. Đơn nghỉ phép (models/leave_request.py)

#### LeaveRequest
- Đơn xin nghỉ phép chính
- Thuộc tính quan trọng:
  - `detail_data`: JSON chứa chi tiết các ngày nghỉ
  - `total`: Tổng số ngày nghỉ
  - `system_status`: Trạng thái phê duyệt

#### LeaveRequestDateListRegister
- Chi tiết từng ngày nghỉ trong đơn
- Lưu thông tin ca sáng/chiều cho mỗi ngày

#### LeaveAvailable
- Số dư phép năm của nhân viên
- Thuộc tính:
  - `total`: Tổng số ngày được phép
  - `used`: Số ngày đã sử dụng
  - `available`: Số ngày còn lại
  - `check_balance`: Có kiểm soát số dư không

#### LeaveAvailableHistory
- Lịch sử thay đổi số dư phép năm
- Ghi lại mọi thao tác tăng/giảm số dư

## API Endpoints

### Cấu hình nghỉ phép
- `GET/PUT /config` - Xem/Cập nhật cấu hình nghỉ phép
- `POST /leave-type/create` - Tạo loại nghỉ phép mới
- `PUT/DELETE /leave-type/detail/<id>` - Cập nhật/Xóa loại nghỉ phép
- `GET/PUT /working-calendar/config` - Cấu hình lịch làm việc
- `POST /working-calendar/year` - Thêm năm làm việc
- `POST /working-calendar/holiday` - Thêm ngày lễ

### Đơn nghỉ phép
- `GET/POST /request` - Danh sách/Tạo đơn nghỉ phép
- `GET /calendar` - Xem lịch nghỉ phép
- `GET/PUT/DELETE /request/detail/<id>` - Chi tiết/Cập nhật/Xóa đơn

### Số dư phép năm
- `GET /available/list` - Danh sách số dư phép
- `GET /available/dd-list` - Dropdown danh sách số dư
- `PUT /available/edit/<id>` - Chỉnh sửa số dư phép
- `GET /available/history/<employee_id>` - Lịch sử thay đổi số dư

## Logic nghiệp vụ quan trọng

### 1. Tạo đơn nghỉ phép
- Kiểm tra số dư phép có đủ không (`LeaveRequestCreateSerializer.validate_detail_data`)
- Kiểm tra ngày hết hạn phép năm
- Tự động trừ số dư khi đơn được phê duyệt (`LeaveRequest.minus_available`)

### 2. Quản lý số dư phép
- Tự động tạo LeaveAvailable khi tạo LeaveType có `balance_control=True`
- Cập nhật số dư khi đơn nghỉ phép được phê duyệt (system_status=3)
- Ghi lại lịch sử mọi thay đổi số dư

### 3. Workflow phê duyệt
- Sử dụng decorator `@decorator_run_workflow` để tích hợp với hệ thống workflow
- Gửi email thông báo khi đơn được phê duyệt (`LeaveRequest.call_send_mail`)

## Lưu ý kỹ thuật

### Cấu hình quan trọng
- Loại phép đặc biệt: FF (Ốm gia đình), MY (Thai sản), MC (Ốm bản thân) có logic riêng
- Phép năm (AN) có ràng buộc tối thiểu 12 ngày
- Phép năm trước (ANPY) có logic tính ngày hết hạn đặc biệt

### Tích hợp với các module khác
- `apps.core.mailer`: Gửi email thông báo
- `apps.core.workflow`: Quy trình phê duyệt
- `apps.core.hr.Employee`: Quản lý nhân viên
- `apps.company.Company`: Thông tin công ty

## Testing
Chạy unit tests:
```bash
python manage.py test apps.eoffice.leave
```

## Migrations
Có 10 migration files, bao gồm:
- Migration ban đầu tạo các bảng
- Thêm các trường mới như `next_node_collab`, `document_change_order`
- Cập nhật các ràng buộc và index

---
*Tài liệu này được tạo tự động bởi Claude Code. Cập nhật lần cuối: 2025-07-29*