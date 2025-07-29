# Lease Order Module (apps.sales.leaseorder)

## Tổng quan

Module Lease Order (Đơn hàng cho thuê) là một thành phần quan trọng trong hệ thống ERP MIS, chuyên quản lý các giao dịch cho thuê tài sản cố định (Fixed Assets) và công cụ dụng cụ (Tools). Module này được thiết kế đặc biệt cho các doanh nghiệp có hoạt động cho thuê thiết bị, máy móc, và các tài sản khác.

### Đặc điểm nổi bật

- **Quản lý cho thuê tài sản**: Theo dõi tài sản cố định và công cụ dụng cụ được cho thuê
- **Tích hợp với Asset Management**: Liên kết chặt chẽ với module quản lý tài sản
- **Quản lý thời gian thuê**: Theo dõi thời gian bắt đầu và kết thúc thuê
- **Tính toán khấu hao**: Hỗ trợ tính toán khấu hao tài sản trong thời gian cho thuê
- **Workflow tích hợp**: Quy trình phê duyệt và xử lý đơn hàng tự động

### Chức năng chính

- **Quản lý đơn hàng thuê**: Tạo, cập nhật, theo dõi trạng thái đơn hàng
- **Quản lý tài sản cho thuê**: Theo dõi tài sản cố định và công cụ dụng cụ
- **Quản lý chi phí**: Chi phí thuê, chi phí khấu hao, chi phí vận hành
- **Quản lý thanh toán**: Lịch thanh toán theo kỳ, hóa đơn
- **Báo cáo cho thuê**: Báo cáo doanh thu, lợi nhuận từ hoạt động cho thuê
- **Đơn hàng định kỳ**: Hỗ trợ tạo đơn hàng thuê lặp lại

## Kiến trúc

### Models

#### 1. **LeaseOrder** (Model chính)
Model quản lý thông tin đơn hàng cho thuê:

```python
# apps/sales/leaseorder/models/leaseorder.py:115
class LeaseOrder(DataAbstractModel, BastionFieldAbstractModel, RecurrenceAbstractModel):
```

**Các trường quan trọng:**
- `opportunity`: Liên kết với Cơ hội bán hàng
- `customer`: Khách hàng thuê
- `quotation`: Báo giá liên quan
- `lease_from`: Ngày bắt đầu thuê
- `lease_to`: Ngày kết thúc thuê
- `total_product`: Tổng giá trị sản phẩm cho thuê
- `total_cost`: Tổng chi phí
- `indicator_revenue`: Chỉ số doanh thu
- `indicator_gross_profit`: Chỉ số lợi nhuận gộp
- `indicator_net_income`: Chỉ số lợi nhuận ròng
- `system_status`: Trạng thái workflow

**Phương thức quan trọng:**
- `check_change_document()`: Kiểm tra khả năng thay đổi tài liệu
- `check_reject_document()`: Kiểm tra khả năng từ chối tài liệu
- `save()`: Override để xử lý logic khi phê duyệt

#### 2. **LeaseOrderProduct**
Quản lý danh sách sản phẩm/tài sản cho thuê:

```python
# apps/sales/leaseorder/models/leaseorder.py:309
class LeaseOrderProduct(MasterDataAbstractModel):
```

**Các trường đặc biệt:**
- `asset_type`: Loại tài sản (Fixed Asset hoặc Tool)
- `offset`: Sản phẩm offset (để theo dõi tồn kho)
- `tool_data`: Thông tin công cụ dụng cụ
- `asset_data`: Thông tin tài sản cố định
- `product_quantity_time`: Số lượng thời gian thuê
- `uom_time`: Đơn vị thời gian (ngày, tháng, năm)

#### 3. **LeaseOrderProductTool & LeaseOrderProductAsset**
Models liên kết cụ thể với từng tool/asset được cho thuê:

```python
# apps/sales/leaseorder/models/leaseorder.py:421
class LeaseOrderProductTool(MasterDataAbstractModel):
# apps/sales/leaseorder/models/leaseorder.py:461
class LeaseOrderProductAsset(MasterDataAbstractModel):
```

#### 4. **LeaseOrderCost**
Quản lý chi phí và khấu hao:

```python
# apps/sales/leaseorder/models/leaseorder.py:518
class LeaseOrderCost(MasterDataAbstractModel):
```

**Các trường khấu hao:**
- `product_depreciation_price`: Giá khấu hao
- `product_depreciation_method`: Phương pháp khấu hao
- `product_depreciation_time`: Thời gian khấu hao
- `product_lease_start_date`: Ngày bắt đầu thuê
- `product_lease_end_date`: Ngày kết thúc thuê
- `depreciation_data`: Dữ liệu khấu hao chi tiết

