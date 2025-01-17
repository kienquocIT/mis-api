from rest_framework import serializers

ATTACHMENT_TYPE = (
    ("location", "user_send_location"),
    ("image", "user_send_image"),
    ("link", "user_send_link"),
    ("sticker", "user_send_sticker"),
    ("gif", "user_send_gif"),
    ("audio", "user_send_audio"),
)


class LocationPayloadSerializer(serializers.Serializer):  # noqa
    coordinates = serializers.DictField(child=serializers.DecimalField(max_digits=20, decimal_places=15))


class ImagePayloadSerializer(serializers.Serializer):  # noqa
    thumbnail = serializers.URLField()
    url = serializers.URLField()


class LinkPayloadSerializer(serializers.Serializer):  # noqa
    thumbnail = serializers.URLField()
    description = serializers.CharField(max_length=1024)
    url = serializers.URLField()


class StickerPayloadSerializer(serializers.Serializer):  # noqa
    id = serializers.CharField(max_length=255)
    url = serializers.URLField()


class GifPayloadSerializer(serializers.Serializer):  # noqa
    thumbnail = serializers.URLField()
    url = serializers.URLField()


class AudioPayloadSerializer(serializers.Serializer):  # noqa
    url = serializers.URLField()


class AttachmentSerializer(serializers.Serializer):  # noqa
    type = serializers.ChoiceField(choices=["location", "image", "link", "sticker", "gif", "audio"])
    payload = serializers.DictField()

    def validate(self, data):
        type_mapping = {
            "location": LocationPayloadSerializer,
            "image": ImagePayloadSerializer,
            "link": LinkPayloadSerializer,
            "sticker": StickerPayloadSerializer,
            "gif": GifPayloadSerializer,
            "audio": AudioPayloadSerializer,
        }
        payload_type = data.get("type")
        payload_data = data.get("payload")

        if payload_type in type_mapping:
            serializer = type_mapping[payload_type](data=payload_data)
            if not serializer.is_valid():
                raise serializers.ValidationError({f"payload for type {payload_type}": serializer.errors})
        else:
            raise serializers.ValidationError({"type": f"Unsupported type: {payload_type}"})

        return data


class SenderSerializer(serializers.Serializer):  # noqa
    id = serializers.CharField(max_length=255)


class RecipientSerializer(serializers.Serializer):  # noqa
    id = serializers.CharField(max_length=255)


class FollowerSerializer(serializers.Serializer):  # noqa
    id = serializers.CharField(max_length=255)


class MessageSerializer(serializers.Serializer):  # noqa
    msg_id = serializers.CharField(max_length=255, required=False)
    text = serializers.CharField(max_length=1024, required=False)
    attachments = AttachmentSerializer(many=True, required=False)
    msg_ids = serializers.ListField(child=serializers.CharField(max_length=255), required=False)
