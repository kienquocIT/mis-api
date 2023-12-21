import magic

from django.conf import settings
from rest_framework import serializers
from apps.core.attachments.models import Files
from apps.shared import HrMsg, TypeCheck, AttMsg, FORMATTING


class FilesUploadSerializer(serializers.ModelSerializer):
    def validate_file(self, attrs):
        user_obj = self.context.get('user_obj', None)
        if user_obj:  # pylint: disable=R1702
            employee_current_id = getattr(user_obj, 'employee_current_id', None)
            if employee_current_id and TypeCheck.check_uuid(employee_current_id):
                if attrs and hasattr(attrs, 'size'):
                    if isinstance(attrs.size, int) and attrs.size < settings.FILE_SIZE_UPLOAD_LIMIT:
                        # check employee has available storage
                        state_available, _code_err, msg_err = Files.check_available_size_employee(
                            employee_id=employee_current_id, new_size=attrs.size
                        )
                        if state_available is True:
                            # move control to first buffer file
                            attrs.seek(0)
                            # if mine type of magic != InMemoryUploadedFile.content_type => raise danger
                            if magic.from_buffer(attrs.read(), mime=True) == attrs.content_type:
                                return attrs
                            raise serializers.ValidationError({'file': AttMsg.FILE_TYPE_DETECT_DANGER})
                        raise serializers.ValidationError({'file': msg_err})
                    file_size_limit = AttMsg.FILE_SIZE_SHOULD_BE_LESS_THAN_X.format(
                        FORMATTING.size_to_text(settings.FILE_SIZE_UPLOAD_LIMIT)
                    )
                    raise serializers.ValidationError({'file': file_size_limit})
                raise serializers.ValidationError({'file': AttMsg.FILE_NO_DETECT_SIZE})
            raise serializers.ValidationError({'file': HrMsg.EMPLOYEE_REQUIRED})
        raise serializers.ValidationError({'employee': HrMsg.EMPLOYEE_REQUIRED})

    def validate(self, attrs):
        file_memory = attrs['file']
        attrs['file_name'] = file_memory.name
        attrs['file_size'] = file_memory.size
        attrs['file_type'] = file_memory.content_type
        return attrs

    def create(self, validated_data):
        instance = Files.objects.create(
            **validated_data
        )
        return instance

    class Meta:
        model = Files
        fields = ('file', 'remarks')


class FilesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = (
            'id',
            'relate_app',
            'relate_app_code',
            'relate_doc_id',
            'file_name',
            'file_size',
            'file_type',
            'remarks',
        )


class FilesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = (
            'id',
            'file_name',
            'file_size',
            'file_type',
            'date_created',
            'remarks',
        )
