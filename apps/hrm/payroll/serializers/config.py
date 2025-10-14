from django.db import transaction
from rest_framework import serializers

from apps.hrm.payroll.models import PayrollConfig, PayrollInsuranceRule, PayrollDeductionRule, PayrollTaxBracket
from apps.shared import AbstractListSerializerModel, AbstractCreateSerializerModel


class PayrollConfigInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollInsuranceRule
        fields = (
            'social_insurance_employee',
            'social_insurance_employer',
            'social_insurance_ceiling',
            'unemployment_insurance_employee',
            'unemployment_insurance_employer',
            'unemployment_insurance_ceiling',
            'health_insurance_employee',
            'health_insurance_employer',
            'union_insurance_employee',
            'union_insurance_employer'
        )


class PayrollConfigIncomeTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollDeductionRule
        fields = (
            'personal_deduction',
            'dependent_deduction',
            'effective_date'
        )


class PayrollConfigTaxBracketSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollTaxBracket
        fields = (
            'order',
            'min_amount',
            'max_amount',
            'rate'
        )


class PayrollConfigCommonFunction:
    @staticmethod
    def create_insurance_data(payroll_config_obj, insurance_data):
        PayrollInsuranceRule.objects.filter(payroll_config=payroll_config_obj).delete()
        PayrollInsuranceRule.objects.create(
            title='',
            payroll_config_id=str(payroll_config_obj.id),
            company=payroll_config_obj.company,
            **insurance_data
        )
        return True

    @staticmethod
    def create_personal_income_tax(payroll_config_obj, personal_income_tax):
        PayrollDeductionRule.objects.filter(payroll_config=payroll_config_obj).delete()
        PayrollDeductionRule.objects.create(
            title='',
            payroll_config_id=str(payroll_config_obj.id),
            company=payroll_config_obj.company,
            **personal_income_tax
        )
        return True

    @staticmethod
    def create_tax_bracket(payroll_config_obj, tax_bracket_data):
        bulk_info_tax_bracket = []

        for tax_bracket_item in tax_bracket_data:
            tax_bracket_obj = PayrollTaxBracket(
                payroll_config=payroll_config_obj,
                title='',
                order=tax_bracket_item.get('order'),
                min_amount=tax_bracket_item.get('min_amount'),
                max_amount=tax_bracket_item.get('max_amount'),
                rate=tax_bracket_item.get('rate'),
            )
            bulk_info_tax_bracket.append(tax_bracket_obj)

        PayrollTaxBracket.objects.filter(payroll_config=payroll_config_obj).delete()
        PayrollTaxBracket.objects.bulk_create(bulk_info_tax_bracket)
        return True


class PayrollConfigListSerializer(AbstractListSerializerModel):
    employee = serializers.SerializerMethodField()

    class Meta:
        model = PayrollConfig
        fields = (
            'id',
            'code',
            'description',
            'absence_type',
            'employee',
            'date_created',
            'system_status'
        )

    @classmethod
    def get_employee(cls, obj):
        return obj.employee.get_detail_minimal() if obj.employee else {}


class PayrollConfigCreateSerializer(AbstractCreateSerializerModel):
    insurance_data = PayrollConfigInsuranceSerializer()
    personal_income_tax = PayrollConfigIncomeTaxSerializer()
    tax_bracket_data = PayrollConfigTaxBracketSerializer(many=True)

    def create(self, validate_data):
        with transaction.atomic():
            for field in ['system_status', 'is_change', 'employee_inherit_id']:
                validate_data.pop(field, None)
            insurance_data = validate_data.pop('insurance_data', [])
            personal_income_tax = validate_data.pop('personal_income_tax', [])
            tax_bracket_data = validate_data.pop('tax_bracket_data', [])
            payroll_config = PayrollConfig.objects.create(**validate_data)
            PayrollConfigCommonFunction.create_insurance_data(payroll_config, insurance_data)
            PayrollConfigCommonFunction.create_personal_income_tax(payroll_config, personal_income_tax)
            PayrollConfigCommonFunction.create_tax_bracket(payroll_config, tax_bracket_data)
            return payroll_config

    class Meta:
        model = PayrollConfig
        fields = (
            'company',
            'insurance_data',
            'personal_income_tax',
            'tax_bracket_data',
        )


class PayrollConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollConfig
        fields = '__all__'
