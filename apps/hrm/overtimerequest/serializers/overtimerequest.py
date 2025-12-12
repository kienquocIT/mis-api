from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.hrm.overtimerequest.models import OvertimeRequest, OTMapWithEmployeeShift
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, DisperseModel, \
    AbstractListSerializerModel
from apps.shared.translations.hrm import HRMMsg


def create_mapped_with_shift(obj):
    data = obj.date_list
    ot_id = obj.id
    employee_lst = obj.employee_list
    bulk_create_lst = []
    for empl_id in employee_lst:
        for item in data:
            if item['shift']:
                bulk_create_lst.append(
                    OTMapWithEmployeeShift(
                        overtime_request_id=ot_id,
                        shift_id=item['shift']['id'],
                        date=item['date'],
                        employee_id=empl_id,
                        type=item['ot_type'],
                        company_id=obj.company_id,
                        tenant_id=obj.tenant_id
                    )
                )
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
        date_list = [item['date'] for item in validate_data['date_list']]
        valid_list = OTMapWithEmployeeShift.objects.filter_on_company(
            date__in=date_list
        )
        if len(validate_data['employee_list']):
            valid_list = valid_list.filter(employee_id__in=validate_data['employee_list'])
        else:
            valid_list = valid_list.filter(employee_id=validate_data['employee_inherit']['id'])
        for item in valid_list:
            ot_request = item.overtime_request
            if validate_data['start_time'] < ot_request.end_time and validate_data['end_time'] > ot_request.start_time:
                raise serializers.ValidationError({'detail': HRMMsg.HRM_OVERTIME_VALID_DATE})
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        overtime = OvertimeRequest.objects.create(**validated_data)
        create_mapped_with_shift(overtime)
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
        date_list = [item['date'] for item in validate_data['date_list']]
        valid_list = OTMapWithEmployeeShift.objects.filter_on_company(date__in=date_list).exclude(
            id__in=self.instance.ot_map_with_employee_shift.all().values_list('id', flat=True)
        )
        if len(validate_data['employee_list']):
            valid_list = valid_list.filter(employee_id__in=validate_data['employee_list'])
        else:
            valid_list = valid_list.filter(employee_id=validate_data['employee_inherit']['id'])
        for item in valid_list:
            if validate_data['start_time'] < item.overtime_request.end_time \
                    and validate_data['end_time'] > item.overtime_request.start_time:
                raise ValueError(HRMMsg.HRM_OVERTIME_VALID_DATE)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        instance.ot_map_with_employee_shift.all().delete()
        create_mapped_with_shift(instance)
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
