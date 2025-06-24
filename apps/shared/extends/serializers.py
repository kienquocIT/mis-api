from rest_framework import serializers

__all__ = [
    'AbstractListSerializerModel',
    'AbstractDetailSerializerModel',
    'AbstractCreateSerializerModel',
    'AbstractCurrencyCreateSerializerModel',
    'AbstractCurrencyDetailSerializerModel',
]


class AbstractListSerializerModel(serializers.ModelSerializer):
    def get_fields(self):
        return {
            'id': serializers.UUIDField(),
            **super().get_fields(),
            'system_status': serializers.IntegerField(),
            'is_change': serializers.BooleanField(),
            'document_root_id': serializers.UUIDField(),
            'document_change_order': serializers.IntegerField(),
        }

    class Meta:
        abstract = True


class AbstractDetailSerializerModel(serializers.ModelSerializer):
    def get_fields(self):
        return {
            'id': serializers.UUIDField(),
            **super().get_fields(),
            'workflow_runtime_id': serializers.UUIDField(),
            'system_status': serializers.IntegerField(),
            'is_change': serializers.BooleanField(),
            'document_root_id': serializers.UUIDField(),
            'document_change_order': serializers.IntegerField(),
            'date_created': serializers.DateTimeField(),
        }

    class Meta:
        abstract = True


class AbstractCreateSerializerModel(serializers.ModelSerializer):
    def get_fields(self):
        return {
            **super().get_fields(),
            'system_status': serializers.ChoiceField(
                choices=[0, 1],
                help_text='0: draft, 1: created',
                default=0,
            ),
            'next_association_id': serializers.UUIDField(required=False, allow_null=True),
            'next_node_collab_id': serializers.UUIDField(required=False, allow_null=True),
            'is_change': serializers.BooleanField(required=False, default=False),
            'document_root_id': serializers.UUIDField(required=False, allow_null=True),
            'document_change_order': serializers.IntegerField(required=False, allow_null=True),
        }

    class Meta:
        abstract = True


class AbstractCurrencyCreateSerializerModel(serializers.ModelSerializer):
    def get_fields(self):
        return {
            **super().get_fields(),
            'currency_company_id': serializers.UUIDField(required=False, allow_null=True),
            'currency_company_data': serializers.JSONField(required=False, default=dict),
            'currency_exchange_id': serializers.UUIDField(required=False, allow_null=True),
            'currency_exchange_data': serializers.JSONField(required=False, default=dict),
            'currency_exchange_rate': serializers.FloatField(default=1),
        }

    class Meta:
        abstract = True


class AbstractCurrencyDetailSerializerModel(serializers.ModelSerializer):
    def get_fields(self):
        return {
            **super().get_fields(),
            'currency_company_id': serializers.UUIDField(),
            'currency_company_data': serializers.JSONField(),
            'currency_exchange_id': serializers.UUIDField(),
            'currency_exchange_data': serializers.JSONField(),
            'currency_exchange_rate': serializers.FloatField(),
        }

    class Meta:
        abstract = True
