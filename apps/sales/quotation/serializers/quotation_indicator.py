from rest_framework import serializers

from apps.sales.quotation.models import QuotationIndicatorConfig
from apps.shared import SaleMsg
from apps.shared.extends.signals import ConfigDefaultData


class IndicatorListSerializer(serializers.ModelSerializer):
    formula_data = serializers.JSONField()
    formula_data_show = serializers.JSONField()

    class Meta:
        model = QuotationIndicatorConfig
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'example',
            'order',
            'formula_data',
            'formula_data_show',
            'acceptance_affect_by',
            'is_acceptance_editable',
        )


class IndicatorDetailSerializer(serializers.ModelSerializer):
    formula_data = serializers.JSONField()
    formula_data_show = serializers.JSONField()

    class Meta:
        model = QuotationIndicatorConfig
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'example',
            'order',
            'formula_data',
            'formula_data_show',
            'acceptance_affect_by',
            'is_acceptance_editable',
        )


class IndicatorCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuotationIndicatorConfig
        fields = (
            'title',
            'remark',
            'example',
            'order',
            'application_code'
        )

    def create(self, validated_data):
        indicator = QuotationIndicatorConfig.objects.create(**validated_data)
        return indicator


class IndicatorUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuotationIndicatorConfig
        fields = (
            'title',
            'remark',
            'example',
            'formula_data',
            'formula_data_show',
            'acceptance_affect_by',
            'is_acceptance_editable',
            'order',
        )

    @classmethod
    def validate_order(cls, value):
        if isinstance(value, int):
            if value > QuotationIndicatorConfig.objects.filter_current(fill__company=True).count() or value == 0:
                raise serializers.ValidationError({'detail': SaleMsg.INDICATOR_ORDER_OUT_OF_RANGE})
        return value

    @classmethod
    def reorder(cls, instance, validated_data):
        list_update = []
        json_store = {}
        # change order to lower order => update order of records after instance += 1
        if validated_data['order'] < instance.order:
            other_indicators = QuotationIndicatorConfig.objects.filter(
                company_id=instance.company_id,
                order__gte=validated_data['order'],
                order__lte=instance.order,
            ).exclude(id=instance.id)
            for other_indicator in other_indicators:
                original_order = other_indicator.order  # Store original order before update
                json_store[original_order] = original_order + 1  # Save original -> new mapping
                other_indicator.order = other_indicator.order + 1
                list_update.append(other_indicator)
        # change order to higher order => update order of records after instance -= 1
        elif validated_data['order'] > instance.order:
            other_indicators = QuotationIndicatorConfig.objects.filter(
                company_id=instance.company_id,
                order__lte=validated_data['order'],
                order__gte=instance.order,
            ).exclude(id=instance.id)
            for other_indicator in other_indicators:
                original_order = other_indicator.order  # Store original order before update
                json_store[original_order] = original_order - 1  # Save original -> new mapping
                other_indicator.order = other_indicator.order - 1
                list_update.append(other_indicator)
                # other_indicator.save(update_fields=['order'])
        QuotationIndicatorConfig.objects.bulk_update(list_update, fields=['order'])
        return json_store

    @classmethod
    def reparse_formula_data(cls, instance, json_store):
        list_update = []
        for indicator in QuotationIndicatorConfig.objects.filter(company_id=instance.company_id):
            if indicator.formula_data:
                for formula in indicator.formula_data:
                    if 'is_indicator' in formula and 'order' in formula:
                        if formula['is_indicator'] is True and formula['order'] in json_store:
                            formula['order'] = json_store[formula['order']]
                            list_update.append(indicator)
        QuotationIndicatorConfig.objects.bulk_update(list_update, fields=['formula_data'])
        return True

    def update(self, instance, validated_data):
        # update other indicators if change order
        if 'order' in validated_data:
            json_store = self.reorder(instance=instance, validated_data=validated_data)
            self.reparse_formula_data(instance=instance, json_store=json_store)
        # update
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance


class IndicatorCompanyRestoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuotationIndicatorConfig
        fields = ('title',)

    @staticmethod
    def restore_company_indicator(company_obj):
        QuotationIndicatorConfig.objects.filter(company_id=company_obj.id).delete()
        ConfigDefaultData(company_obj).quotation_indicator_config()
        return True

    def update(self, instance, validated_data):
        self.restore_company_indicator(company_obj=instance.company)
        return instance
