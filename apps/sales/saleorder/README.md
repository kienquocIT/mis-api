# Sales Order Module (apps.sales.saleorder)

## Tổng quan

Module Sales Order (Đơn hàng) là một thành phần quan trọng trong hệ thống ERP MIS, quản lý toàn bộ quy trình xử lý đơn hàng từ khách hàng. Module này tích hợp chặt chẽ với các module khác như Quotation (Báo giá), Opportunity (Cơ hội), Inventory (Kho), và các module báo cáo.

### Chức năng chính

- **Quản lý đơn hàng**: Tạo, cập nhật, theo dõi trạng thái đơn hàng
- **Quản lý sản phẩm**: Danh sách sản phẩm, giá, thuế, chiết khấu
- **Quản lý chi phí**: Chi phí sản phẩm, chi phí vận hành
- **Quản lý thanh toán**: Lịch thanh toán, hóa đơn
- **Chỉ số hiệu suất**: Doanh thu, lợi nhuận gộp, lợi nhuận ròng
- **Tích hợp workflow**: Hỗ trợ quy trình phê duyệt
- **Đơn hàng định kỳ**: Hỗ trợ tạo đơn hàng lặp lại

## Kiến trúc

### Models

#### 1. **SaleOrder** (Model chính)
Model quản lý thông tin đơn hàng:

```python
# apps/sales/saleorder/models/saleorder.py:93
class SaleOrder(DataAbstractModel, BastionFieldAbstractModel, RecurrenceAbstractModel):
```

**Các trường quan trọng:**
- `opportunity`: Liên kết với Cơ hội bán hàng
- `customer`: Khách hàng
- `quotation`: Báo giá liên quan
- `payment_term`: Điều khoản thanh toán
- `total_product`: Tổng giá trị sản phẩm
- `total_cost`: Tổng chi phí
- `total_expense`: Tổng chi phí vận hành
- `indicator_revenue`: Chỉ số doanh thu
- `indicator_gross_profit`: Chỉ số lợi nhuận gộp
- `indicator_net_income`: Chỉ số lợi nhuận ròng
- `delivery_status`: Trạng thái giao hàng
- `system_status`: Trạng thái workflow

**Phương thức quan trọng:**
- `check_change_document()`: Kiểm tra khả năng thay đổi tài liệu
- `check_reject_document()`: Kiểm tra khả năng từ chối tài liệu
- `save()`: Override để xử lý logic khi phê duyệt

#### 2. **SaleOrderProduct**
Quản lý danh sách sản phẩm trong đơn hàng:

```python
# apps/sales/saleorder/models/saleorder.py:305
class SaleOrderProduct(MasterDataAbstractModel):
```

**Các trường:**
- `product`: Sản phẩm
- `product_quantity`: Số lượng
- `product_unit_price`: Đơn giá
- `product_discount_value`: Giá trị chiết khấu
- `product_tax_value`: Thuế
- `is_promotion`: Sản phẩm khuyến mãi
- `is_shipping`: Phí vận chuyển

#### 3. **SaleOrderCost**
Quản lý chi phí sản xuất/mua hàng:

```python
# apps/sales/saleorder/models/saleorder.py:413
class SaleOrderCost(MasterDataAbstractModel):
```

#### 4. **SaleOrderExpense**
Quản lý chi phí vận hành:

```python
# apps/sales/saleorder/models/saleorder.py:486
class SaleOrderExpense(MasterDataAbstractModel):
```

#### 5. **SaleOrderPaymentStage**
Quản lý lịch thanh toán:

```python
# apps/sales/saleorder/models/saleorder.py:567
class SaleOrderPaymentStage(MasterDataAbstractModel):
```

#### 6. **SaleOrderIndicatorConfig & SaleOrderIndicator**
Quản lý cấu hình và giá trị các chỉ số hiệu suất:

```python
# apps/sales/saleorder/models/indicator.py
```

### API Endpoints

Base URL: `/api/saleorder/`

#### 1. **Đơn hàng**
- `GET /list` - Danh sách đơn hàng
- `POST /list` - Tạo đơn hàng mới
- `GET /{id}` - Chi tiết đơn hàng
- `PUT /{id}` - Cập nhật đơn hàng

#### 2. **Cấu hình**
- `GET /config` - Lấy cấu hình đơn hàng
- `PUT /config` - Cập nhật cấu hình

#### 3. **Chỉ số**
- `GET /indicators` - Danh sách chỉ số
- `POST /indicators` - Tạo chỉ số mới
- `GET /indicator/{id}` - Chi tiết chỉ số
- `PUT /indicator/{id}` - Cập nhật chỉ số

#### 4. **Endpoints khác**
- `GET /saleorder-expense-list/lists` - Danh sách chi phí
- `GET /product/list/{id}` - Danh sách sản phẩm của đơn hàng
- `GET /purchasing-staff/list` - Danh sách nhân viên mua hàng
- `GET /sale-order-product-wo/list` - Sản phẩm cho Work Order
- `GET /sale-order-recurrence/list` - Danh sách đơn hàng định kỳ
- `GET /dropdown/list` - Danh sách dropdown

### Views

Các view class sử dụng kế thừa từ shared mixins:

```python
# apps/sales/saleorder/views.py
class SaleOrderList(BaseListMixin, BaseCreateMixin)
class SaleOrderDetail(BaseRetrieveMixin, BaseUpdateMixin)
```

### Serializers

