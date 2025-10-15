from rest_framework import serializers
from apps.hrm.payroll.models import PayrollConfig, PayrollInsuranceRule, PayrollDeductionRule, PayrollTaxBracket


class PayrollConfigDetailSerializer(serializers.ModelSerializer):
    insurance_data = serializers.JSONField()
    personal_tax_data = serializers.JSONField()
    tax_bracket_data = serializers.JSONField()

    class Meta:
        model = PayrollConfig
        fields = (
            'id',
            'insurance_data',
            'personal_tax_data',
            'tax_bracket_data',
        )

    @classmethod
    def get_insurance_data(cls, obj):
        rules = obj.payroll_insurance_rule_config.all()
        return [
            {
                "id": rule.id,
                "social_insurance_employee": rule.social_insurance_employee,
                "social_insurance_employer": rule.social_insurance_employer,
                "social_insurance_ceiling": rule.social_insurance_ceiling,
                "unemployment_insurance_employee": rule.unemployment_insurance_employee,
                "unemployment_insurance_employer": rule.unemployment_insurance_employer,
                "unemployment_insurance_ceiling": rule.unemployment_insurance_ceiling,
                "health_insurance_employee": rule.health_insurance_employee,
                "health_insurance_employer": rule.health_insurance_employer,
                "union_insurance_employee": rule.union_insurance_employee,
                "union_insurance_employer": rule.union_insurance_employer,
            } for rule in rules
        ]

    @classmethod
    def get_personal_tax_data(cls, obj):
        deduction_rules = obj.payroll_deduction_rule_config.all()
        return [
            {
                "id": rule.id,
                "personal_deduction": rule.personal_deduction,
                "dependent_deduction": rule.dependent_deduction,
                "effective_date": rule.effective_date
            } for rule in deduction_rules
        ]

    @classmethod
    def get_tax_bracket_data(cls, obj):
        tax_bracket_data = obj.payroll_tax_bracket_config.all()
        return [
            {
                "id": item.id,
                "order": item.order,
                "min_amount": item.min_amount,
                "max_amount": item.max_amount,
                "rate": item.rate
            } for item in tax_bracket_data
        ]


class PayrollConfigUpdateSerializer(serializers.ModelSerializer):
    insurance_data = serializers.JSONField()
    personal_tax_data = serializers.JSONField()
    tax_bracket_data = serializers.JSONField()

    class Meta:
        model = PayrollConfig
        fields = (
            'insurance_data',
            'personal_tax_data',
            'tax_bracket_data',
        )

    def update(self, instance, validated_data):
        insurance_data = validated_data.pop('insurance_data', [])
        personal_tax_data = validated_data.pop('personal_tax_data', {})
        tax_bracket_data = validated_data.pop('tax_bracket_data', [])

        # ------------ Update insurance data ------------
        instance.payroll_insurance_rule_config.all().delete()
        PayrollInsuranceRule.objects.bulk_create([
            PayrollInsuranceRule(payroll_config=instance, **data)
            for data in insurance_data
        ])

        # ------------ Update personal tax data ------------
        instance.payroll_deduction_rule_config.all().delete()
        if personal_tax_data:
            PayrollDeductionRule.objects.create(
                payroll_config=instance,
                **personal_tax_data
            )

        # ------------ Update tax bracket data ------------
        instance.payroll_tax_bracket_config.all().delete()
        PayrollTaxBracket.objects.bulk_create([
            PayrollTaxBracket(payroll_config=instance, **data)
            for data in tax_bracket_data
        ])

        return instance
