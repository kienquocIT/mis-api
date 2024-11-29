### Process Instructions

---

Thành phần bao gồm:

Cấu hình:
- Stage: Hệ thống (start, end) và các stage người tạo dùng
- Application: Ứng dụng trong từng stage (Hệ thống không chứa app)
- Global App: Ứng dụng toàn cầu trong cả tiến trình - tạo phiếu cho ứng dụng đó lúc nào cũng được
- ProcessConfigurationMembers: Chứa thành viên cơ bản đầu tiên khi runtime 1 tiến trình - chưa sử dụng!

Runtime:
- Process, ProcessStage, ProcessStageApplication: Ánh xạ từ cấu hình
- ProcessMembers: Chứa thành viên của tiến trình, người dùng khởi tạo runtime sẽ là member không thể xoá
- ProcessDoc: Chứa các đăng ký doc cho ProcessStageApplication của người dùng tạo
- ProcessActivity: Lưa tất cả các nhật ký hoạt động của tiến trình

Quyền:
- Thành viên trong tiến trình có quyền xem tiến trình, tạo mọi phiếu trong tiến trình, thêm xoá thành viên.
- Thành viên trong Opp sẽ ánh xạ sang tiến trình tương ứng

---

1. Models
    - Đảm bảo Models đích tính năng kế thừa từ `DataAbstractModel` hoặc có trường `process_stage_app` (copy trường mẫu từ `DataAbstractModel`)
    - Đảm bảo tên của Process liên kết trên Model đều luôn là `process` và `process_stage_app`
    - Ví dụ model cần xử lý là `XModel`
    - Viết lại hàm `get_app_id()` trong `XModel` trả về ID của ứng dụng đó, tương ứng với ứng dụng ở `base.application`:
        ```python
        @classmethod
        def get_app_id(cls, raise_exception=True) -> str or None:
            return 'UUID4'
        ```
    - 

2. Serializers
   1. Create: 
      - Thêm khai báo trường dữ liệu vào class serializer
          ```python
          process = serializers.UUIDField(allow_null=True, default=None, required=False)
          process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)
          ```
      - Thêm vào `Meta.fields` 2 tên trường dữ liệu vừa thêm
          ```python
          class Meta:
            fields = (
                ..., 
                'process', 'process_stage_app',
            )
          ```
      - Thêm import hàm hỗ trợ của Process
          ```python
          from apps.core.process.utils import ProcessRuntimeControl  
          ```
      - Thêm hàm valid trường Process
          ```python
          @classmethod
          def validate_process(cls, attrs):
              return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None
          ```
      - Thêm hàm valid trường Process Stage App
          ```python
          @classmethod
          def validate_process_stage_app(cls, attrs):
              return ProcessRuntimeControl.get_process_stage_app(
                  stage_app_id=attrs, app_id=XModel.get_app_id()
              ) if attrs else None
          ```
      - Thêm khối xử lý `process` trong hàm `validate`
          ```python
          def validate(self, validate_data):
              ...
              # Xử lý lấy nhân viên đang tạo để kiểm tra quyền trên Process
              employee_obj = validate_data.get('employee_inherit', None)
              if not employee_obj:
                  raise serializers.ValidationError({
                      'detail': 'Need employee information to check permission to create progress ticket'
                  })
              ...
              process_obj = validate_data.get('process', None)
              process_stage_app_obj = validate_data.get('process_stage_app', None)
              opportunity_id = validate_data.get('opportunity_id', None)
              if process_obj:
                  ProcessRuntimeControl(process_obj=process_obj).validate_process(
                      process_stage_app_obj=process_stage_app_obj,
                      employee_id=employee_obj.id, 
                      opp_id=opportunity_id,
                  )
              ...
              return validate_data
          ```
      - Thêm khối xử lý `process` trong hàm `create`
          ```python
          def create(self, validated_data):
              ...
              instance = XModel.objects.create(**validated_data)
              if instance.process:
                  ProcessRuntimeControl(process_obj=instance.process).register_doc(
                      process_stage_app_obj=instance.process_stage_app,
                      app_id=instance.get_app_id(),
                      doc_id=instance.id,
                      doc_title=instance.title,
                      employee_created_id=instance.employee_created_id,
                      date_created=instance.date_created,
                  )
              ...
              return instance
          ```
      - Nếu không thể truyền employee_id vào khối kiểm tra trong validate() thì có thể sử dụng `ProcessRuntimeControl.check_permit_process_app` để kiểm tra quyền của nguười dùng đó tạo phiếu
          ```python
          # Ví dụ kiểm tra quyền trước khi tạo phiếu
          def create(self, validated_data):
              employee_created_id = validated_data.get('employee_created_id', None)
              process_stage_app_obj = validate_data.get('process_stage_app', None)
              if not employee_created_id or not process_stage_app_obj:
                  raise serializers.ValidationError({
                      'detail': 'Need employee information to check permission to create progress ticket'
                  })
              ProcessRuntimeControl.check_permit_process_app(stage_app=process_stage_app_obj, employee_id=employee_created_id)
              ...
              # các xử lý khác
              return ...
          ```
   2. Detail
      - Thêm khai báo 2 trường lấy dữ liệu vào class serializer
          ```python
          process = serializers.SerializerMethodField()
          process_stage_app = serializers.SerializerMethodField()
          ```
      - Thêm 2 hàm lấy dữ liệu vào class serializer
          ```python
          @classmethod
          def get_process(cls, obj):
              if obj.process:
                  return {
                      'id': obj.process.id,
                      'title': obj.process.title,
                      'remark': obj.process.remark,
                  }
              return {}

          @classmethod
          def get_process_stage_app(cls, obj):
              if obj.process_stage_app:
                  return {
                      'id': obj.process_stage_app.id,
                      'title': obj.process_stage_app.title,
                      'remark': obj.process_stage_app.remark,
                  }
              return {}
          ```
      - Thêm vào `Meta.fields` 2 tên trường dữ liệu vừa thêm
          ```python
          class Meta:
            fields = (
                ..., 
                'process', 'process_stage_app',
            )
          ```
3. Bật cờ `allow_process=True` trong `base.application` cho ứng dụng vừa thêm `XModel` để xuất hiện trong Process Configuration. Bằng cách sửa hoặc thêm dữ liệu cấu hình ứng dụng trong `apps.sharedapp.data.base.plan_app_sub...`