Module sử dụng pattern nhiều serializers cho các mục đích khác nhau:
- `SaleOrderListSerializer`: Hiển thị danh sách
- `SaleOrderCreateSerializer`: Tạo mới
- `SaleOrderUpdateSerializer`: Cập nhật
- `SaleOrderDetailSerializer`: Hiển thị chi tiết

### Business Logic

#### 1. **SOHandler** (apps/sales/saleorder/utils/logical.py)
- `push_opportunity_log()`: Ghi log hoạt động vào Opportunity
- `push_diagram()`: Cập nhật diagram document

#### 2. **SOFinishHandler** (apps/sales/saleorder/utils/logical_finish.py)
Xử lý logic khi đơn hàng được phê duyệt:
- `push_product_info()`: Cập nhật thông tin tồn kho
- `update_opportunity()`: Cập nhật trạng thái cơ hội
- `push_to_customer_activity()`: Ghi log hoạt động khách hàng
- `push_to_report_*()`: Cập nhật các báo cáo
- `push_final_acceptance_so()`: Tạo nghiệm thu
- `push_to_payment_plan()`: Tạo kế hoạch thanh toán
- `update_recurrence_task()`: Xử lý đơn hàng định kỳ

#### 3. **DocumentChangeHandler**
Xử lý logic khi có yêu cầu thay đổi đơn hàng

## Workflow Integration

Module tích hợp với hệ thống workflow của Bflow:
- Kế thừa từ `DataAbstractModel` để có các trường workflow
- Sử dụng `system_status` để theo dõi trạng thái
- Tự động trigger các action khi chuyển trạng thái

## Quan hệ với các module khác

### 1. **Quotation (Báo giá)**
- Đơn hàng có thể được tạo từ báo giá
- Kế thừa thông tin sản phẩm, giá từ báo giá

### 2. **Opportunity (Cơ hội)**
- Liên kết với cơ hội bán hàng
- Cập nhật trạng thái cơ hội khi đơn hàng hoàn thành

### 3. **Inventory (Kho)**
- Cập nhật số lượng chờ giao hàng
- Tạo phiếu xuất kho khi giao hàng

### 4. **Purchase (Mua hàng)**
- Tạo yêu cầu mua hàng từ đơn hàng
- Theo dõi số lượng đã mua

### 5. **Accounting (Kế toán)**
- Tạo hóa đơn bán hàng
- Quản lý công nợ phải thu

### 6. **Reports (Báo cáo)**
- Cập nhật báo cáo doanh thu
- Cập nhật báo cáo sản phẩm
- Cập nhật báo cáo khách hàng
- Cập nhật báo cáo dòng tiền

## Chỉ số hiệu suất (KPIs)

Module hỗ trợ tính toán các chỉ số:

1. **Revenue (IN0001)**: Doanh thu
2. **Total cost (IN0002)**: Tổng chi phí
3. **Gross profit (IN0003)**: Lợi nhuận gộp = Doanh thu - Chi phí
4. **Operating expense (IN0004)**: Chi phí vận hành
5. **Other expenses (IN0005)**: Chi phí khác
6. **Net income (IN0006)**: Lợi nhuận ròng = Lợi nhuận gộp - Chi phí vận hành - Chi phí khác

## Security & Permissions

Module sử dụng decorator `@mask_view` để kiểm soát quyền truy cập:
- `label_code='saleorder'`
- `model_code='saleorder'`
- Các permission: `view`, `create`, `edit`

## Development Guidelines

### 1. **Khi thêm trường mới vào SaleOrder**
- Tạo migration
- Cập nhật serializers tương ứng
- Xem xét ảnh hưởng đến logic finish

### 2. **Khi thêm logic business mới**
- Đặt trong utils/logical.py hoặc logical_finish.py
- Đảm bảo xử lý transaction properly
- Cập nhật documentation

### 3. **Khi tích hợp module mới**
- Import và sử dụng trong save() method
- Xử lý rollback khi có lỗi
- Test kỹ các case edge

## Testing

### Unit Tests
```bash
python manage.py test apps.sales.saleorder.tests
```

### Test Cases quan trọng
1. Tạo đơn hàng từ báo giá
2. Cập nhật trạng thái workflow
3. Tính toán chỉ số hiệu suất
4. Xử lý đơn hàng định kỳ

## Troubleshooting

### 1. **Lỗi khi tạo đơn hàng**
- Kiểm tra quyền user
- Kiểm tra dữ liệu required fields
- Kiểm tra workflow configuration

### 2. **Lỗi tính toán chỉ số**
- Kiểm tra formula configuration
- Kiểm tra data integrity
- Review logs để debug

### 3. **Lỗi tích hợp**
- Kiểm tra related object existence
- Kiểm tra transaction isolation
- Review celery logs nếu async

## Maintenance

### Regular Tasks
1. Clean up orphaned records
2. Archive old completed orders
3. Optimize database indexes
4. Monitor performance metrics

### Database Optimization
- Index on: `customer_id`, `opportunity_id`, `system_status`
- Composite index: `(tenant_id, company_id, system_status)`
- Regular VACUUM on PostgreSQL

## Change Log

### Version 1.0
- Initial implementation
- Basic CRUD operations
- Workflow integration

### Recent Updates (based on migrations)
- Added delivery status tracking
- Added payment stage management
- Added recurring order support
- Added attachment support
- Performance optimizations

## Contact & Support

- **Module Owner**: Sales Team
- **Technical Lead**: Enterprise Software Architect
- **Documentation**: Updated on 2025-07-29

For issues or questions, please contact the development team or create an issue in the project repository.