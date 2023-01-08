import random

from rest_framework import serializers

from apps.core.company.models import Company


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'date_created',
            'representative_fullname'
        )


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'address',
            'email',
            'phone',
        )


class CompanyOverviewSerializer(serializers.ModelSerializer):
    license_used = serializers.SerializerMethodField()
    total_user = serializers.SerializerMethodField()
    power_user = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    employee_linked_user = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'license_used',
            'total_user',
            'power_user',
            'employee',
            'employee_linked_user'
        )

    @classmethod
    def get_license_used(cls, obj):
        return {
            'sale': random.randrange(20, 50, 3),
            'e-office': random.randrange(20, 50, 3),
            'hrm': random.randrange(20, 50, 3),
            'personal': random.randrange(20, 50, 3)
        }

    @classmethod
    def get_total_user(cls, obj):
        return random.randrange(20, 50, 3)

    @classmethod
    def get_power_user(cls, obj):
        return random.randrange(1, 10, 3)

    @classmethod
    def get_employee(cls, obj):
        return random.randrange(20, 50, 3)

    @classmethod
    def get_employee_linked_user(cls, obj):
        return random.randrange(1, 20, 3)
