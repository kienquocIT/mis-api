from rest_framework import serializers

from apps.core.comment.models import Comments
from apps.shared import DisperseModel, HrMsg


class CommentListSerializer(serializers.ModelSerializer):
    employee_created = serializers.SerializerMethodField()

    @classmethod
    def get_employee_created(cls, obj):
        if obj.employee_created and hasattr(obj.employee_created, 'get_detail_minimal'):
            return obj.employee_created.get_detail_minimal()
        return {}

    class Meta:
        model = Comments
        fields = (
            'id', 'doc_id', 'application', 'contents', 'employee_created', 'date_created',
            'children_count', 'mentions', 'mentions_data', 'replies_persons', 'replies_latest',
        )


class CommentCreateSerializer(serializers.ModelSerializer):
    mentions = serializers.ListField(
        required=False, default=[],
        child=serializers.UUIDField(),
    )

    @classmethod
    def validate_mentions(cls, attrs):
        obj_employee_count = DisperseModel(app_model='hr.Employee').get_model().objects.filter_current(
            id__in=attrs, fill__tenant=True, fill__company=True
        ).count()
        if obj_employee_count == len(attrs):
            return [str(idx) for idx in attrs]
        raise serializers.ValidationError({
            'mentions': HrMsg.EMPLOYEE_SOME_NOT_FOUND
        })

    class Meta:
        model = Comments
        fields = ('mentions', 'contents', 'contents_txt')
