from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.core.organization.models import GroupLevel, Group, GroupEmployee
from apps.core.hr.models import Role, RoleHolder


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
            'user_created',
            'user_modified',
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
            'user_created',
            'user_modified',
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


class GroupLevelMainCreateSerializer(serializers.Serializer):
    group_level_data = GroupLevelCreateSerializer(
        required=False,
        many=True
    )

    def create_new_update_old_group_level(self, validated_data, group_level_old_level_list, bulk_info):
        group_level_old_level = GroupLevel.object_global.filter(
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
                    user_created=validated_data.get('user_created', None),
                    tenant_id=validated_data.get('tenant_id', None),
                    company_id=validated_data.get('company_id', None),
                ))
            # update old
            else:
                group_level_instance = GroupLevel.object_global.filter(level=data['level']).first()
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
                    group_level_old_level = GroupLevel.object_global.filter(
                        tenant_id=validated_data.get('tenant_id', None),
                        company_id=validated_data.get('company_id', None),
                    )
                    if group_level_old_level:
                        group_level_old_level.delete()
        # delete group level
        if group_level_old_level_list:
            group_level_delete = GroupLevel.object_global.filter(
                    tenant_id=validated_data.get('tenant_id', None),
                    company_id=validated_data.get('company_id', None),
                    level__in=group_level_old_level_list
                )
            if group_level_delete:
                group_level_delete.delete()
        group_level = GroupLevel.object_global.bulk_create(bulk_info)
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
class GroupListSerializer(serializers.ModelSerializer):
    group_level = serializers.SerializerMethodField()

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
            'user_created',
            'user_modified',
        )

    def get_group_level(self, obj):
        if obj.group_level:
            return {
                'id': obj.group_level.id,
                'code': obj.group_level.code,
                'level': obj.group_level.level,
                'description': obj.group_level.description,
            }
        return {}


class GroupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            'id',
            'group_level',
            'parent_n',
            'description',
            'group_employee',
            'first_manager',
            'first_manager_title',
            'second_manager',
            'second_manager_title',
            'user_created',
            'user_modified',
        )


class GroupCreateSerializer(serializers.ModelSerializer):
    group_level = serializers.UUIDField()
    parent_n = serializers.UUIDField(required=False)
    group_employee = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    first_manager = serializers.UUIDField()
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

    def validate_code(self, value):
        if Group.object_global.filter(code=value).exists():
            raise serializers.ValidationError("Code is exist.")
        return value

    def validate_group_level(self, value):
        try:
            return GroupLevel.object_global.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Group level does not exist.")

    def validate_parent_n(self, value):
        try:
            return Group.object_global.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Group does not exist.")

    def validate_group_employee(self, value):
        if isinstance(value, list):
            pass

    def validate_first_manager(self, value):
        try:
            return Employee.object_global.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Employee does not exist.")

    def validate_second_manager(self, value):
        try:
            return Employee.object_global.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Employee does not exist.")

    def create(self, validated_data):
        # create Group
        group = Group.objects.create(**validated_data)
        # create Group Employee
        if 'group_employee' in validated_data:
            bulk_info = []
            for employee in validated_data['group_employee']:
                bulk_info.append(GroupEmployee(
                    group=group,
                    employee_id=employee
                ))
            if bulk_info:
                GroupEmployee.object_normal.bulk_create(bulk_info)

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

    def validate_group_level(self, value):
        try:
            return GroupLevel.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Group level does not exist.")

    def validate_parent_n(self, value):
        try:
            return Group.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Group does not exist.")

    def validate_group_employee(self, value):
        if isinstance(value, list):
            pass

    def validate_first_manager(self, value):
        try:
            return Employee.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Employee does not exist.")

    def validate_second_manager(self, value):
        try:
            return Employee.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Employee does not exist.")

    def update(self, instance, validated_data):
        # update Group
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # delete old & update Group Employee
        if 'group_employee' in validated_data:
            group_employee_old = GroupEmployee.object_normal.filter(
                group=instance
            )
            if group_employee_old:
                group_employee_old.delete()
            bulk_info = []
            for employee in validated_data['group_employee']:
                bulk_info.append(GroupEmployee(
                    group=instance,
                    employee_id=employee
                ))
            if bulk_info:
                GroupEmployee.object_normal.bulk_create(bulk_info)

        return instance


class RoleListSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            'id',
            'title',
            'abbreviation',
            'employees',
        )

    def get_employees(self, obj):
        emp = RoleHolder.object_normal.filter(role_id=obj.id)
        employees = [{'id': i.employee_id} for i in emp]
        return employees


class RoleCreateSerializer(serializers.ModelSerializer):
    employees = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )

    class Meta:
        model = Role
        fields = (
            'title',
            'abbreviation',
            'employees',
        )

    def validate_code(self, value):
        if Role.object_global.filter(code=value).exists():
            raise serializers.ValidationError("Code is exist.")
        return value

    def create(self, validated_data):
        if 'employees' in validated_data:
            data_bulk = validated_data['employees']
        del validated_data['employees']
        role = Role.objects.create(**validated_data)
        if data_bulk:
            bulk_info = []
            for employee in data_bulk:
                bulk_info.append(RoleHolder(
                    role=role,
                    employee_id=employee
                ))
            if bulk_info:
                RoleHolder.object_normal.bulk_create(bulk_info)
        return role


class RoleUpdateSerializer(serializers.ModelSerializer):
    employees = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )

    class Meta:
        model = Role
        fields = (
            'title',
            'abbreviation',
            'employees',
        )

    def validate_code(self, value):
        if Role.object_global.filter(code=value).exists():
            raise serializers.ValidationError("Code is exist.")
        return value

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if 'employees' in validated_data:
            employees_old = RoleHolder.object_normal.filter(role=instance)
            if employees_old:
                employees_old.delete()
            data_bulk = validated_data['employees']
        del validated_data['employees']
        if data_bulk:
            bulk_info = []
            for employee in data_bulk:
                bulk_info.append(RoleHolder(
                    role=instance,
                    employee_id=employee
                ))
            if bulk_info:
                RoleHolder.object_normal.bulk_create(bulk_info)
        return instance


class RoleDetailSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            'id',
            'code',
            'title',
            'abbreviation',
            'employees',
        )

    def get_employees(self, obj):
        emp = RoleHolder.object_normal.filter(role_id=obj.id)
        employees = [{'id': i.employee_id} for i in emp]
        return employees



