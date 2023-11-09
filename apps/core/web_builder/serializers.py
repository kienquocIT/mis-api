from rest_framework import serializers

from apps.core.web_builder.models import PageBuilder


class PageBuilderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBuilder
        fields = ('id', 'title', 'remarks', 'page_title', 'page_path', 'is_publish')


class PageBuilderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBuilder
        fields = ('id', 'title', 'remarks', 'page_title', 'page_path', 'is_publish')


class PageBuilderDetailViewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBuilder
        fields = (
            'page_title', 'is_publish',
            'page_html', 'page_css', 'page_js',
        )


class PageBuilderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBuilder
        fields = (
            'id', 'title', 'remarks', 'page_title', 'page_path', 'is_publish',
            'page_html', 'page_css', 'page_js', 'page_full',
        )


class PageBuilderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBuilder
        fields = (
            'title', 'remarks', 'page_title', 'page_path', 'is_publish',
            'page_html', 'page_css', 'page_js', 'page_full',
        )
