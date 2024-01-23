from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from apps.masterdata.saledata.models.config import Term, PaymentTerm


def create_term(data, instance):
    if data:
        Term.objects.bulk_create(
            [Term(**term, payment_term=instance) for term in data]
        )
    return True


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = (
            'value',
            'unit_type',
            'day_type',
            'no_of_days',
            'after',
            'order',
        )


class PaymentTermListSerializer(serializers.ModelSerializer):
    term = serializers.SerializerMethodField()

    class Meta:
        model = PaymentTerm
        fields = (
            'id',
            'title',
            'apply_for',
            'term',
        )

    @classmethod
    def get_term(cls, obj):
        return TermSerializer(obj.term_payment_term.all(), many=True).data


class PaymentTermCreateSerializer(serializers.ModelSerializer):
    term = TermSerializer(many=True)

    class Meta:
        model = PaymentTerm
        fields = (
            'title',
            'apply_for',
            'remark',
            'term',
        )

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError(_("Title is required."))

    @classmethod
    def validate_term(cls, value):
        if isinstance(value, list) and value:
            return value
        raise serializers.ValidationError("Term must be at least one rows")

    def create(self, validated_data):
        pm_term = PaymentTerm.objects.create(**validated_data)
        list_term = validated_data['term']
        if list_term:
            create_term(list_term, pm_term)
        return pm_term


class PaymentTermDetailSerializer(serializers.ModelSerializer):
    term = TermSerializer(many=True)

    class Meta:
        model = PaymentTerm
        fields = (
            'id',
            'title',
            'apply_for',
            'remark',
            'term',
        )

    @classmethod
    def validate_term(cls, value):
        if isinstance(value, list) and value:
            return value
        raise serializers.ValidationError("Term must be at least one rows")

    def update(self, instance, validated_data):

        # update Payment term
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # delete old term list follow by payment_term ID
        if instance:
            term = Term.objects.filter(payment_term=instance)
            if term:
                term.delete()
            # create list of term
            create_term(validated_data['term'], instance)
        return instance
