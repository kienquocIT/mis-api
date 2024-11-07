from rest_framework import serializers

from apps.hrm.employeeinfo.models import EmployeeInfo, EmployeeHRNotMapEmployeeHRM


class EmployeeInfoListSerializers(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    @classmethod
    def get_employee(cls, obj):
        if obj.employee and hasattr(obj.employee, 'get_detail_minimal'):
            return obj.employee.get_detail_minimal()
        return {}

    class Meta:
        model = EmployeeInfo
        fields = (
            'id',
            'employee',
        )


class EmployeeInfoCreateSerializers(serializers.ModelSerializer):

    # @classmethod
    def create(self, validated_data):
        info = EmployeeInfo.objects.create(**validated_data)
        return info

    class Meta:
        model = EmployeeInfo
        fields = (
            'id',
        )


class EmployeeInfoDetailSerializers(serializers.ModelSerializer):
    # employee = serializers.SerializerMethodField()
    #
    # @classmethod
    # def get_employee(cls, obj):
    #     if obj.employee_inherit:
    #         return obj.employee_inherit_data
    #     return {}

    class Meta:
        model = EmployeeInfo
        fields = (
            'id',
            'employee'
        )


class EmployeeInfoUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeInfo
        fields = (
            'id',
            'employee'
        )


class EmployeeHRNotMapHRMListSerializers(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    @classmethod
    def get_employee(cls, obj):
        if obj.employee and hasattr(obj.employee, 'get_detail_minimal'):
            emp = obj.employee.get_detail_minimal()
            emp.update(
                {
                    'email': obj.employee.email,
                    'date_joined': obj.employee.date_joined,
                    'dob': obj.employee.dob,
                    'phone': obj.employee.phone,
                }
            )
            user = obj.employee.user
            emp['user'] = {
                'id': str(user.id),
                'first_name': user.first_name,
                'last_name': user.last_name
            } if user else {}

            return emp
        return {}

    class Meta:
        model = EmployeeHRNotMapEmployeeHRM
        fields = (
            'employee',
        )
