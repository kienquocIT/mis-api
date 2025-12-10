from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.hrm.overtimerequest.models import OvertimeRequest, OTMapWithEmployeeShift
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, DisperseModel, \
    AbstractListSerializerModel


def create_mapped_with_shift(data, ot_id, employee_lst):
    bulk_create_lst = []
    for empl_id in employee_lst:
        for item in data:
            if item['shift']:
                bulk_create_lst.append(OTMapWithEmployeeShift(
                    overtime_request_id=ot_id,
                    shift_id=item['shift']['id'],
                    date=item['date'],
                    employee_id=empl_id,
                    type=item['ot_type'],
                ))
    if bulk_create_lst:
        OTMapWithEmployeeShift.objects.bulk_create(bulk_create_lst)


class OvertimeRequestListSerializers(AbstractListSerializerModel):
    class Meta:
        model = OvertimeRequest
        fields = (
            'id',
            'title',
            'code',
            'employee_created_data',
            'employee_list_data',
            'employee_inherit_data',
            'date_created',
            'system_status',
        )


class OvertimeRequestCreateSerializers(AbstractCreateSerializerModel):

    def validate(self, validate_data):
        if len(validate_data['employee_list']):
            employee_list = DisperseModel(app_model='hr.Employee').get_model().objects.filter(
                id__in=validate_data['employee_list'],
            )
            if employee_list.exists() and employee_list.count() == len(validate_data['employee_list']):
                validate_data['employee_list_data'] = [{
                    'id': str(item.id),
                    'code': item.code,
                    'group': {'id': str(item.group.id), 'title': item.group.title} if item.group else {},
                    'full_name': item.get_full_name()
                } for item in employee_list]
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        overtime = OvertimeRequest.objects.create(**validated_data)
        create_mapped_with_shift(overtime.date_list, overtime.id, overtime.employee_list)
        return overtime

    class Meta:
        model = OvertimeRequest
        fields = (
            'title',
            'employee_inherit',
            'employee_list',
            'employee_list_data',
            'start_time',
            'end_time',
            'reason',
            'date_list',
        )


class OvertimeRequestDetailSerializers(AbstractDetailSerializerModel):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit_data

    class Meta:
        model = OvertimeRequest
        fields = (
            'id',
            'title',
            'code',
            'employee_inherit',
            'employee_list_data',
            'employee_created_data',
            'start_time',
            'end_time',
            'reason',
            'date_list',
        )


class OvertimeRequestUpdateSerializers(AbstractCreateSerializerModel):
    employee_list = serializers.JSONField(required=False, allow_null=True)

    def validate(self, validate_data):
        if len(validate_data['employee_list']):
            employee_list = DisperseModel(app_model='hr.Employee').get_model().objects.filter(
                id__in=validate_data['employee_list'],
            )
            if employee_list.exists() and employee_list.count() == len(validate_data['employee_list']):
                validate_data['employee_list_data'] = [{
                    'id': str(item.id),
                    'code': item.code,
                    'group': {'id': str(item.group.id), 'title': item.group.title} if item.group else {},
                    'full_name': item.get_full_name()
                } for item in employee_list]
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        instance.ot_map_with_employee_shift.all().delete()
        create_mapped_with_shift(instance.date_list, instance.id, instance.employee_list)
        return instance

    class Meta:
        model = OvertimeRequest
        fields = (
            'title',
            'employee_inherit',
            'employee_list',
            'employee_list_data',
            'start_time',
            'end_time',
            'reason',
            'date_list',
        )
