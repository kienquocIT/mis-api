import magic
from django.conf import settings
from rest_framework import serializers

from apps.core.mailer.handle_html import HTMLController
from apps.core.mailer.models import MailTemplate, MailTemplateSystem, MailConfig
from apps.shared import BaseMsg, AttMsg, FORMATTING


class MailTemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailTemplate
        fields = ('id', 'title', 'remarks', 'application', 'is_active', 'is_default')


class MailTemplateDetailSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    @classmethod
    def get_contents(cls, obj):
        return HTMLController.unescape(obj.contents)

    application = serializers.SerializerMethodField()

    @classmethod
    def get_application(cls, obj):
        if obj:
            return {
                'id': obj.application_id,
                'title': obj.application.title,
            }
        return {}

    class Meta:
        model = MailTemplate
        fields = ('id', 'title', 'remarks', 'application', 'is_active', 'is_default', 'contents')


class MailTemplateCreateSerializer(serializers.ModelSerializer):
    @classmethod
    def validate_contents(cls, attrs):
        if not attrs or HTMLController(html_str=attrs).is_html():
            return attrs
        raise serializers.ValidationError(
            {
                'contents': BaseMsg.NOT_IS_HTML,
            }
        )

    class Meta:
        model = MailTemplate
        fields = ('title', 'remarks', 'application', 'is_active', 'contents')


class MailTemplateUpdateSerializer(serializers.ModelSerializer):
    @classmethod
    def validate_contents(cls, attrs):
        if not attrs or HTMLController(html_str=attrs).is_html():
            return attrs
        raise serializers.ValidationError(
            {
                'contents': BaseMsg.NOT_IS_HTML,
            }
        )

    class Meta:
        model = MailTemplate
        fields = ('title', 'remarks', 'is_active', 'is_default', 'contents')


class MailTemplateSystemDetailSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    @classmethod
    def get_contents(cls, obj):
        return HTMLController.unescape(obj.contents)

    class Meta:
        model = MailTemplateSystem
        fields = ('id', 'system_code', 'subject', 'contents', 'is_active')


class MailTemplateSystemUpdateSerializer(serializers.ModelSerializer):
    @classmethod
    def validate_contents(cls, attrs):
        if not attrs or HTMLController(html_str=attrs).is_html():
            return attrs
        raise serializers.ValidationError(
            {
                'contents': BaseMsg.NOT_IS_HTML,
            }
        )

    class Meta:
        model = MailTemplateSystem
        fields = ('subject', 'contents', 'is_active')


class MailConfigDetailSerializer(serializers.ModelSerializer):
    host = serializers.SerializerMethodField()

    @classmethod
    def get_host(cls, obj):
        return obj.data.get('host', '')

    port = serializers.SerializerMethodField()

    @classmethod
    def get_port(cls, obj):
        return obj.data.get('port', '')

    username = serializers.SerializerMethodField()

    @classmethod
    def get_username(cls, obj):
        return obj.data.get('username', '')

    password = serializers.SerializerMethodField()

    @classmethod
    def get_password(cls, obj):
        return obj.data.get('password', '')

    ssl_key = serializers.SerializerMethodField()

    @classmethod
    def get_ssl_key(cls, obj):
        return obj.data.get('ssl_key', None)

    ssl_cert = serializers.SerializerMethodField()

    @classmethod
    def get_ssl_cert(cls, obj):
        return obj.data.get('ssl_cert', None)

    class Meta:
        model = MailConfig
        fields = (
            'id', 'use_our_server',
            'host', 'port', 'username', 'password',
            'use_tls',
            'use_ssl', 'ssl_key', 'ssl_cert',
            'is_active'
        )


