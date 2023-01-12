from rest_framework import serializers

from apps.core.hr.models import Employee, GroupLevel, Group, GroupEmployee, RoleHolder


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

    def get_level(self, obj):
        if obj.group_level:
            return obj.group_level.level
        return None


class GroupListSerializer(serializers.ModelSerializer):
    group_level = serializers.SerializerMethodField()
    first_manager = serializers.SerializerMethodField()
    parent_n = serializers.SerializerMethodField()
    upper_group = serializers.SerializerMethodField()

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
            'upper_group',
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

    def get_first_manager(self, obj):
        if obj.first_manager:
            return {
                'id': obj.first_manager.id,
                'full_name': Employee.get_full_name(obj.first_manager, 2),
                'code': obj.first_manager.code
            }
        return {}

    def get_parent_n(self, obj):
        if obj.parent_n:
            return {
                'id': obj.parent_n.id,
                'title': obj.parent_n.title,
                'code': obj.parent_n.code
            }
        return {}

    def get_upper_group(self, obj):
        current_level = obj.group_level.level
        if current_level:
            upper_group = Group.object_global.filter(group_level__level=(current_level-1)).first()
            if upper_group:
                return {
                    'id': upper_group.id,
                    'title': upper_group.title,
                    'code': upper_group.code
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
                'first_manager_description': obj.group_level.first_manager_description,
                'second_manager_description': obj.group_level.second_manager_description,
            }
        return {}

    def get_first_manager(self, obj):
        if obj.first_manager:
            return {
                'id': obj.first_manager.id,
                'full_name': Employee.get_full_name(obj.first_manager, 2),
                'code': obj.first_manager.code
            }
        return {}

    def get_second_manager(self, obj):
        if obj.second_manager:
            return {
                'id': obj.second_manager.id,
                'full_name': Employee.get_full_name(obj.second_manager, 2),
                'code': obj.second_manager.code
            }
        return {}

    def get_parent_n(self, obj):
        if obj.parent_n:
            return {
                'id': obj.parent_n.id,
                'title': obj.parent_n.title,
                'code': obj.parent_n.code
            }
        return {}

    def get_group_employee(self, obj):
        result = []
        group_employee = Employee.object_global.filter(group=obj)
        if group_employee:
            for employee in group_employee:
                role_list = []
                employee_role = RoleHolder.object_normal.filter(employee=employee)
                if employee_role:
                    for emp_role in employee_role:
                        role_list.append({
                            'id': emp_role.role.id,
                            'title': emp_role.role.title,
                            'code': emp_role.role.code,
                        })
                result.append({
                    'id': employee.id,
                    'full_name': Employee.get_full_name(employee, 2),
                    'code': employee.code,
                    'role': role_list
                })
        return result


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
            employee_list = Employee.object_global.filter(id__in=value).count()
            if employee_list == len(value):
                return value
            else:
                raise serializers.ValidationError("Some employee does not exist.")
        else:
            raise serializers.ValidationError("Employee must be array.")

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

    # def validate(self, validate_data):
    #     if 'group_level' in validate_data:
    #         if Group.object_global.filter(group_level=validate_data['group_level']).exists():
    #             raise serializers.ValidationError({"detail": "Group with this level was exist."})
    #     return validate_data

    def create(self, validated_data):
        # create Group
        group = Group.objects.create(**validated_data)
        # create Group Employee
        if 'group_employee' in validated_data:
            employee_list = Employee.object_global.filter(
                id__in=validated_data['group_employee']
            )
            if employee_list:
                for employee in employee_list:
                    employee.group = group
                    employee.save()

            # bulk_info = []
            # for employee in validated_data['group_employee']:
            #     bulk_info.append(GroupEmployee(
            #         group=group,
            #         employee_id=employee
            #     ))
            # if bulk_info:
            #     GroupEmployee.object_normal.bulk_create(bulk_info)

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
            employee_list = Employee.object_global.filter(id__in=value).count()
            if employee_list == len(value):
                return value
            else:
                raise serializers.ValidationError("Some employee does not exist.")
        else:
            raise serializers.ValidationError("Employee must be array.")

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

    def update(self, instance, validated_data):
        # update Group
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # update Group for Employee
        if 'group_employee' in validated_data:
            employee_list = Employee.object_global.filter(
                id__in=validated_data['group_employee']
            )
            if employee_list:
                for employee in employee_list:
                    employee.group = instance
                    employee.save()

            # group_employee_old = GroupEmployee.object_normal.filter(
            #     group=instance
            # )
            # if group_employee_old:
            #     group_employee_old.delete()
            # bulk_info = []
            # for employee in validated_data['group_employee']:
            #     bulk_info.append(GroupEmployee(
            #         group=instance,
            #         employee_id=employee
            #     ))
            # if bulk_info:
            #     GroupEmployee.object_normal.bulk_create(bulk_info)

        return instance
