from uuid import uuid4

from django.utils import timezone
from rest_framework import serializers

from apps.core.forms.i18n import FormMsg
from apps.core.forms.models import Form, FormPublished, FormPublishedEntries
from apps.core.forms.validation import FormValidation

from apps.core.mailer.handle_html import HTMLController


class EntriesDefaultShow(serializers.Serializer):  # noqa
    display_referrer_name = serializers.BooleanField(default=False)
    display_creator = serializers.BooleanField(default=False)


class FormListSerializer(serializers.ModelSerializer):
    publish = serializers.SerializerMethodField()

    @classmethod
    def get_publish(cls, obj):
        if obj.form_published:
            return {
                'is_active': obj.form_published.is_active,
                'is_public': obj.form_published.is_public,
                'is_iframe': obj.form_published.is_iframe,
                'id': obj.form_published.id,
                'code': obj.form_published.code,
            }
        return {}

    class Meta:
        model = Form
        fields = ('id', 'title', 'remark', 'publish', 'is_active')


class FormDetailSerializer(serializers.ModelSerializer):
    published = serializers.SerializerMethodField()

    @classmethod
    def get_published(cls, obj):
        try:
            obj_published = FormPublished.objects.get(form=obj)
            return FormPublishedDetailSerializer(instance=obj_published).data
        except FormPublished.DoesNotExist:
            pass
        return {}

    display_referrer_name = serializers.SerializerMethodField()

    @classmethod
    def get_display_referrer_name(cls, obj):
        return obj.entries_default_show.get('display_referrer_name', False)

    display_creator = serializers.SerializerMethodField()

    @classmethod
    def get_display_creator(cls, obj):
        return obj.entries_default_show.get('display_creator', False)

    class Meta:
        model = Form
        fields = (
            'id', 'title', 'remark', 'label_placement', 'instruction_placement',
            'authentication_required', 'submit_only_one', 'edit_submitted',
            'display_referrer_name', 'display_creator',
            'theme_selected', 'theme_assets',
            'configs_order', 'configs',
            'published'
        )


class FormDetailForEntriesSerializer(serializers.ModelSerializer):
    configs_order = serializers.SerializerMethodField()

    @classmethod
    def get_configs_order(cls, obj):
        if isinstance(obj.configs_order, list):
            if 'head-sortable' in obj.configs_order:
                obj.configs_order.remove('head-sortable')
            return obj.configs_order
        return []

    display_referrer_name = serializers.SerializerMethodField()

    @classmethod
    def get_display_referrer_name(cls, obj):
        return obj.entries_default_show.get('display_referrer_name', False)

    display_creator = serializers.SerializerMethodField()

    @classmethod
    def get_display_creator(cls, obj):
        return obj.entries_default_show.get('display_creator', False)

    class Meta:
        model = Form
        fields = (
            'id', 'title', 'remark',
            'authentication_required', 'submit_only_one', 'edit_submitted',
            'display_referrer_name', 'display_creator',
            'configs_order', 'configs'
        )


class FormCreateSerializer(serializers.ModelSerializer):
    configs = serializers.DictField(
        child=serializers.JSONField(),
        allow_empty=True, allow_null=True,
    )

    @classmethod
    def validate_configs(cls, attrs):
        if isinstance(attrs, dict):
            return attrs
        raise serializers.ValidationError(
            {
                'configs': 'Contents should be format'
            }
        )

    theme_assets = serializers.JSONField(required=False)

    @classmethod
    def validate_theme_assets(cls, attrs):
        ctx = {}

        if not attrs:
            return {}

        css = attrs.get('css', [])
        if css and isinstance(css, list):
            ctx['css'] = []
            for item in css:
                if item.startswith('/static/'):
                    ctx['css'].append(item)

        js = attrs.get('js', [])
        if js and isinstance(js, list):
            ctx['js'] = []
            for item in js:
                if item.startswith('/static/'):
                    ctx['js'].append(item)

        return ctx

    html_text = serializers.CharField(required=False)

    configs_order = serializers.ListSerializer(
        child=serializers.CharField(), allow_empty=True, allow_null=True, required=False
    )

    entries_default_show = EntriesDefaultShow()

    def create(self, validated_data):
        html_text = validated_data.pop('html_text', None)

        configs_order = validated_data.pop('configs_order', [])
        configs = validated_data.pop('configs', {})

        valid_cls = FormValidation(configs_order=configs_order, configs=configs)
        validated_data['configs_order'] = configs_order
        validated_data['configs'] = valid_cls.configs_validated

        instance = Form.objects.create(**validated_data)
        published_obj, _created = instance.get_or_create_publish()
        if html_text:
            published_obj.html_text = html_text
            published_obj.save(update_fields=['html_text'])

        return instance

    class Meta:
        model = Form
        fields = (
            'title', 'remark', 'label_placement', 'instruction_placement',
            'authentication_required', 'submit_only_one', 'edit_submitted',
            'entries_default_show',
            'theme_selected', 'theme_assets',
            'configs_order', 'configs',
            'html_text',
        )