#### 5. **LeaseOrderAppConfig**
Cấu hình cho module Lease Order:

```python
# apps/sales/leaseorder/models/leaseorder.py:12
class LeaseOrderAppConfig(MasterDataAbstractModel):
```

**Cấu hình quan trọng:**
- `asset_type`: Loại tài sản mặc định
- `asset_group_manage`: Nhóm quản lý tài sản
- `asset_group_using`: Nhóm sử dụng tài sản
- `tool_type`: Loại công cụ mặc định
- `tool_group_manage`: Nhóm quản lý công cụ
- `tool_group_using`: Nhóm sử dụng công cụ

### API Endpoints

Base URL: `/api/leaseorder/`

#### 1. **Đơn hàng thuê**
- `GET /list` - Danh sách đơn hàng thuê
- `POST /list` - Tạo đơn hàng thuê mới
- `GET /{id}` - Chi tiết đơn hàng thuê
- `PUT /{id}` - Cập nhật đơn hàng thuê

#### 2. **Cấu hình**
- `GET /config` - Lấy cấu hình lease order
- `PUT /config` - Cập nhật cấu hình

#### 3. **Endpoints khác**
- `GET /lease-order-recurrence/list` - Danh sách đơn hàng thuê định kỳ
- `GET /dropdown/list` - Danh sách dropdown

### Views

Các view class sử dụng kế thừa từ shared mixins:

```python
# apps/sales/leaseorder/views.py
class LeaseOrderList(BaseListMixin, BaseCreateMixin)
class LeaseOrderDetail(BaseRetrieveMixin, BaseUpdateMixin)
class LeaseOrderConfigDetail(BaseRetrieveMixin, BaseUpdateMixin)
class LORecurrenceList(BaseListMixin, BaseCreateMixin)
```

### Serializers

Module sử dụng pattern nhiều serializers:
- `LeaseOrderListSerializer`: Hiển thị danh sách
- `LeaseOrderCreateSerializer`: Tạo mới
- `LeaseOrderUpdateSerializer`: Cập nhật
- `LeaseOrderDetailSerializer`: Hiển thị chi tiết
- `LeaseOrderMinimalListSerializer`: Danh sách tối giản
- `LORecurrenceListSerializer`: Danh sách định kỳ

### Business Logic

#### 1. **LOHandler** (apps/sales/leaseorder/utils/logical.py)
- `push_opportunity_log()`: Ghi log hoạt động vào Opportunity
- `push_diagram()`: Cập nhật diagram document

#### 2. **LOFinishHandler** (apps/sales/leaseorder/utils/logical_finish.py)
Xử lý logic khi đơn hàng được phê duyệt:
- `push_product_info()`: Cập nhật thông tin tồn kho (cho offset products)
- `update_asset_status()`: Cập nhật trạng thái tài sản (status = 1: đang cho thuê)
- `push_to_report_revenue()`: Cập nhật báo cáo doanh thu
- `push_to_report_customer()`: Cập nhật báo cáo khách hàng
- `push_to_report_lease()`: Cập nhật báo cáo cho thuê đặc biệt
- `push_final_acceptance_lo()`: Tạo nghiệm thu
- `update_recurrence_task()`: Xử lý đơn hàng định kỳ

#### 3. **DocumentChangeHandler**
Xử lý logic khi có yêu cầu thay đổi đơn hàng (giống như Sale Order)

## Workflow Integration

Module tích hợp với hệ thống workflow của Bflow:
- Kế thừa từ `DataAbstractModel` để có các trường workflow
- Sử dụng `system_status` để theo dõi trạng thái
- Tự động trigger các action khi chuyển trạng thái

## Quan hệ với các module khác

### 1. **Asset Management**
- Liên kết với Fixed Asset và Instrument Tool
- Cập nhật trạng thái tài sản khi cho thuê
- Theo dõi lịch sử cho thuê của từng tài sản

### 2. **Quotation (Báo giá)**
- Đơn hàng thuê có thể được tạo từ báo giá
- Kế thừa thông tin sản phẩm, giá từ báo giá

### 3. **Opportunity (Cơ hội)**
- Liên kết với cơ hội bán hàng
- Cập nhật trạng thái cơ hội khi đơn hàng hoàn thành

### 4. **Inventory (Kho)**
- Cập nhật số lượng cho offset products
- Theo dõi tồn kho sản phẩm liên quan

