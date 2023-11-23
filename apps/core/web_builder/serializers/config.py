from rest_framework import serializers

from apps.core.web_builder.models import PageBuilder
from apps.shared.translations import WebBuilderMsg


class PageBuilderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBuilder
        fields = ('id', 'title', 'remarks', 'page_title', 'page_path', 'is_publish')


class PageBuilderCreateSerializer(serializers.ModelSerializer):
    def validate_page_path(self, attrs):
        if (
                attrs.startswith('system')
                or attrs.startswith('/system')
                or attrs.startswith('admin')
                or attrs.startswith('/admin')
        ):
            raise serializers.ValidationError({'page_path': WebBuilderMsg.PATH_NOT_ALLOWED_USE})

        if not attrs.startswith('/'):
            raise serializers.ValidationError({'page_path': WebBuilderMsg.PATH_START_WITH_FORWARD_SLASH})

        company_current_id = self.context.get('company_current_id', None)
        if not company_current_id:
            raise serializers.ValidationError({'base': WebBuilderMsg.FILTER_COMPANY_NOT_EXIST})

        if PageBuilder.objects.filter(company_id=company_current_id, page_path=attrs).exists():
            raise serializers.ValidationError({'page_path': WebBuilderMsg.PATH_EXIST})

        return attrs

    class Meta:
        model = PageBuilder
        fields = ('id', 'title', 'remarks', 'page_title', 'page_path', 'is_publish')


class PageBuilderDetailViewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBuilder
        fields = (
            'page_title', 'is_publish',
            'page_html', 'page_css', 'page_js',
            'is_publish',
        )


class PageBuilderDetailSerializer(serializers.ModelSerializer):
    menus = serializers.SerializerMethodField()

    @classmethod
    def get_menus(cls, obj):  # pylint: disable=W0613
        return [
            {
                'id': page_obj.page_path,
                'name': page_obj.title,
            } for page_obj in PageBuilder.objects.filter_current(fill__tenant=True, fill__company=True)
        ]

    class Meta:
        model = PageBuilder
        fields = (
            'id', 'title', 'remarks', 'page_title', 'page_path', 'is_publish',
            'page_html', 'page_css', 'page_js', 'page_full',
            'menus',
        )


class PageBuilderUpdateSerializer(serializers.ModelSerializer):
    def validate_page_path(self, attrs):
        if (
                attrs.startswith('system')
                or attrs.startswith('/system')
                or attrs.startswith('admin')
                or attrs.startswith('/admin')
        ):
            raise serializers.ValidationError({'page_path': WebBuilderMsg.PATH_NOT_ALLOWED_USE})

        if not attrs.startswith('/'):
            raise serializers.ValidationError({'page_path': WebBuilderMsg.PATH_START_WITH_FORWARD_SLASH})

        company_current_id = self.context.get('company_current_id', None)
        if not company_current_id:
            raise serializers.ValidationError({'base': WebBuilderMsg.FILTER_COMPANY_NOT_EXIST})

        page_builder_kw = {
            'company_id': company_current_id,
            'page_path': attrs,
        }
        if PageBuilder.objects.filter(**page_builder_kw).exclude(pk=self.instance.id).exists():
            raise serializers.ValidationError({'page_path': WebBuilderMsg.PATH_EXIST})

        return attrs

    class Meta:
        model = PageBuilder
        fields = (
            'title', 'remarks', 'page_title', 'page_path', 'is_publish',
            'page_html', 'page_css', 'page_js', 'page_full',
        )