class FormUpdateSerializer(serializers.ModelSerializer):
    configs = serializers.DictField(
        child=serializers.JSONField(),
        allow_empty=True, allow_null=True,
    )

    @classmethod
    def validate_configs(cls, attrs):
        if isinstance(attrs, dict):
            return attrs
        raise serializers.ValidationError(
            {
                'configs': 'Contents should be format'
            }
        )

    html_text = serializers.CharField(required=False)

    configs_order = serializers.ListSerializer(
        child=serializers.CharField(), allow_empty=True, allow_null=True, required=False
    )

    entries_default_show = EntriesDefaultShow()

    def update(self, instance, validated_data):
        html_text = validated_data.pop('html_text', None)

        configs_order = validated_data.pop('configs_order', instance.configs_order)
        configs = validated_data.pop('configs', instance.configs)
        valid_cls = FormValidation(configs_order=configs_order, configs=configs)
        validated_data['configs_order'] = configs_order
        validated_data['configs'] = valid_cls.configs_validated

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        try:
            published_obj = FormPublished.objects.get_current(fill__company=True, form=instance)
            if html_text:
                published_obj.html_text = html_text
                published_obj.save(update_fields=['html_text'])
        except FormPublished.DoesNotExist:
            pass

        return instance

    class Meta:
        model = Form
        fields = (
            'title', 'remark', 'label_placement', 'instruction_placement',
            'authentication_required', 'submit_only_one', 'edit_submitted',
            'entries_default_show',
            'configs_order', 'configs',
            'html_text'
        )


class FormUpdateThemeSerializer(serializers.ModelSerializer):
    theme_assets = serializers.JSONField(required=False)

    @classmethod
    def validate_theme_assets(cls, attrs):
        ctx = {}

        if not attrs:
            return {}

        css = attrs.get('css', [])
        if css and isinstance(css, list):
            ctx['css'] = []
            for item in css:
                if item.startswith('/static/'):
                    ctx['css'].append(item)

        js = attrs.get('js', [])
        if js and isinstance(js, list):
            ctx['js'] = []
            for item in js:
                if item.startswith('/static/'):
                    ctx['js'].append(item)

        return ctx

    class Meta:
        model = Form
        fields = ('theme_selected', 'theme_assets',)


class FormUpdateTurnOffSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=False)
    is_public = serializers.BooleanField(required=False)
    is_iframe = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        try:
            published_obj = FormPublished.objects.get(form=instance)
        except FormPublished.DoesNotExist:
            published_obj = None

        is_active = validated_data.pop('is_active', instance.is_active)
        instance.is_active = is_active
        instance.save(update_fields=['is_active'])
        if published_obj:
            published_obj.is_active = is_active

            is_public = validated_data.pop('is_public', published_obj.is_public)
            published_obj.is_public = is_public

            is_iframe = validated_data.pop('is_iframe', published_obj.is_iframe)
            published_obj.is_iframe = is_iframe

            published_obj.save(update_fields=['is_active', 'is_public', 'is_iframe'])
        return instance

    class Meta:
        model = Form
        fields = ('is_active', 'is_public', 'is_iframe')


class FormUpdateDuplicateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        published, _created = instance.get_or_create_publish()

        instance.id = uuid4()
        instance.title = f'[{str(FormMsg.A_COPY)}] {instance.title}'
        instance.date_created = timezone.now()
        instance.save()

        published_new, _created = instance.get_or_create_publish()
        published_new.update_same_obj(published)
        published_new.save()

        return instance

    class Meta:
        model = Form
        fields = ()


class FormPublishedDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormPublished
        fields = (
            'id', 'date_publish_start', 'date_publish_finish',
            'is_active', 'code',
            'is_public', 'is_iframe'
        )


class FormPublishedUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormPublished
        fields = ('is_public', 'is_iframe')


