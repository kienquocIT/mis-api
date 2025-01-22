from rest_framework import serializers

from apps.core.chat3rd.models import ZaloPerson, ZaloMessage, ZaloToken
from apps.core.chat3rd.utils.zalo_serializer_sub import (
    SenderSerializer, RecipientSerializer, FollowerSerializer,
    MessageSerializer,
)

EVENT_NAME = [
    "user_send_location",
    "user_send_image",
    "user_send_link",
    "user_send_text",
    "user_send_sticker",
    "user_send_gif",
    "user_received_message",
    "user_seen_message",
    "user_send_audio",

    "oa_send_text",
    "oa_send_image",
    "oa_send_list",
    "oa_send_gif",
    "oa_send_file",
    "oa_send_sticker",
    "oa_send_consent",
]


class ZaloEventSerializer(serializers.Serializer):  # noqa
    app_id = serializers.CharField(max_length=255)
    user_id_by_app = serializers.CharField(max_length=255, required=False)
    oa_id = serializers.CharField(max_length=255, required=False)
    event_name = serializers.ChoiceField(
        choices=EVENT_NAME,
    )
    timestamp = serializers.CharField(max_length=255)
    sender = SenderSerializer(required=False)
    recipient = RecipientSerializer(required=False)
    follower = FollowerSerializer(required=False)
    source = serializers.CharField(max_length=255, required=False)
    message = MessageSerializer(required=False)

    def validate(self, attrs):
        event_name = attrs["event_name"]

        if event_name.startswith('user_'):
            if event_name.startswith('user_send_'):
                if not attrs.get("message"):
                    raise serializers.ValidationError({"message": "Field is required for this event."})
                if event_name == 'user_seen_message' and not attrs["message"].get("msg_ids"):
                    raise serializers.ValidationError(
                        {"message.msg_ids": "Field is required for seen message event."}
                    )
            elif event_name == 'user_received_message':
                if not attrs.get("message") or not attrs["message"].get("msg_id"):
                    raise serializers.ValidationError(
                        {"message.msg_id": "Field is required for received message event."}
                    )
            else:
                raise serializers.ValidationError(
                    {
                        'detail': 'Event name is not support',
                    }
                )
            return attrs
        if event_name.startswith('oa_'):
            return attrs
        raise serializers.ValidationError(
            {
                'detail': 'Event name is not support',
            }
        )

    @classmethod
    def create_by_user_send_text(cls, token_obj: ZaloToken, validated_data: dict):
        cls_event = ZaloEventControl(token_obj=token_obj, validated_data=validated_data)
        person_obj = cls_event.create_or_get_person()
        return cls_event.create_msg(person_obj=person_obj)

    def save(self, **kwargs):
        # token_obj: ZaloToken = kwargs['token_obj']
        event_name = kwargs['event_name']

        if event_name.startswith('user_'):
            ...
        elif event_name.startswith('oa_'):
            ...
        else:
            ...


class ZaloMessageControl:
    token_obj: ZaloToken
    validated_data: dict

    @property
    def sender_id(self):
        return self.validated_data['sender']['id']

    @property
    def recipient_id(self):
        return self.validated_data['recipient']['id']

    @property
    def msg_id(self):
        return self.validated_data['message']['msg_id']

    @property
    def text(self):
        return self.validated_data['message']['text']

    @property
    def attachments(self):
        return self.validated_data['message']['attachments']

    @property
    def timestamp(self):
        return self.validated_data['message']['timestamp']

    @property
    def user_send__oa_id(self):
        return self.recipient_id

    @property
    def oa_send__oa_id(self):
        return self.sender_id

    def __init__(self, token_obj: ZaloToken, validated_data: dict):
        self.token_obj = token_obj
        self.validated_data = validated_data


class ZaloEventControl:
    msg_control: ZaloMessageControl

    def __init__(self, token_obj: ZaloToken, validated_data: dict):
        self.token_obj = token_obj
        self.validated_data = validated_data
        self.msg_control = ZaloMessageControl(token_obj=token_obj, validated_data=validated_data)

    def create_or_get_person(self) -> ZaloPerson:
        sender_id = self.msg_control.sender_id
        person_obj, _created = ZaloPerson.objects.get_or_create(
            oa_id=self.token_obj.oa_id,
            account_id=sender_id,
            defaults={
                'token': self.token_obj,
                'oa_id': self.token_obj.oa_id,
                'account_id': sender_id,
            }
        )
        return person_obj

    def create_msg(self, person_obj=None) -> ZaloMessage:
        if not person_obj:
            person_obj = self.create_or_get_person()
        return ZaloMessage.objects.create(
            person=person_obj,
            sender=self.msg_control.sender_id,
            recipient=self.msg_control.recipient_id,
            mid=self.msg_control.msg_id,
            text=self.msg_control.text,
            is_echo=True,
            attachments=self.msg_control.attachments,
            timestamp=self.msg_control.timestamp,
        )
