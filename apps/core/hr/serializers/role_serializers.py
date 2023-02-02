from rest_framework import serializers

from apps.core.hr.models import Role, RoleHolder, Employee


class RoleListSerializer(serializers.ModelSerializer):

    holder = serializers.SerializerMethodField()
    class Meta:
        model = Role
        fields = (
            'id',
            'title',
            'abbreviation',
            'holder',
        )

    @classmethod
    def get_holder(cls, obj):
        employees = []
        for emp in obj.employee.all():
            try:
                emp = Employee.object_global.get(pk=emp.id)
                employees.append({
                    'id': emp.id,
                    'full_name': emp.last_name + ' ' + emp.first_name,
                    'code': emp.code,
                })
            except Exception as err:
                raise serializers.ValidationError("Employee does not exist.")
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

    @classmethod
    def validate_code(cls, value):
        if Role.object_global.filter(code=value).exclude(code=value).exists():
            raise serializers.ValidationError("Code is exist.")
        return value

    def create(self, validated_data):
        if 'employees' in validated_data:
            data_bulk = validated_data.pop('employees')
            role = Role.object_global.create(**validated_data)
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
        raise serializers.ValidationError("Data is not valid")


class RoleUpdateSerializer(serializers.ModelSerializer):
    employees = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )

    class Meta:
        model = Role
        fields = (
            'id',
            'title',
            'code',
            'abbreviation',
            'employees',
        )

    @classmethod
    def validate_code(cls, value):
        if Role.object_global.filter(code=value).exclude(code=value).exists():
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
            data_bulk = validated_data.pop('employees')
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
    holder = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            'id',
            'title',
            'code',
            'abbreviation',
            'holder',
        )

    @classmethod
    def get_holder(cls, obj):
        employees = []
        for emp in obj.employee.all():
            try:
                emp = Employee.object_global.get(pk=emp.id)
                employees.append({
                    'id': emp.id,
                    'full_name': emp.last_name + ' ' + emp.first_name,
                    'code': emp.code,
                })
            except Exception as err:
                raise serializers.ValidationError("Employee does not exist.")
        return employees
