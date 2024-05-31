import magic

from django.conf import settings
from rest_framework import serializers
from apps.core.attachments.models import Files, PublicFiles, Folder
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


class PublicFilesUploadSerializer(serializers.ModelSerializer):
    def validate_file(self, attrs):
        user_obj = self.context.get('user_obj', None)
        if user_obj:  # pylint: disable=R1702
            employee_current_id = getattr(user_obj, 'employee_current_id', None)
            if employee_current_id and TypeCheck.check_uuid(employee_current_id):
                return attrs
            raise serializers.ValidationError({'file': HrMsg.EMPLOYEE_REQUIRED})
        raise serializers.ValidationError({'employee': HrMsg.EMPLOYEE_REQUIRED})

    def validate(self, attrs):
        file_memory = attrs['file']
        attrs['file_name'] = file_memory.name
        attrs['file_size'] = file_memory.size
        attrs['file_type'] = file_memory.content_type
        return attrs

    def create(self, validated_data):
        instance = PublicFiles.objects.create(
            **validated_data
        )
        return instance

    class Meta:
        model = PublicFiles
        fields = ('file',)


class PublicFilesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicFiles
        fields = (
            'id',
            'file_name',
            'file_size',
            'file_type',
            'remarks',
        )


class CreateImageWebBuilderInPublicFileListSerializer(PublicFilesUploadSerializer):
    def validate_file(self, attrs):
        user_obj = self.context.get('user_obj', None)
        if user_obj and hasattr(user_obj, 'company_current_id'):  # pylint: disable=R1702
            # valid used with limit of web_builder
            web_builder_used = PublicFiles.get_used_of_web_builder(company_id=user_obj.company_current_id)
            if web_builder_used < settings.FILE_WEB_BUILDER_LIMIT_SIZE:
                attrs = super().validate_file(attrs)
                if attrs and hasattr(attrs, 'size'):
                    if isinstance(attrs.size, int) and attrs.size < settings.FILE_SIZE_WEB_BUILDER:
                        if attrs.content_type.startswith('image/'):
                            attrs.seek(0)
                            mine_detect = magic.from_buffer(attrs.read(), mime=True)
                            if mine_detect == attrs.content_type:
                                return attrs
                            raise serializers.ValidationError({'file': AttMsg.FILE_TYPE_DETECT_DANGER})
                        raise serializers.ValidationError({'file': AttMsg.FILE_IS_NOT_IMAGE})
                    file_size_limit = AttMsg.FILE_SIZE_SHOULD_BE_LESS_THAN_X.format(
                        FORMATTING.size_to_text(settings.FILE_SIZE_WEB_BUILDER)
                    )
                    raise serializers.ValidationError({'file': file_size_limit})
                raise serializers.ValidationError({'file': AttMsg.FILE_NO_DETECT_SIZE})
            raise serializers.ValidationError({'file': AttMsg.WEB_BUILDER_USED_OVER_SIZE.format(
                used_size=FORMATTING.size_to_text(settings.FILE_WEB_BUILDER_LIMIT_SIZE)
            )})
        raise serializers.ValidationError({'employee': HrMsg.EMPLOYEE_REQUIRED})

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['relate_app_code'] = settings.FILE_WEB_BUILDER_RELATE_APP
        return attrs

    def create(self, validated_data):
        instance = PublicFiles.objects.create(
            **validated_data
        )
        return instance


class DetailImageWebBuilderInPublicFileListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    @classmethod
    def get_url(cls, obj):
        return obj.get_url()

    class Meta:
        model = PublicFiles
        fields = (
            'file_name',
            'file_type',
            'url',
        )


# BEGIN FOLDER
class FolderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Folder
        fields = (
            'id',
            'title',
            'parent_n_id',
            'date_created',
            'date_modified',
        )


class FolderDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Folder
        fields = (
            'title',
            'parent_n',
        )


class FolderCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    parent_n = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Folder
        fields = (
            'title',
            'parent_n',
        )

    @classmethod
    def validate_parent_n(cls, value):
        try:
            return Folder.objects.get(id=value)
        except Folder.DoesNotExist:
            raise serializers.ValidationError({'folder': AttMsg.FOLDER_NOT_EXIST})

    def create(self, validated_data):
        folder = Folder.objects.create(**validated_data)
        return folder


class FolderUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, allow_blank=False)
    parent_n = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Folder
        fields = (
            'title',
            'parent_n',
        )

    @classmethod
    def validate_parent_n(cls, value):
        try:
            return Folder.objects.get(id=value)
        except Folder.DoesNotExist:
            raise serializers.ValidationError({'folder': AttMsg.FOLDER_NOT_EXIST})

    def update(self, instance, validated_data):
        # update instance
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class FolderFilesListSerializer(serializers.ModelSerializer):
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
