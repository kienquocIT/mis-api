from rest_framework import serializers

from apps.core.comment.models import Comments


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
            'id', 'doc_id', 'application', 'mentions', 'contents', 'employee_created', 'date_created', 'children_count'
        )


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ('mentions', 'contents')
