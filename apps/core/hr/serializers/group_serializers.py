from rest_framework import serializers

from apps.core.hr.models import Employee, GroupLevel, Group, RoleHolder
from apps.shared import HRMsg


# Group Level Serializer
class GroupLevelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLevel
        fields = (
            'id',
            'level',
            'description',
            'first_manager_description',
            'second_manager_description',
        )


class GroupLevelDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLevel
        fields = (
            'id',
            'level',
            'description',
            'first_manager_description',
            'second_manager_description',
        )


class GroupLevelCreateSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField()
    description = serializers.CharField(max_length=500)

    class Meta:
        model = GroupLevel
        fields = (
            'level',
            'description',
            'first_manager_description',
            'second_manager_description',
        )


class GroupLevelMainCreateSerializer(serializers.Serializer):   # noqa
    group_level_data = GroupLevelCreateSerializer(
        required=False,
        many=True
    )

    @classmethod
    def create_new_update_old_group_level(cls, validated_data, group_level_old_level_list, bulk_info):
        group_level_old_level = GroupLevel.objects.filter(
            tenant_id=validated_data.get('tenant_id', None),
            company_id=validated_data.get('company_id', None),
        ).values_list('level', flat=True)
        for level in group_level_old_level:
            group_level_old_level_list.append(level)
        for data in validated_data['group_level_data']:
            # create new
            if data['level'] not in group_level_old_level:
                bulk_info.append(GroupLevel(
                    **data,
                    tenant_id=validated_data.get('tenant_id', None),
                    company_id=validated_data.get('company_id', None),
                ))
            # update old
            else:
                group_level_instance = GroupLevel.objects.filter(level=data['level']).first()
                if group_level_instance:
                    for key, value in data.items():
                        setattr(group_level_instance, key, value)
                    group_level_instance.save()
                    group_level_old_level_list.remove(data['level'])
        return True

    def create(self, validated_data):
        bulk_info = []
        group_level_old_level_list = []
        if 'group_level_data' in validated_data:
            if isinstance(validated_data['group_level_data'], list):
                # create new or update group level
                if validated_data['group_level_data']:
                    self.create_new_update_old_group_level(
                        validated_data=validated_data,
                        group_level_old_level_list=group_level_old_level_list,
                        bulk_info=bulk_info
                    )
                # delete all group level if data from UI == []
                else:
                    group_level_old_level = GroupLevel.objects.filter(
                        tenant_id=validated_data.get('tenant_id', None),
                        company_id=validated_data.get('company_id', None),
                    )
                    if group_level_old_level:
                        group_level_old_level.delete()
        # delete group level
        if group_level_old_level_list:
            group_level_delete = GroupLevel.objects.filter(
                tenant_id=validated_data.get('tenant_id', None),
                company_id=validated_data.get('company_id', None),
                level__in=group_level_old_level_list
            )
            if group_level_delete:
                group_level_delete.delete()
        group_level = GroupLevel.objects.bulk_create(bulk_info)
        return group_level


class GroupLevelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLevel
        fields = (
            'level',
            'description',
            'first_manager_description',
            'second_manager_description',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()


# Group Serializer
class GroupParentListSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            'id',
            'title',
            'code',
            'level'
        )

    @classmethod
    def get_level(cls, obj):
        if obj.group_level:
            return obj.group_level.level
        return None


class GroupListSerializer(serializers.ModelSerializer):
    group_level = serializers.SerializerMethodField()
    first_manager = serializers.SerializerMethodField()
    parent_n = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            'id',
            'title',
            'code',
            'group_level',
            'parent_n',
            'description',
            'group_employee',
            'first_manager',
            'first_manager_title',
            'second_manager',
            'second_manager_title',
        )

    @classmethod
    def get_group_level(cls, obj):
        if obj.group_level:
            return {
                'id': obj.group_level_id,
                'code': obj.group_level.code,
                'level': obj.group_level.level,
                'description': obj.group_level.description,
            }
        return {}

    @classmethod
    def get_first_manager(cls, obj):
        if obj.first_manager:
            return {
                'id': obj.first_manager_id,
                'full_name': obj.first_manager.get_full_name(2),
                'code': obj.first_manager.code
            }
        return {}

    @classmethod
    def get_parent_n(cls, obj):
        if obj.parent_n:
            return {
                'id': obj.parent_n_id,
                'title': obj.parent_n.title,
                'code': obj.parent_n.code
            }
        return {}