class FormPublishedRuntimeDetailSerializer(serializers.ModelSerializer):
    theme_assets = serializers.SerializerMethodField()

    @classmethod
    def get_theme_assets(cls, obj):
        return obj.form.theme_assets

    form_title = serializers.SerializerMethodField()

    @classmethod
    def get_form_title(cls, obj):
        return obj.form.title

    form_remark = serializers.SerializerMethodField()

    @classmethod
    def get_form_remark(cls, obj):
        return obj.form.remark

    company_title = serializers.SerializerMethodField()

    @classmethod
    def get_company_title(cls, obj):
        if obj.company:
            return obj.company.title
        return ''

    company_logo = serializers.SerializerMethodField()

    @classmethod
    def get_company_logo(cls, obj):
        if obj.company and obj.company.logo:
            return obj.company.logo.url
        return None

    html_text = serializers.SerializerMethodField()

    @classmethod
    def get_html_text(cls, obj):
        html_text = HTMLController.unescape(obj.html_text)
        return html_text

    edit_submitted = serializers.SerializerMethodField()

    @classmethod
    def get_edit_submitted(cls, obj):
        return obj.form.edit_submitted

    submitted_data = serializers.SerializerMethodField()

    def get_submitted_data(self, obj):  # pylint: disable=W0611,W0613
        entry_obj = self.context.get('entry_obj', None)
        if entry_obj:
            return {
                'id': entry_obj.id,
                'body_data': entry_obj.body_data,
            }
        return None

    class Meta:
        model = FormPublished
        fields = (
            'html_text', 'theme_assets',
            'form_title', 'form_remark',
            'company_title', 'company_logo',
            'edit_submitted',
            'is_public', 'is_iframe',
            'submitted_data',
        )


class FormPublishedEntriesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormPublishedEntries
        fields = ('id',)


class FormPublishedEntriesCreateSerializer(serializers.ModelSerializer):
    def validate_body_data(self, attrs):
        published_obj = self.context['published_obj']
        if published_obj:
            if attrs and isinstance(attrs, dict):
                return attrs
            raise serializers.ValidationError(
                {
                    'detail': FormMsg.FORM_DATA_CORRECT_TYPE,
                }
            )
        raise serializers.ValidationError(
            {
                'detail': FormMsg.FORM_NOT_FOUND,
            }
        )

    def validate(self, attrs):
        published_obj = self.context['published_obj']
        user_obj = self.context.get('user_obj', None)
        body_data = attrs.pop('body_data', {})
        if published_obj:
            if published_obj.form.authentication_required is True:
                if not user_obj:
                    raise serializers.ValidationError(
                        {
                            'detail': FormMsg.FORM_REQUIRE_AUTHENTICATED,
                        }
                    )
                if published_obj.form.submit_only_one is True:
                    submitted = FormPublishedEntries.objects.filter(published=published_obj, user_created=user_obj)
                    if submitted.exists():
                        raise serializers.ValidationError({
                            'detail': FormMsg.FORM_SUBMIT_ONLY_ONE_PER_USER,
                        })

            cls = FormValidation(configs_order=published_obj.form.configs_order, configs=published_obj.form.configs)
            attrs['body_data'] = cls.runtime__valid(body_data=body_data)
        return attrs

    def create(self, validated_data):
        published_obj = self.context['published_obj']
        user_obj = self.context.get('user_obj', None)
        if published_obj:
            create_data = {
                **validated_data,
                'published': published_obj,
                'tenant': published_obj.tenant,
                'company': published_obj.company,
                'employee_created_id': user_obj.employee_current_id if user_obj else None,
                'user_created': user_obj,
            }
            instance = FormPublishedEntries.objects.create(**create_data)
            return instance
        raise serializers.ValidationError(
            {
                'detail': FormMsg.FORM_NOT_FOUND,
            }
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    class Meta:
        model = FormPublishedEntries
        fields = ('body_data', 'ref_name', 'meta_data')


class FormPublishedEntriesUpdateSerializer(FormPublishedEntriesCreateSerializer):
    def validate(self, attrs):
        published_obj = self.context['published_obj']
        user_obj = self.context.get('user_obj', None)
        body_data = attrs.pop('body_data', {})
        if published_obj:
            if published_obj.form.authentication_required is True:
                if not user_obj:
                    raise serializers.ValidationError(
                        {
                            'detail': FormMsg.FORM_REQUIRE_AUTHENTICATED,
                        }
                    )
                if published_obj.form.edit_submitted is not True:
                    raise serializers.ValidationError({
                        'detail': FormMsg.FORM_ENTRY_EDIT_DENY,
                    })

            cls = FormValidation(configs_order=published_obj.form.configs_order, configs=published_obj.form.configs)
            attrs['body_data'] = cls.runtime__valid(body_data=body_data)
        return attrs

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    class Meta:
        model = FormPublishedEntries
        fields = ('body_data', 'ref_name', 'meta_data')


class FormEntriesListSerializer(serializers.ModelSerializer):
    user_created = serializers.SerializerMethodField()

    @classmethod
    def get_user_created(cls, obj):
        return {'full_name': obj.user_created.get_full_name()} if obj.user_created else {}

    class Meta:
        model = FormPublishedEntries
        fields = ('id', 'body_data', 'date_created', 'ref_name', 'user_created')
