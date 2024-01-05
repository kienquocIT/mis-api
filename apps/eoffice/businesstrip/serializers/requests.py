__all__ = [
    'BusinessRequestListSerializer', 'BusinessRequestCreateSerializer', 'BusinessRequestDetailSerializer',
    'BusinessRequestUpdateSerializer',
]

from collections import Counter
from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.eoffice.businesstrip.models import (
    ExpenseItemMapBusinessRequest, BusinessRequest,
    BusinessRequestAttachmentFile, BusinessRequestEmployeeOnTrip,
)

from apps.shared import TypeCheck, HRMsg, SYSTEM_STATUS, AbstractDetailSerializerModel, DisperseModel
from apps.shared.translations.base import AttachmentMsg
from apps.shared.translations.eoffices import BusinessMsg


def handle_attach_file(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="87ce1662-ca9d-403f-a32e-9553714ebc6d")
        state = BusinessRequestAttachmentFile.resolve_change(
            result=attachment_result, doc_id=instance.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
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
    tax = serializers.UUIDField(allow_null=True, required=False)
    title = serializers.CharField()
    uom_txt = serializers.CharField()
    quantity = serializers.FloatField()
    price = serializers.FloatField()
    subtotal = serializers.FloatField()
    order = serializers.IntegerField()
    id = serializers.UUIDField(allow_null=True, required=False)


class BusinessRequestListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    employee_on_trip = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            "id": obj.employee_inherit_id,
            "first_name": obj.employee_inherit.first_name,
            "last_name": obj.employee_inherit.last_name,
            "full_name": obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    @classmethod
    def get_destination(cls, obj):
        return {
            "id": obj.destination_id,
            "title": obj.destination.title,
        } if obj.destination else {}

    @classmethod
    def get_employee_on_trip(cls, obj):
        if obj.employee_on_trip_list:
            employee_on_trip = []
            for item in list(obj.employee_on_trip_list.all()):
                employee_on_trip.append({'id': item.id, 'code': item.code, 'fullname': item.get_full_name(2)})
            return employee_on_trip
        return {}

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
    departure = serializers.UUIDField()
    destination = serializers.UUIDField()
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
    def validate_departure(cls, value):
        city = DisperseModel(app_model='base.City').get_model()
        try:
            return city.objects.get(pk=value)
        except city.DoesNotExist:
            raise serializers.ValidationError({'detail': BusinessMsg.EMPTY_DEPARTURE})


    @classmethod
    def validate_destination(cls, value):
        city = DisperseModel(app_model='base.City').get_model()
        try:
            return city.objects.get(pk=value)
        except city.DoesNotExist:
            raise serializers.ValidationError({'detail': BusinessMsg.EMPTY_DESTINATION})

    @classmethod
    def create_expense_items(cls, instance, order_dict):
        list_create = []
        for item in order_dict:
            expense = ExpenseItemMapBusinessRequest(
                title=item['title'],
                business_request=instance,
                expense_item_id=str(item['expense_item']),
                tax_id=str(item['tax']) if 'tax' in item else None,
                uom_txt=item['uom_txt'],
                quantity=item['quantity'],
                price=item['price'],
                subtotal=item['subtotal'],
                order=item['order'],
            )
            expense.before_save()
            list_create.append(expense)
        ExpenseItemMapBusinessRequest.objects.bulk_create(list_create)

    @classmethod
    def create_employee_list(cls, instance, emp_list):
        create_list = []
        for emp in emp_list:
            create_list.append(BusinessRequestEmployeeOnTrip(business_mapped=instance, employee_on_trip_mapped_id=emp))
        BusinessRequestEmployeeOnTrip.objects.bulk_create(create_list)

    def validate_attachment(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = BusinessRequestAttachmentFile.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', None)
        expense_list = validated_data.pop('expense_items')
        employee_list = validated_data['employee_on_trip']
        business_request = BusinessRequest.objects.create(**validated_data)
        self.create_expense_items(business_request, expense_list)

        if attachment is not None:
            handle_attach_file(business_request, attachment)

        self.create_employee_list(business_request, employee_list)
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
        att_objs = BusinessRequestAttachmentFile.objects.select_related('attachment').filter(business_request=obj)
        return [item.attachment.get_detail() for item in att_objs]

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
    employee_inherit_id = serializers.UUIDField()

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
        list_current = [str(item.id) for item in ExpenseItemMapBusinessRequest.objects.filter_current(
            business_request=instance
        )]
        list_update = []
        list_create = []
        has_item = []
        for item in order_dict:
            if 'id' in item and TypeCheck.check_uuid(item['id']):
                expense = ExpenseItemMapBusinessRequest(
                    id=item['id'],
                    title=item['title'],
                    business_request=instance,
                    expense_item_id=str(item['expense_item']),
                    tax_id=str(item['tax']) if 'tax' in item else None,
                    uom_txt=item['uom_txt'],
                    quantity=item['quantity'],
                    price=item['price'],
                    subtotal=item['subtotal'],
                    order=item['order'],
                )
                expense.before_save()
                list_update.append(expense)
                has_item.append(str(expense.id))
            else:
                list_create.append(item)

        if len(list_update) > 0:
            ExpenseItemMapBusinessRequest.objects.bulk_update(
                list_update, fields=['title', 'business_request',
                                     'expense_item_id', 'tax_id', 'uom_txt', 'quantity', 'price', 'subtotal', 'order']
            )
        # delete if expense not in list update
        has_item = Counter(list_current) - Counter(has_item)
        has_item = [element for element, count in has_item]
        if len(has_item) > 0:
            ExpenseItemMapBusinessRequest.objects.exclude(id__in=has_item).delete()
        if len(list_create) > 0:
            ExpenseItemMapBusinessRequest.objects.bulk_create(list_create)

    @classmethod
    def handle_employee_on_trip(cls, instance, emp_list):
        delete_id = []
        temp = []
        for item in BusinessRequestEmployeeOnTrip.objects.filter(business_mapped=instance):
            if str(item.employee_on_trip_mapped.id) not in emp_list:
                delete_id.append(str(item.id))
            else:
                temp.append(str(item.employee_on_trip_mapped.id))
        BusinessRequestEmployeeOnTrip.objects.filter(id__in=delete_id).delete()
        temp = Counter(emp_list) - Counter(temp)
        create_obt = []
        for item in temp:
            create_obt.append(
                BusinessRequestEmployeeOnTrip(
                    business_mapped=instance, employee_on_trip_mapped_id=item
                )
            )
        BusinessRequestEmployeeOnTrip.objects.bulk_create(create_obt)

    def validate_attachment(self, attrs):
        user = self.context.get('user', None)
        instance = self.instance
        if user and hasattr(user, 'employee_current_id') and instance and hasattr(instance, 'id'):
            state, result = BusinessRequestAttachmentFile.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=instance.id
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', None)
        expense_list = validated_data.pop('expense_items', None)
        emp_list = validated_data['employee_on_trip'] if 'employee_on_trip' in validated_data else []

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if expense_list is not None:
            self.cover_expense_items(instance, expense_list)

        if attachment is not None:
            handle_attach_file(instance, attachment)

        if len(emp_list) > 0:
            self.handle_employee_on_trip(instance, emp_list)
        return instance

    class Meta:
        model = BusinessRequest
        fields = (
            'title',
            'code',
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