class GroupDetailSerializer(serializers.ModelSerializer):
    group_level = serializers.SerializerMethodField()
    first_manager = serializers.SerializerMethodField()
    second_manager = serializers.SerializerMethodField()
    parent_n = serializers.SerializerMethodField()
    group_employee = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            'id',
            'title',
            'code',
            'group_level',
            'parent_n',
            'description',
            'group_employee',
            'first_manager',
            'first_manager_title',
            'second_manager',
            'second_manager_title',
        )

    @classmethod
    def get_group_level(cls, obj):
        if obj.group_level:
            return {
                'id': obj.group_level_id,
                'code': obj.group_level.code,
                'level': obj.group_level.level,
                'description': obj.group_level.description,
                'first_manager_description': obj.group_level.first_manager_description,
                'second_manager_description': obj.group_level.second_manager_description,
            }
        return {}

    @classmethod
    def get_first_manager(cls, obj):
        if obj.first_manager:
            return {
                'id': obj.first_manager_id,
                'full_name': obj.first_manager.get_full_name(2),
                'code': obj.first_manager.code
            }
        return {}

    @classmethod
    def get_second_manager(cls, obj):
        if obj.second_manager:
            return {
                'id': obj.second_manager_id,
                'full_name': obj.second_manager.get_full_name(2),
                'code': obj.second_manager.code
            }
        return {}

    @classmethod
    def get_parent_n(cls, obj):
        if obj.parent_n:
            return {
                'id': obj.parent_n_id,
                'title': obj.parent_n.title,
                'code': obj.parent_n.code
            }
        return {}

    @classmethod
    def get_group_employee(cls, obj):
        result = []
        group_employee = Employee.objects.filter(group=obj)
        if group_employee:
            for employee in group_employee:
                role_list = []
                employee_role = RoleHolder.objects.filter(employee=employee)
                if employee_role:
                    for emp_role in employee_role:
                        role_list.append({
                            'id': emp_role.role.id,
                            'title': emp_role.role.title,
                            'code': emp_role.role.code,
                        })
                result.append({
                    'id': employee.id,
                    'full_name': employee.get_full_name(2),
                    'code': employee.code,
                    'role': role_list
                })
        return result


def validate_employee_for_group(value):
    if isinstance(value, list):
        employee_list = Employee.objects.filter(id__in=value).count()
        if employee_list == len(value):
            return value
        raise serializers.ValidationError({'detail': HRMsg.EMPLOYEES_NOT_EXIST})
    raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_IS_ARRAY})


class GroupCreateSerializer(serializers.ModelSerializer):
    group_level = serializers.UUIDField()
    parent_n = serializers.UUIDField(required=False)
    group_employee = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    first_manager = serializers.UUIDField()
    second_manager = serializers.UUIDField(required=False)
    first_manager_title = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)
    code = serializers.CharField(max_length=100)

    class Meta:
        model = Group
        fields = (
            'group_level',
            'parent_n',
            'title',
            'code',
            'description',
            'group_employee',
            'first_manager',
            'first_manager_title',
            'second_manager',
            'second_manager_title'
        )

    @classmethod
    def validate_code(cls, value):
        if Group.objects.filter(code=value).exists():
            raise serializers.ValidationError({'detail': HRMsg.GROUP_CODE_EXIST})
        return value

    @classmethod
    def validate_group_level(cls, value):
        try:
            return GroupLevel.objects.get(id=value)
        except GroupLevel.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.GROUP_LEVEL_NOT_EXIST})

    @classmethod
    def validate_parent_n(cls, value):
        try:
            return Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.GROUP_NOT_EXIST})

    @classmethod
    def validate_group_employee(cls, value):
        return validate_employee_for_group(value)

    @classmethod
    def validate_first_manager(cls, value):
        try:
            return Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    @classmethod
    def validate_second_manager(cls, value):
        try:
            return Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    def create(self, validated_data):
        # create Group
        group = Group.objects.create(**validated_data)
        # create Group Employee
        if 'group_employee' in validated_data:
            employee_list = Employee.objects.filter(
                id__in=validated_data['group_employee']
            )
            if employee_list:
                for employee in employee_list:
                    employee.group = group
                    employee.save()

        return group


class GroupUpdateSerializer(serializers.ModelSerializer):
    group_level = serializers.UUIDField(required=False)
    parent_n = serializers.UUIDField(required=False)
    group_employee = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    first_manager = serializers.UUIDField(required=False)
    second_manager = serializers.UUIDField(required=False)

    class Meta:
        model = Group
        fields = (
            'group_level',
            'parent_n',
            'title',
            'code',
            'description',
            'group_employee',
            'first_manager',
            'first_manager_title',
            'second_manager',
            'second_manager_title'
        )

    @classmethod
    def validate_group_level(cls, value):
        try:
            return GroupLevel.objects.get(id=value)
        except GroupLevel.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.GROUP_LEVEL_NOT_EXIST})

    @classmethod
    def validate_parent_n(cls, value):
        try:
            return Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.GROUP_NOT_EXIST})

    @classmethod
    def validate_group_employee(cls, value):
        return validate_employee_for_group(value)

    @classmethod
    def validate_first_manager(cls, value):
        try:
            return Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    @classmethod
    def validate_second_manager(cls, value):
        try:
            return Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    def update(self, instance, validated_data):
        # update Group
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # update Group for Employee
        if 'group_employee' in validated_data:
            employee_group_old = Employee.objects.filter(
                group=instance
            )
            for emp_group_old in employee_group_old:
                if emp_group_old.id not in validated_data['group_employee']:
                    emp_group_old.group = None
                    emp_group_old.save()

            employee_list = Employee.objects.filter(
                id__in=validated_data['group_employee']
            )
            if employee_list:
                for employee in employee_list:
                    employee.group = instance
                    employee.save()

        return instance
