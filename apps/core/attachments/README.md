# Attachments app

---

Lịch sử phiên bản tài liệu (Document Revision History)
- ...
- 2023-12-27: Khởi tạo tài liệu
    ```text
    Mô tả việc sử dụng tính tổng dung lượng đã sử dụng của Company / Người dùng (employee)
    ```

---

### Thông tin kho lưu trữ
1. Ở môi trường không sử dụng Cloud Storage thì việc đường dẫn đến tập tin sẽ luôn truy cập được!
2. Ở môi trường Cloud Storage việc trả URL sẽ thông tin method get_url() của attachments.Files hoặc attachments.PublicFiles để đảm bảo việc storage trả đúng đường dẫn truy cập - tự trả Presigned URL khi storage là Private!
3. Luôn kiểm tra quyền trước khi gọi get_url() vì bước get_url() không kiểm tra bất cứ quyền gì! Tốt nhất tuỳ vào chức năng mà truyền expire (seconds) vào hàm get_url()

### Thông tin luật
1. Private: Bắt buộc sử dụng Presigned URL -> nghĩa là nó sẽ hết hạn trên đường dẫn và cấp URL khi đã vượt qua bước kiểm tra quyền!
2. Public: Được sử dụng trong chức năng và có quyền truy cập từ mọi người mà không cần kiểm tra quyền + trả lại đường dẫn chính thức tới file không thông qua Presigned URL
3. Ngoài ra có 2 trường hợp đặc biệt đó là Logo Company và Avatar IMG Employee là lưu trực tiếp tại trường của Model -> Nó thuộc phạm vi Public nhưng không lưu trữ thông qua bảng Attachments.models.* nào!

### Thông tin Lưu trữ tập tin
1. Attachments.Files: Là các tập tin thuộc phạm vi private
2. Attachments.PublicFiles: Là các tập tin chức năng liên kết nhưng hỗ trợ việc luôn công khai
3. Attachments.M2MFilesAbstractModel: Là abtract model hỗ trợ cho các bảng ManyToMany của chức năng với attachments.Files

### Ngoài ra
```text
Các bước để tạo lập 1 PublicFiles từ chức năng (chức năng sản phẩm, ...) mong muốn sau khi tạo tệp mô tả/đính kèm của nó luôn công khai

B1: Client --[upload]--> Attachments.Files (của họ)
B2: Gọi tạo/cập nhật: Kiểm tra tập tin của họ hợp lệ
B3: Tiến hành tạo/cập nhật doc chính
B4: Di chuyển file từ attachments.Files sang attachments.PublicFiles của công ty (có thể gắn tên họ là employee_created)
B5: Link attachments.PublicFiles vừa chuyển xong với doc chính.

** Luôn yêu cầu người chỉnh sửa có đủ dụng lượng lưu trữ trong dung lượng của họ trước khi tập tin được chuyển sang khu vực public của công ty.
** Các phương thức còn thiếu cho việc chuyển tập tin này sẽ được cập nhật trong phiên bản tiếp theo. 
```

--- 

### Tính dung lượng đã sử dụng của Công Ty

Tổng của:
- attachments.Files lọc theo company_id. Sử dụng file_size (bytes) để tính.
- attachments.PublicFiles lọc them company_id. Sử dụng file_size (bytes) để tính.
- company.Company::logo lấy dữ liệu trường logo và gọi tính size (mặc định trường này tối đa 2MB)
- hr.Employee::avatar_img lọc them company_id và lấy trường avatar_img để gọi tính size (mặc định trường này tối đa 2MB)

---

### Tính dung lượng đã sử dụng của Nhân viên

Tổng của:
- attachments.Files lọc theo company_id & employee_id. Sử dụng file_size (bytes) để tính.
- **[*]Không tính dung lượng avatar của người này vào dung lượng đã sử dụng của họ mà tính vào company!**
- **[*]không tính dung lượng của Public Files vào dung lượng đã sử dụng của họ mà tính vào company!**

---
