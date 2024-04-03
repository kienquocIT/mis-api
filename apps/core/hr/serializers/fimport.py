from rest_framework import serializers

from apps.core.hr.models import Group, Employee, GroupLevel
from apps.shared import HRMsg, BaseMsg


class GroupLevelImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLevel
        fields = ('id', 'title', 'code')


class GroupLevelImportSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField()

    @classmethod
    def validate_level(cls, value):
        if value and isinstance(value, int) and value > 0:
            if not GroupLevel.objects.filter_current(level=value, fill__company=True).exists():
                return value
            raise serializers.ValidationError({'level': HRMsg.GROUP_LEVEL_EXIST})
        raise serializers.ValidationError({'level': HRMsg.GROUP_LEVEL_OUT_OF_RANGE})

    description = serializers.CharField(max_length=500)

    def create(self, validated_data):
        group_level = GroupLevel.objects.create(**validated_data)
        return group_level

    class Meta:
        model = GroupLevel
        fields = (
            'level',
            'description',
            'first_manager_description',
            'second_manager_description',
        )


class GroupImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'title', 'code')


class GroupImportSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)

    @classmethod
    def validate_code(cls, value):
        if Group.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError({'code': HRMsg.GROUP_CODE_EXIST})
        return value

    group_level = serializers.CharField()

    @classmethod
    def validate_group_level(cls, value):
        try:
            return GroupLevel.objects.get_current(fill__company=True, level=value)
        except GroupLevel.DoesNotExist:
            raise serializers.ValidationError({'group_level': HRMsg.GROUP_LEVEL_NOT_EXIST})
        except GroupLevel.MultipleObjectsReturned:
            raise serializers.ValidationError({'group_level': BaseMsg.CAUSE_DUPLICATE})

    parent_n = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @classmethod
    def validate_parent_n(cls, value):
        if value:
            try:
                return Group.objects.get_current(fill__company=True, code=value)
            except Group.DoesNotExist:
                raise serializers.ValidationError({'parent_n': HRMsg.GROUP_NOT_EXIST})
            except Group.MultipleObjectsReturned:
                raise serializers.ValidationError({'parent_n': BaseMsg.CAUSE_DUPLICATE})
        return None

    # group_employee = serializers.ListField(
    #     child=serializers.UUIDField(required=False),
    #     required=False
    # )
    #
    # @classmethod
    # def validate_group_employee(cls, value):
    #     return validate_employee_for_group(value)

    first_manager = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @classmethod
    def validate_first_manager(cls, value):
        if value:
            try:
                return Employee.objects.get_current(fill__company=True, code=value)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({'first_manager': HRMsg.EMPLOYEE_NOT_EXIST})
            except Employee.MultipleObjectsReturned:
                raise serializers.ValidationError({'first_manager': BaseMsg.CAUSE_DUPLICATE})
        return None

    second_manager = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @classmethod
    def validate_second_manager(cls, value):
        if value:
            try:
                return Employee.objects.get_current(fill__company=True, code=value)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({'second_manager': HRMsg.EMPLOYEE_NOT_EXIST})
            except Employee.MultipleObjectsReturned:
                raise serializers.ValidationError({'second_manager': BaseMsg.CAUSE_DUPLICATE})
        return None

    title = serializers.CharField(max_length=100)

    def create(self, validated_data):
        group = Group.objects.create(**validated_data)
        if 'group_employee' in validated_data:
            employee_list = Employee.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=validated_data['group_employee']
            )
            if employee_list:
                employee_list.update(group=group)

        return group

    class Meta:
        model = Group
        fields = (
            'code',
            'group_level',
            'parent_n',
            'title',
            'description',
            # 'group_employee',
            'first_manager',
            'first_manager_title',
            'second_manager',
            'second_manager_title'
        )