class MailConfigUpdateSerializer(serializers.ModelSerializer):
    # Ref: https://www.clamav.net/
    # import clamd
    # cd = clamd.ClamdUnixSocket()
    # scan_results = cd.instream(file_obj)
    # print('scan_results:', scan_results)

    @staticmethod
    def handle_valid_file(file_obj, max_size):
        if file_obj and hasattr(file_obj, 'size'):
            if isinstance(file_obj.size, int) and file_obj.size < max_size:
                file_obj.seek(0)
                magic_check_content_type = magic.from_buffer(file_obj.read(), mime=True)
                if magic_check_content_type in ['text/plain', file_obj.content_type]:
                    return file_obj
                raise serializers.ValidationError({'file': AttMsg.FILE_TYPE_DETECT_DANGER})
            file_size_limit = AttMsg.FILE_SIZE_SHOULD_BE_LESS_THAN_X.format(
                FORMATTING.size_to_text(max_size)
            )
            raise serializers.ValidationError({'file': file_size_limit})
        raise serializers.ValidationError({'file': AttMsg.FILE_NO_DETECT_SIZE})

    @classmethod
    def validate_ssl_key(cls, attrs):
        return cls.handle_valid_file(file_obj=attrs, max_size=settings.EMAIL_CONFIG_SSL_KEY_MAX_SIZE)

    @classmethod
    def validate_ssl_cert(cls, attrs):
        return cls.handle_valid_file(file_obj=attrs, max_size=settings.EMAIL_CONFIG_SSL_CERT_MAX_SIZE)

    @classmethod
    def force_ssl(cls, instance, ssl_key_file, ssl_cert_file):
        if ssl_key_file:
            if instance.ssl_key:
                instance.ssl_key.storage.delete(instance.ssl_key.name)
            instance.ssl_key = ssl_key_file
        if ssl_cert_file:
            if instance.ssl_cert:
                instance.ssl_cert.storage.delete(instance.ssl_cert.name)
            instance.ssl_cert = ssl_cert_file
        return instance

    from_email = serializers.EmailField(required=False)
    reply_email = serializers.EmailField(required=False)
    cc_email = serializers.ListSerializer(
        child=serializers.EmailField(required=False),
        required=False, allow_null=True
    )
    bcc_email = serializers.ListSerializer(
        child=serializers.EmailField(required=False),
        required=False, allow_null=True
    )

    def update(self, instance, validated_data):  # pylint: disable=R0914
        # get data simple and update data simple
        use_our_server = validated_data.get('use_our_server', instance.use_our_server)
        use_tls = validated_data.get('use_tls', instance.use_tls)
        use_ssl = validated_data.get('use_ssl', instance.use_ssl)
        is_active = validated_data.get('is_active', instance.is_active)
        instance.use_our_server = use_our_server
        instance.use_tls = use_tls
        instance.use_ssl = use_ssl
        instance.is_active = is_active

        # ssl file
        ssl_key_file = validated_data.get('ssl_key', None)
        ssl_cert_file = validated_data.get('ssl_cert', None)
        self.force_ssl(instance=instance, ssl_key_file=ssl_key_file, ssl_cert_file=ssl_cert_file)

        # get data must encrypt and call push data encrypt
        host = validated_data.get('host', None)
        port = validated_data.get('port', None)
        username = validated_data.get('username', None)
        password = validated_data.get('password', None)
        from_email = validated_data.get('from_email', None)
        reply_email = validated_data.get('from_email', None)
        cc_email = validated_data.get('from_email', None)
        bcc_email = validated_data.get('from_email', None)
        instance.encrypt_and_collect(
            host=host, port=port, username=username, password=password,
            from_email=from_email, reply_email=reply_email, cc_email=cc_email, bcc_email=bcc_email,
            ssl_key_file=bool(ssl_key_file),
            ssl_cert_file=bool(ssl_cert_file),
        )

        # force save
        instance.save()
        return instance

    class Meta:
        model = MailConfig
        fields = (
            'use_our_server', 'host', 'port', 'username', 'password', 'use_tls', 'use_ssl', 'is_active',
            'from_email', 'reply_email', 'cc_email', 'bcc_email',
            'ssl_key', 'ssl_cert'
        )


class MailTestConnectDataSerializer(serializers.ModelSerializer):
    host = serializers.CharField(required=True)
    port = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    use_tls = serializers.BooleanField(required=True)

    class Meta:
        model = MailConfig
        fields = ('host', 'port', 'username', 'password', 'use_tls')
