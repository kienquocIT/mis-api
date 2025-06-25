from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

__all__ = [
    'AbstractListSerializerModel',
    'AbstractDetailSerializerModel',
    'AbstractCreateSerializerModel',
    'SerializerCommonValidate',
    'SerializerCommonHandle',
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


class SerializerCommonValidate:

    @classmethod
    def validate_attachment(cls, user, model_cls, value, doc_id=None):
        if user and hasattr(user, 'employee_current_id'):
            if model_cls and hasattr(model_cls, 'objects') and hasattr(model_cls, 'valid_change'):
                state, result = model_cls.valid_change(
                    current_ids=value, employee_id=user.employee_current_id, doc_id=doc_id
                )
                if state is True:
                    return result
                raise serializers.ValidationError({
                    'attachment': _('Some attachments are being used by another document or do not exist')
                })
        raise serializers.ValidationError({
            'employee_id': _('Employee does not exist.')
        })


class SerializerCommonHandle:

    @classmethod
    def handle_attach_file(cls, relate_app, model_cls, instance, attachment_result):
        if attachment_result and isinstance(attachment_result, dict):
            if relate_app:
                state = model_cls.resolve_change(
                    result=attachment_result, doc_id=instance.id, doc_app=relate_app,
                )
                if state:
                    return True
            raise serializers.ValidationError({
                'attachment': _('Attachment can not verify please try again or contact your admin')
            })
        return True


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
