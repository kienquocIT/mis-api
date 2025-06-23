from datetime import datetime
import magic
from django.conf import settings
from rest_framework import serializers
from apps.shared import HrMsg, TypeCheck, AttMsg, FORMATTING, BaseMsg
from .models import Files, PublicFiles, Folder, FolderPermission


def update_folder_permission(perm):
    folder_id = str(perm['folder'].id)
    default = {
        'folder_id': folder_id,
        'employee_list': perm['employee_list'],
        'group_list': perm['group_list'],
        'folder_perm_list': perm['folder_perm_list'],
        'file_in_perm_list': perm['file_in_perm_list'],
        'employee_or_group': perm['employee_or_group'],
        'exp_date': perm.get('exp_date', None),
        'capability_list': perm['capability_list'],
        'is_apply_sub': perm.get('is_apply_sub', False),
    }
    _, _ = FolderPermission.objects.update_or_create(
        folder_id=folder_id,
        defaults={
            **default,
            'employee_created': perm['folder'].employee_created,
            'date_created': datetime.now(),
        }
    )

    return True


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
                            if settings.FILE_ENABLE_MAGIC_CHECK is True:
                                # move control to first buffer file
                                attrs.seek(0)
                                # if mine type of magic != InMemoryUploadedFile.content_type => raise danger
                                magic_check_mime = magic.from_buffer(attrs.read(), mime=True)
                                if magic_check_mime == attrs.content_type:
                                    return attrs
                                raise serializers.ValidationError({'file': AttMsg.FILE_TYPE_DETECT_DANGER})
                            return attrs
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
        fields = ('file', 'remarks', 'folder')


class FilesDetailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()  # Add a custom field for the file URL
    employee_created = serializers.SerializerMethodField()  # Add a custom field for the file URL

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
            'url',
            'date_modified',
            'employee_created'
        )

    @classmethod
    def get_url(cls, obj):
        # Return the file's URL
        return obj.get_url()

    @classmethod
    def get_employee_created(cls, obj):
        # Return the file's URL
        return {'id': str(obj.employee_created.id), 'full_name': obj.employee_created.get_full_name()}


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


class FileDeleteAllSerializer(serializers.ModelSerializer):
    id_list = serializers.ListField(
        child=serializers.UUIDField(), help_text='ID list record delete data'
    )

    @staticmethod
    def validate_id_list(attrs):
        id_list = Files.objects.filter(id__in=attrs)
        if id_list.count() == len(attrs):
            return id_list
        raise serializers.ValidationError({'file': AttMsg.FILE_DELETE_ERROR})

    class Meta:
        model = Files
        fields = ('id_list',)


class PublicFilesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicFiles
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
                if attrs and hasattr(attrs, 'size'):
                    if isinstance(attrs.size, int) and attrs.size < settings.FILE_SIZE_UPLOAD_LIMIT:
                        #skip checking if company has avaiable storage
                        if settings.FILE_ENABLE_MAGIC_CHECK is True:
                            # move control to first buffer file
                            attrs.seek(0)
                            # if mine type of magic != InMemoryUploadedFile.content_type => raise danger
                            magic_check_mime = magic.from_buffer(attrs.read(), mime=True)
                            if magic_check_mime == attrs.content_type:
                                return attrs
                            raise serializers.ValidationError({'file': AttMsg.FILE_TYPE_DETECT_DANGER})
                        return attrs
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
        instance = PublicFiles.objects.create(
            **validated_data
        )
        return instance

    class Meta:
        model = PublicFiles
        fields = ('file', 'remarks')


class PublicFilesDetailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()  # Add a custom field for the file URL

    class Meta:
        model = PublicFiles
        fields = (
            'id',
            'file_name',
            'file_size',
            'file_type',
            'remarks',
            'url'
        )

    @classmethod
    def get_url(cls, obj):
        # Return the file's URL
        return obj.get_url()


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
                            if settings.FILE_ENABLE_MAGIC_CHECK is True:
                                attrs.seek(0)
                                mine_detect = magic.from_buffer(attrs.read(), mime=True)
                                if mine_detect == attrs.content_type:
                                    return attrs
                                raise serializers.ValidationError({'file': AttMsg.FILE_TYPE_DETECT_DANGER})
                            return attrs
                        raise serializers.ValidationError({'file': AttMsg.FILE_IS_NOT_IMAGE})
                    file_size_limit = AttMsg.FILE_SIZE_SHOULD_BE_LESS_THAN_X.format(
                        FORMATTING.size_to_text(settings.FILE_SIZE_WEB_BUILDER)
                    )
                    raise serializers.ValidationError({'file': file_size_limit})
                raise serializers.ValidationError({'file': AttMsg.FILE_NO_DETECT_SIZE})
            raise serializers.ValidationError(
                {
                    'file': AttMsg.WEB_BUILDER_USED_OVER_SIZE.format(
                        used_size=FORMATTING.size_to_text(settings.FILE_WEB_BUILDER_LIMIT_SIZE)
                    )
                }
            )
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
    employee_inherit = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            "full_name": obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    @classmethod
    def get_files(cls, obj):
        files = obj.files_folder.select_related('employee_created').all()
        file_lst = []
        for file in files:
            file_lst.append({
                'id': str(file.id),
                'file_name': file.file_name,
                'file_size': file.file_size,
                'file_type': file.file_type,
                'date_created': file.date_created,
                'employee_created': {
                    'id': str(file.employee_created),
                    'full_name': file.employee_created.get_full_name()
                } if file.employee_created else {},
                'remarks': file.remarks,
            })
        return file_lst

    @classmethod
    def get_parent_n(cls, obj):
        return {'id': obj.parent_n_id, 'title': obj.parent_n.title, 'code': obj.parent_n.code} if obj.parent_n else {}

    class Meta:
        model = Folder
        fields = (
            'id',
            'title',
            'parent_n',
            'employee_inherit',
            'date_modified',
            'files',
        )


class FolderDetailSerializer(serializers.ModelSerializer):
    parent_n = serializers.SerializerMethodField()
    child_n = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = (
            'id',
            'title',
            'parent_n',
            'child_n',
            'files',
            'date_created',
            'date_modified',
            'employee_inherit',
        )

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    @classmethod
    def get_parent_n(cls, obj):
        return {'id': obj.parent_n_id, 'title': obj.parent_n.title, 'code': obj.parent_n.code} if obj.parent_n else {}

    @classmethod
    def get_child_n(cls, obj):
        return [
            {
                'id': child.id, 'title': child.title,
                'employee_inherit': {
                    'id': child.employee_inherit_id,
                    'full_name': child.employee_inherit.get_full_name()
                } if child.employee_inherit else {},
                'date_modified': child.date_modified,
            }
            for child in obj.folder_parent_n.select_related('employee_inherit').all()
        ]

    @classmethod
    def get_files(cls, obj):
        return [
            {
                'id': f.id, 'file_name': f.file_name,
                'file_size': f.file_size, 'file_type': f.file_type,
                'date_created': f.date_created, 'remarks': f.remarks,
                'employee_inherit': {
                    'id': f.employee_created_id,
                    'full_name': f.employee_created.get_full_name()
                } if f.employee_created else {}
            }
            for f in obj.files_folder.select_related('employee_created').all()
        ]


class FolderDeleteAllSerializer(serializers.ModelSerializer):
    id_list = serializers.ListField(
        child=serializers.UUIDField(), help_text='ID list record delete data'
    )

    @classmethod
    def validate_id_list(cls, attrs):
        id_list = Folder.objects.filter(id__in=attrs)
        if id_list.count() == len(attrs):
            return id_list
        raise serializers.ValidationError({'folder': BaseMsg.VALUE_DELETE_LIST_ERROR})

    class Meta:
        model = Folder
        fields = '__all__'


class FolderCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    parent_n = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Folder
        fields = (
            'title',
            'parent_n',
            'is_owner',
            'is_admin'
        )

    @classmethod
    def validate_parent_n(cls, value):
        try:
            if value is None:
                return value
            return Folder.objects.get(id=value)
        except Folder.DoesNotExist:
            raise serializers.ValidationError({'folder': AttMsg.FOLDER_NOT_EXIST})

    def create(self, validated_data):
        folder = Folder.objects.create(**validated_data)
        return folder


