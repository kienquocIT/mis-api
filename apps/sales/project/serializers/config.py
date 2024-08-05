__all__ = ['ProjectConfigDetailSerializer', 'ProjectConfigUpdateSerializer']

from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.sales.project.models import ProjectConfig
from apps.shared import HRMsg


class ProjectConfigDetailSerializer(serializers.ModelSerializer):
    person_can_end = serializers.SerializerMethodField()

    @classmethod
    def get_person_can_end(cls, obj):
        if obj.person_can_end:
            p_list = Employee.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=obj.person_can_end
            ).select_related('group')
            person_list = [
                {
                    "id": str(item[0]),
                    "full_name": f'{item[2]} {item[1]}',
                    "first_name": item[1],
                    "last_name": item[2],
                    "group": {
                        "id": str(item[3]),
                        "title": item[4],
                        "code": item[5],
                    }
                } for item in p_list.values_list(
                    'id', 'first_name', 'last_name', 'group__id', 'group__title', 'group__code'
                )
            ]
            return person_list
        return []

    class Meta:
        model = ProjectConfig
        fields = (
            'id',
            'person_can_end',
        )


class ProjectConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectConfig
        fields = ('person_can_end',)

    @classmethod
    def validate_person_can_end(cls, value):
        deli_per = Employee.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id__in=value
        )
        if len(deli_per) != len(value):
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
