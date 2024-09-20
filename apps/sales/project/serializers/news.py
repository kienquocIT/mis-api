from uuid import uuid4

from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.sales.project.models import ProjectNews, ProjectNewsComment, ProjectNewsCommentMentions
from apps.sales.project.msg import ProjectMsg
from apps.shared import TypeCheck, BaseMsg


class ProjectNewsListSerializer(serializers.ModelSerializer):
    application_id = serializers.SerializerMethodField()

    @classmethod
    def get_application_id(cls, obj):
        if obj.application:
            return {
                'id': obj.application.id,
                'title': obj.application.title,
                'app_label': obj.application.app_label,
                'model_code': obj.application.model_code,
            }
        return {}

    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit and hasattr(obj.employee_inherit, 'get_detail_minimal'):
            return obj.employee_inherit.get_detail_minimal()
        return {}

    class Meta:
        model = ProjectNews
        fields = (
            'id', 'title', 'msg',
            'document_id', 'document_title', 'application_id',
            'date_created',
            'employee_inherit',
        )


class ProjectNewsCommentListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit and hasattr(obj.employee_inherit, 'get_detail_minimal'):
            return obj.employee_inherit.get_detail_minimal()
        return {}

    class Meta:
        model = ProjectNewsComment
        fields = (
            'id', 'msg', 'mentions',
            'date_created',
            'employee_inherit',
            'reply_from_id',
        )


class ProjectNewsCommentCreateSerializer(serializers.ModelSerializer):
    mentions = serializers.ListSerializer(
        child=serializers.UUIDField(), allow_empty=True, required=False
    )

    @classmethod
    def validate_mentions(cls, attrs):
        if attrs and isinstance(attrs, list):
            if TypeCheck.check_uuid_list(attrs):
                emp_objs = Employee.objects.filter_current(id__in=attrs)
                if emp_objs.count() == len(attrs):
                    return emp_objs
            raise serializers.ValidationError(
                {
                    'mentions': ProjectMsg.MENTIONS_NOT_FOUND,
                }
            )
        return []

    reply_from = serializers.UUIDField(allow_null=True, required=False)

    @classmethod
    def validate_reply_from(cls, attrs):
        if attrs and TypeCheck.check_uuid(attrs):
            try:
                prev_obj = ProjectNewsComment.objects.get_current(fill__tenant=True, fill__company=True, pk=attrs)
            except ProjectNewsComment.DoesNotExist:
                pass
            else:
                if prev_obj.reply_from is None:
                    return prev_obj
                raise serializers.ValidationError({
                    'reply_from': ProjectMsg.REPLY_NOT_SUPPORT
                })
        raise serializers.ValidationError({
            'reply_from': BaseMsg.REQUIRED
        })

    def create(self, validated_data):
        generate_id = uuid4()
        mentions = validated_data.pop('mentions', [])
        mention_ids = []
        bulk_objs = []
        for obj in mentions:
            mention_ids.append(str(obj.id))
            bulk_objs.append(
                ProjectNewsCommentMentions(
                    comment_id=generate_id,
                    employee=obj,
                )
            )
        instance = ProjectNewsComment.objects.create(**validated_data, mentions=mention_ids, id=generate_id)
        if bulk_objs:
            ProjectNewsCommentMentions.objects.bulk_create(bulk_objs)
        return instance

    class Meta:
        model = ProjectNewsComment
        fields = ('news', 'msg', 'mentions', 'reply_from')


class ProjectNewsCommentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectNewsComment
        fields = ('id', 'msg')


class ProjectNewsCommentUpdateSerializer(serializers.ModelSerializer):
    mentions = serializers.ListSerializer(
        child=serializers.UUIDField(), allow_empty=True, required=False
    )

    @classmethod
    def validate_mentions(cls, attrs):
        if attrs and isinstance(attrs, list):
            if TypeCheck.check_uuid_list(attrs):
                emp_objs = Employee.objects.filter_current(id__in=attrs)
                if emp_objs.count() == len(attrs):
                    return emp_objs
            raise serializers.ValidationError(
                {
                    'mentions': ProjectMsg.MENTIONS_NOT_FOUND,
                }
            )
        return []

    def update(self, instance, validated_data):
        mentions = validated_data.pop('mentions', [])
        mention_ids = []
        bulk_objs = []
        for obj in mentions:
            mention_ids.append(str(obj.id))
            bulk_objs.append(
                ProjectNewsCommentMentions(
                    comment=instance,
                    employee=obj,
                )
            )
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.mentions = mention_ids
        instance.save()
        if bulk_objs:
            old_mentions = ProjectNewsCommentMentions.objects.filter(comment=instance)
            if old_mentions:
                old_mentions.delete()
            ProjectNewsCommentMentions.objects.bulk_create(bulk_objs)
        return instance

    class Meta:
        model = ProjectNewsComment
        fields = ('msg', 'mentions')


class ProjectNewsCommentDetailFlowSerializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()

    @classmethod
    def get_sequence(cls, obj):
        objs = [obj]
        if obj.reply_from:
            objs = [obj.reply_from] + objs
        return ProjectNewsCommentListSerializer(data=objs, many=True).data

    class Meta:
        model = ProjectNewsComment
        fields = ('id', 'sequence')
