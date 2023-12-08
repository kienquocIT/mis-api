from rest_framework import serializers

from apps.core.attachments.models import Files
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.eoffice.businesstrip.models import ExpenseItemMapBusinessRequest, BusinessRequest, \
    BusinessRequestAttachmentFile

__all__ = ['BusinessRequestListSerializer', 'BusinessRequestCreateSerializer', 'BusinessRequestDetailSerializer',
           'BusinessRequestUpdateSerializer']

from apps.shared import TypeCheck, HRMsg, SYSTEM_STATUS, AbstractDetailSerializerModel, DisperseModel
from apps.shared.translations.base import AttachmentMsg, BaseMsg
from apps.shared.translations.eoffices import BusinessMsg


def handle_attach_file(user, instance, validate_data):
    if 'attachment' in validate_data and validate_data['attachment']:
        type_check = True
        if isinstance(validate_data['attachment'], list):
            type_check = TypeCheck.check_uuid_list(validate_data['attachment'])
        elif isinstance(validate_data['attachment'], str):
            type_check = TypeCheck.check_uuid(validate_data['attachment'])
        if not type_check:
            return True
        relate_app = Application.objects.get(id="87ce1662-ca9d-403f-a32e-9553714ebc6d")
        relate_app_code = 'businesstrip'
        business_request_id = str(instance.id)
        if not user.employee_current:
            raise serializers.ValidationError(
                {'User': BaseMsg.USER_NOT_MAP_EMPLOYEE}
            )
        is_check, attach_check = Files.check_media_file(
            media_file_id=validate_data['attachment'],
            media_user_id=str(user.employee_current.media_user_id)
        )
        if is_check:
            # tạo file
            files_id = Files.regis_media_file(
                relate_app, business_request_id, relate_app_code, user, media_result=attach_check
            )

            # tạo phiếu attachment
            BusinessRequestAttachmentFile.objects.create(
                business_request=instance,
                files=files_id,
                media_file=validate_data['attachment']
            )
            instance.attachment = validate_data['attachment']
            instance.save(update_fields=['attachment'])
            return validate_data

        raise serializers.ValidationError(
            {
                'attachment': AttachmentMsg.ERROR_VERIFY
            }
        )
    return True


class BusinessRequestExpenseItemListSerializer(serializers.ModelSerializer):
    expense_item_data = serializers.SerializerMethodField()
    tax_data = serializers.SerializerMethodField()

    @classmethod
    def get_expense_item_data(cls, obj):
        return {
            'id': obj.expense_item_id,
            'title': obj.expense_item.title,
            'code': obj.expense_item.code,
        } if obj.expense_item else {}

    @classmethod
    def get_tax_data(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
            'code': obj.tax.code,
            'rate': obj.tax.rate
        } if obj.tax else {}

    class Meta:
        model = ExpenseItemMapBusinessRequest
        fields = (
            'id',
            'title',
            'expense_item_data',
            'uom_txt',
            'quantity',
            'price',
            'tax_data',
            'subtotal',
        )


class ExpenseItemListUpdateSerializer(serializers.Serializer):  # noqa
    expense_item = serializers.UUIDField()
    tax = serializers.UUIDField()
    title = serializers.CharField()
    uom_txt = serializers.CharField()
    quantity = serializers.FloatField()
    price = serializers.FloatField()
    subtotal = serializers.FloatField()
    order = serializers.IntegerField()
    id = serializers.UUIDField(allow_null=True, required=False)


class BusinessRequestListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            "id": obj.employee_inherit_id,
            "first_name": obj.employee_inherit.first_name,
            "last_name": obj.employee_inherit.last_name,
            "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
        } if obj.employee_inherit else {}

    class Meta:
        model = BusinessRequest
        fields = (
            'id',
            'title',
            'employee_inherit',
            'code',
            'date_f',
            'date_t',
            'system_status',
            'destination',
            'employee_on_trip',
            'remark'
        )


class BusinessRequestCreateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()
    expense_items = ExpenseItemListUpdateSerializer(many=True)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    @classmethod
    def validate_expense_items(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': BusinessMsg.EMPTY_EXPENSE_ITEMS})
        return value

    @classmethod
    def create_expense_items(cls, instance, order_dict):
        list_create = []
        for item in order_dict:
            expense = ExpenseItemMapBusinessRequest(
                title=item['title'],
                business_request=instance,
                expense_item_id=str(item['expense_item']),
                tax_id=str(item['tax']),
                uom_txt=item['uom_txt'],
                quantity=item['quantity'],
                price=item['price'],
                subtotal=item['subtotal'],
                order=item['order'],
            )
            expense.before_save()
            list_create.append(expense)
        ExpenseItemMapBusinessRequest.objects.bulk_create(list_create)

    @decorator_run_workflow
    def create(self, validated_data):
        user = self.context.get('user', None)
        expense_list = validated_data['expense_items']
        del validated_data['expense_items']
        business_request = BusinessRequest.objects.create(**validated_data)
        self.create_expense_items(business_request, expense_list)
        handle_attach_file(user, business_request, validated_data)
        return business_request

    class Meta:
        model = BusinessRequest
        fields = (
            'title',
            'remark',
            'employee_inherit_id',
            'attachment',
            'expense_items',
            'date_created',
            'system_status',
            'departure',
            'destination',
            'employee_on_trip',
            'date_f',
            'morning_f',
            'date_t',
            'morning_t',
            'total_day',
            'pretax_amount',
            'taxes',
            'total_amount',
        )


class BusinessRequestDetailSerializer(AbstractDetailSerializerModel):
    employee_inherit = serializers.SerializerMethodField()
    expense_items = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    departure = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    employee_on_trip = serializers.SerializerMethodField()

    @classmethod
    def get_expense_items(cls, obj):
        item_list = BusinessRequestExpenseItemListSerializer(
            obj.expense_item_map_business_request.all(),
            many=True,
        ).data
        return item_list

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": str(obj.employee_inherit_id),
                "last_name": obj.employee_inherit.last_name,
                "first_name": obj.employee_inherit.first_name,
                "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
            }
        return {}

    @classmethod
    def get_attachment(cls, obj):
        if obj.attachment:
            attach = BusinessRequestAttachmentFile.objects.filter(
                delivery_sub=obj,
                media_file=obj.attachment
            )
            if attach.exists():
                attachments = []
                for item in attach:
                    files = item.files
                    attachments.append(
                        {
                            'files': {
                                "id": str(files.id),
                                "relate_app_id": str(files.relate_app_id),
                                "relate_app_code": files.relate_app_code,
                                "relate_doc_id": str(files.relate_doc_id),
                                "media_file_id": str(files.media_file_id),
                                "file_name": files.file_name,
                                "file_size": int(files.file_size),
                                "file_type": files.file_type
                            }
                        }
                    )
                return attachments
        return []

    @classmethod
    def get_departure(cls, obj):
        return {
            'id': str(obj.departure_id),
            'title': obj.departure.title
        } if obj.departure else {}

    @classmethod
    def get_destination(cls, obj):
        return {
            'id': str(obj.destination_id),
            'title': obj.destination.title
        } if obj.destination else {}

    @classmethod
    def get_employee_on_trip(cls, obj):
        employee_list = DisperseModel(app_model='hr.Employee').get_model().objects.filter(
            id__in=obj.employee_on_trip,
        )
        if employee_list.exists():
            return [{
                'id': str(item.id),
                'last_name': item.last_name,
                'first_name': item.first_name,
                'full_name': item.get_full_name()
            } for item in employee_list]
        return []

    class Meta:
        model = BusinessRequest
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'employee_inherit',
            'attachment',
            'expense_items',
            'date_created',
            'system_status',
            'departure',
            'destination',
            'employee_on_trip',
            'date_f',
            'morning_f',
            'date_t',
            'morning_t',
            'total_day',
            'pretax_amount',
            'taxes',
            'total_amount',
        )


class BusinessRequestUpdateSerializer(serializers.ModelSerializer):
    expense_items = ExpenseItemListUpdateSerializer(many=True)
    employee_inherit = serializers.UUIDField()

    @classmethod
    def validate_expense_items(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': BusinessMsg.EMPTY_EXPENSE_ITEMS})
        return value

    @classmethod
    def validate_employee_inherit(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    @classmethod
    def cover_expense_items(cls, instance, order_dict):
        list_update = []
        list_create = []
        has_item = []
        for item in order_dict:
            expense = ExpenseItemMapBusinessRequest(
                title=item['title'],
                business_request=instance,
                expense_item_id=str(item['expense_item']),
                tax_id=str(item['tax']),
                uom_txt=item['uom_txt'],
                quantity=item['quantity'],
                price=item['price'],
                subtotal=item['subtotal'],
                order=item['order'],
            )
            if 'id' in item and TypeCheck.check_uuid(item['id']):
                expense.id = item['id']
                expense.before_save()
                list_update.append(expense)
                has_item.append(str(expense.id))
            else:
                list_create.append(item)

        ExpenseItemMapBusinessRequest.objects.bulk_update(
            list_update, fields=['title', 'business_request',
                                 'expense_item_id', 'tax_id', 'uom_txt', 'quantity', 'price', 'subtotal', 'order']
        )
        # delete if expense not in list update
        ExpenseItemMapBusinessRequest.objects.exclude(id__in=has_item).delete()
        ExpenseItemMapBusinessRequest.objects.bulk_create(list_create)

    def update(self, instance, validated_data):
        user = self.context.get('user', None)
        expense_list = validated_data['expense_items']
        del validated_data['expense_items']
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        self.cover_expense_items(instance, expense_list)
        handle_attach_file(user, instance, validated_data)
        return instance

    class Meta:
        model = BusinessRequest
        fields = (
            'title',
            'code',
            'remark',
            'employee_inherit',
            'attachment',
            'expense_items',
            'date_created',
            'system_status',
            'departure',
            'destination',
            'employee_on_trip',
            'date_f',
            'morning_f',
            'date_t',
            'morning_t',
            'total_day',
            'pretax_amount',
            'taxes',
            'total_amount',
        )
