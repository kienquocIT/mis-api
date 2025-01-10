from rest_framework import serializers

from apps.masterdata.saledata.models import Contact
from apps.core.chat3rd.models import MessengerPerson, MessengerMessage
from apps.core.chat3rd.msg import Chat3rdMsg
from apps.sales.lead.models import Lead
from apps.shared import TypeCheck


class MessengerPersonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessengerPerson
        fields = ('id', 'name', 'avatar', 'account_id', 'last_updated', 'contact_id', 'lead_id')


class MessengerMessageListSerializer(serializers.ModelSerializer):
    person = serializers.SerializerMethodField()

    @classmethod
    def get_person(cls, obj):
        return {
            'id': obj.person.id,
            'name': obj.person.name,
            'avatar': obj.person.avatar,
        } if obj.person else {}

    class Meta:
        model = MessengerMessage
        fields = (
            'id', 'sender', 'recipient', 'mid',
            'text', 'attachments', 'is_echo', 'timestamp', 'person',
        )


class MessengerPersonLinkToContactSerializer(serializers.ModelSerializer):
    contact_id = serializers.UUIDField()

    @classmethod
    def validate_contact_id(cls, attr):
        if attr and TypeCheck.check_uuid(attr):
            try:
                Contact.objects.get_current(fill__tenant=True, fill__company=True, pk=attr)
                return attr
            except Contact.DoesNotExist:
                pass
        raise serializers.ValidationError(
            {
                'contact_id': Chat3rdMsg.CONTACT_ID_NOT_FOUND,
            }
        )

    def update(self, instance, validated_data):
        contact_id = validated_data['contact_id']
        instance.contact_id = contact_id
        instance.save(update_fields=['contact_id'])
        return instance

    class Meta:
        model = MessengerPerson
        fields = ('contact_id',)


class MessengerPersonLinkToLeadSerializer(serializers.ModelSerializer):
    lead_id = serializers.UUIDField()

    @classmethod
    def validate_lead_id(cls, attr):
        if attr and TypeCheck.check_uuid(attr):
            try:
                Lead.objects.get_current(fill__tenant=True, fill__company=True, pk=attr)
                return attr
            except Lead.DoesNotExist:
                pass
        raise serializers.ValidationError(
            {
                'lead_id': Chat3rdMsg.LEAD_ID_NOT_FOUND,
            }
        )

    def update(self, instance, validated_data):
        lead_id = validated_data['lead_id']
        instance.lead_id = lead_id
        instance.save(update_fields=['lead_id'])
        return instance

    class Meta:
        model = MessengerPerson
        fields = ('lead_id',)