### 5. **Reports (Báo cáo)**
- Cập nhật báo cáo doanh thu cho thuê
- Cập nhật báo cáo khách hàng
- Báo cáo đặc biệt cho hoạt động cho thuê (ReportLease)

### 6. **Accounting (Kế toán)**
- Tạo hóa đơn cho thuê
- Quản lý công nợ phải thu từ hoạt động cho thuê

## Đặc điểm riêng biệt

### 1. **Quản lý tài sản**
- Phân biệt Fixed Asset và Tool
- Theo dõi trạng thái tài sản (available/leased)
- Liên kết trực tiếp với từng tài sản cụ thể

### 2. **Tính toán khấu hao**
- Hỗ trợ nhiều phương pháp khấu hao
- Tính toán khấu hao theo thời gian thuê
- Lưu trữ lịch sử khấu hao

### 3. **Quản lý thời gian**
- Theo dõi thời gian thuê (lease_from, lease_to)
- Tính toán doanh thu theo thời gian
- Hỗ trợ đơn vị thời gian linh hoạt

### 4. **Báo cáo chuyên biệt**
- ReportLease: Báo cáo riêng cho hoạt động cho thuê
- Theo dõi hiệu quả sử dụng tài sản
- Phân tích lợi nhuận theo tài sản

## Security & Permissions

Module sử dụng decorator `@mask_view` để kiểm soát quyền truy cập:
- `label_code='leaseorder'`
- `model_code='leaseorder'`
- Các permission: `view`, `create`, `edit`

## Development Guidelines

### 1. **Khi thêm tài sản mới để cho thuê**
- Kiểm tra trạng thái tài sản (phải available)
- Cập nhật asset_data hoặc tool_data
- Đảm bảo liên kết đúng với Asset/Tool model

### 2. **Khi tính toán khấu hao**
- Xác định phương pháp khấu hao phù hợp
- Tính toán dựa trên thời gian thuê thực tế
- Lưu trữ chi tiết trong depreciation_data

### 3. **Khi tích hợp báo cáo**
- Sử dụng ReportLease cho báo cáo cho thuê
- Cập nhật trạng thái tài sản kịp thời
- Đảm bảo tính chính xác của các chỉ số

## Testing

### Unit Tests
```bash
python manage.py test apps.sales.leaseorder.tests
```

### Test Cases quan trọng
1. Tạo đơn hàng thuê với nhiều tài sản
2. Cập nhật trạng thái tài sản khi cho thuê
3. Tính toán khấu hao chính xác
4. Xử lý đơn hàng thuê định kỳ
5. Kiểm tra conflict khi thuê tài sản đã được thuê

## Troubleshooting

### 1. **Lỗi khi tạo đơn hàng thuê**
- Kiểm tra trạng thái tài sản
- Kiểm tra cấu hình LeaseOrderAppConfig
- Xác minh quyền user

### 2. **Lỗi tính toán khấu hao**
- Kiểm tra depreciation method configuration
- Xác minh thời gian thuê hợp lệ
- Review depreciation_data structure

### 3. **Lỗi cập nhật trạng thái tài sản**
- Kiểm tra liên kết với Asset/Tool
- Xác minh workflow status
- Review transaction logs

## Maintenance

### Regular Tasks
1. Kiểm tra tài sản quá hạn thuê
2. Cập nhật trạng thái tài sản định kỳ
3. Archive đơn hàng thuê cũ
4. Optimize báo cáo cho thuê

### Database Optimization
- Index on: `customer_id`, `lease_from`, `lease_to`
- Composite index: `(tenant_id, company_id, system_status)`
- Index on asset/tool foreign keys

## Configuration

### LeaseOrderAppConfig
Cấu hình cho từng company:
- Asset types và classifications
- Tool types và classifications
- Group permissions cho quản lý và sử dụng
- Default values cho lease orders

## Change Log

### Version 1.0
- Initial implementation
- Basic lease order management
- Asset/Tool integration

### Recent Updates (based on migrations)
- Added depreciation calculation
- Added asset group management
- Added attachment support
- Performance optimizations
- Added offset product support

## Best Practices

1. **Luôn kiểm tra trạng thái tài sản** trước khi cho thuê
2. **Cập nhật đúng thời điểm** khi kết thúc thuê
3. **Backup depreciation data** định kỳ
4. **Monitor asset utilization** để tối ưu hiệu quả
5. **Validate time periods** để tránh conflict

## Contact & Support

- **Module Owner**: Sales & Asset Management Team
- **Technical Lead**: Enterprise Software Architect
- **Documentation**: Updated on 2025-07-29

For issues or questions, please contact the development team or create an issue in the project repository.