class PermissionFolderSerializer(serializers.ModelSerializer):

    @classmethod
    def validate_folder(cls, attrs):
        if not attrs:
            raise serializers.ValidationError({'folder': AttMsg.FOLDER_NOT_EXIST})
        return attrs

    @classmethod
    def validate_employee_list(cls, attrs):
        if not attrs:
            raise serializers.ValidationError({'employee_list': AttMsg.EMPLOYEE_LIST_NOT_EXIST})
        return attrs

    @classmethod
    def validate_group_list(cls, attrs):
        if not attrs:
            raise serializers.ValidationError({'employee_list': AttMsg.GROUP_LIST_NOT_EXIST})
        return attrs

    @classmethod
    def validate_capability_list(cls, attrs):
        if not attrs:
            raise serializers.ValidationError({'capability_list': AttMsg.CAPABILITY_NOT_EXIST})
        return attrs

    class Meta:
        model = FolderPermission
        fields = (
            'folder',
            'employee_list',
            'group_list',
            'folder_perm_list',
            'file_in_perm_list',
            'employee_or_group',
            'exp_date',
            'capability_list',
            'is_apply_sub'
        )


class FolderUpdateSerializer(serializers.ModelSerializer):
    parent_n = serializers.UUIDField(required=False, allow_null=True)
    permission_obj = PermissionFolderSerializer(required=False, allow_null=True)

    class Meta:
        model = Folder
        fields = (
            'title',
            'parent_n',
            'permission_obj',
        )

    @classmethod
    def validate_parent_n(cls, value):
        try:
            if value is None:
                return value
            return Folder.objects.get(id=value)
        except Folder.DoesNotExist:
            raise serializers.ValidationError({'folder': AttMsg.FOLDER_NOT_EXIST})

    def update(self, instance, validated_data):
        permission_obj = validated_data.pop('permission_obj', None)
        if permission_obj:
            update_folder_permission(permission_obj)
        # update instance
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class FolderUploadFileSerializer(serializers.ModelSerializer):
    folder = serializers.UUIDField(required=False, allow_null=True)

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
                            if settings.FILE_ENABLE_MAGIC_CHECK is True:
                                # move control to first buffer file
                                attrs.seek(0)
                                # if mine type of magic != InMemoryUploadedFile.content_type => raise danger
                                if magic.from_buffer(attrs.read(), mime=True) == attrs.content_type:
                                    return attrs
                                raise serializers.ValidationError({'file': AttMsg.FILE_TYPE_DETECT_DANGER})
                            return attrs
                        raise serializers.ValidationError({'file': msg_err})
                    file_size_limit = AttMsg.FILE_SIZE_SHOULD_BE_LESS_THAN_X.format(
                        FORMATTING.size_to_text(settings.FILE_SIZE_UPLOAD_LIMIT)
                    )
                    raise serializers.ValidationError({'file': file_size_limit})
                raise serializers.ValidationError({'file': AttMsg.FILE_NO_DETECT_SIZE})
            raise serializers.ValidationError({'file': HrMsg.EMPLOYEE_REQUIRED})
        raise serializers.ValidationError({'employee': HrMsg.EMPLOYEE_REQUIRED})

    @classmethod
    def validate_folder(cls, value):
        try:
            return Folder.objects.get(id=value)
        except Folder.DoesNotExist:
            raise serializers.ValidationError({'folder': AttMsg.FOLDER_NOT_EXIST})

    def validate(self, attrs):
        file_memory = attrs['file']
        attrs['file_name'] = file_memory.name
        attrs['file_size'] = file_memory.size
        attrs['file_type'] = file_memory.content_type
        return attrs

    def create(self, validated_data):
        instance = Files.objects.create(**validated_data)
        return instance

    class Meta:
        model = Files
        fields = ('file', 'remarks', 'folder')
