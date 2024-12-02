from django.utils.translation import gettext_lazy as trans
from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.process.models import ProcessConfiguration, Process, ProcessStage
from apps.core.process.models.runtime import ProcessStageApplication, ProcessDoc, ProcessMembers, ProcessActivity
from apps.core.process.msg import ProcessMsg
from apps.core.process.utils import ProcessRuntimeControl
from apps.shared import TypeCheck, HrMsg


class ProcessConfigReadySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessConfiguration
        fields = ('id', 'title', 'remark', 'date_created', 'for_opp', 'is_active')


class ProcessConfigListSerializer(serializers.ModelSerializer):
    employee_created = serializers.SerializerMethodField()

    @classmethod
    def get_employee_created(cls, obj):
        if obj.employee_created:
            return obj.employee_created.get_detail()
        return {}

    class Meta:
        model = ProcessConfiguration
        fields = ('id', 'title', 'remark', 'date_created', 'for_opp', 'is_active', 'employee_created')


class ProcessConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessConfiguration
        fields = (
            'id', 'title', 'remark',
            'apply_start', 'apply_finish', 'is_active', 'for_opp',
            'stages', 'global_app',
        )


class StagesApplicationSerializer(serializers.Serializer):  # noqa
    title = serializers.CharField(max_length=200)
    remark = serializers.CharField(max_length=500, allow_blank=True, default=str)
    min = serializers.ChoiceField(choices=['0', '1', '2', '3', '4', '5'])
    max = serializers.ChoiceField(choices=['1', '2', '3', '4', '5', 'n'])
    application = serializers.UUIDField()

    @classmethod
    def validate_application(cls, attrs):
        if attrs and TypeCheck.check_uuid(attrs):
            try:
                app_obj = Application.objects.get(pk=attrs)
            except Application.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        'stages': ProcessMsg.APPLICATION_NOT_FOUND
                    }
                )
            if app_obj.allow_process is True:
                return str(app_obj.id)
        raise serializers.ValidationError({'stages': ProcessMsg.APPLICATION_NOT_SUPPORT})

    def validate(self, validated_data):
        min_num = validated_data['min']
        max_num = validated_data['max']
        if max_num == "n":
            return validated_data
        try:
            min_num = int(min_num)
            max_num = int(max_num)
        except ValueError:
            raise serializers.ValidationError({'stages': ProcessMsg.MIN_MAX_INCORRECT})
        if max_num >= min_num:
            return validated_data
        raise serializers.ValidationError({'stages': ProcessMsg.MAX_MUST_LARGE_MIN})


class ProcessStagesSerializer(serializers.Serializer):  # noqa
    title = serializers.CharField(max_length=200)
    remark = serializers.CharField(max_length=500, allow_blank=True, default=str)
    is_system = serializers.BooleanField(default=False)
    system_code = serializers.CharField(allow_null=True, max_length=10)
    application = serializers.ListSerializer(
        child=StagesApplicationSerializer(), min_length=0, max_length=20
    )

    def validate(self, validated_data):
        is_system = validated_data.get('is_system', False)
        application = validated_data.get('application', [])
        if is_system is True:
            validated_data['application'] = []
            return validated_data
        if application and isinstance(application, list) and len(application) > 0:
            app_ids = [item['application'] for item in application]
            if len(app_ids) == len(set(app_ids)):
                return validated_data
            raise serializers.ValidationError(
                {
                    'stages': ProcessMsg.APPLICATION_DUPLICATE_IN_STAGES
                }
            )
        raise serializers.ValidationError({'stages': ProcessMsg.APPLICATION_LEASE_ONE})


class ProcessConfigCreateSerializer(serializers.ModelSerializer):
    stages = serializers.ListSerializer(
        child=ProcessStagesSerializer()
    )

    global_app = serializers.ListSerializer(
        child=StagesApplicationSerializer(), min_length=0, max_length=20
    )

    @classmethod
    def validate_stages(cls, attrs):
        if attrs and isinstance(attrs, list):
            if len(attrs) >= 3:
                return attrs
        raise serializers.ValidationError(
            {
                'stages': ProcessMsg.PROCESS_STAGES_REQUIRED
            }
        )

    @classmethod
    def validate_global_app(cls, attrs):
        if attrs and isinstance(attrs, list):
            app_ids = [item['application'] for item in attrs]
            if len(app_ids) == len(set(app_ids)):
                return attrs
            raise serializers.ValidationError(
                {
                    'global_app': ProcessMsg.GLOBAL_APPLICATION_DUPLICATE
                }
            )
        return []

    @staticmethod
    def get_application_for_process(for_opp=False) -> list[str]:
        app_objs = Application.objects.filter(
            allow_process=True, **(
                {'allow_opportunity': True} if for_opp else {}
            )
        )
        return [str(item) for item in app_objs.values_list('id', flat=True)]

    def validate(self, validated_data):
        apply_start = validated_data.get('apply_start', None)
        apply_finish = validated_data.get('apply_finish', None)
        if apply_start and apply_finish:
            if apply_finish > apply_start:
                return validated_data
            raise serializers.ValidationError(
                {
                    'apply_finish': ProcessMsg.FINISH_MUST_LARGE_START
                }
            )

        for_opp = validated_data.get('for_opp', False)
        app_ids = self.get_application_for_process(for_opp=for_opp)
        for stage_data in validated_data.get('stages', []):
            for app_data in stage_data.get('application', []):
                if app_data.get('application', None) not in app_ids:
                    raise serializers.ValidationError(
                        {
                            'stages': ProcessMsg.SOME_APPLICATION_NOT_SUPPORT
                        }
                    )
        for app_data in validated_data.get('global_app', []):
            if app_data.get('application', None) not in app_ids:
                raise serializers.ValidationError(
                    {
                        'stages': ProcessMsg.SOME_APPLICATION_NOT_SUPPORT
                    }
                )
        return validated_data

    class Meta:
        model = ProcessConfiguration
        fields = ('title', 'remark', 'apply_start', 'apply_finish', 'is_active', 'for_opp', 'stages', 'global_app',)


class ProcessConfigUpdateSerializer(serializers.ModelSerializer):
    stages = serializers.ListSerializer(
        child=ProcessStagesSerializer()
    )

    global_app = serializers.ListSerializer(
        child=StagesApplicationSerializer(), min_length=0, max_length=20
    )

    @classmethod
    def validate_stages(cls, attrs):
        if attrs and isinstance(attrs, list):
            if len(attrs) >= 3:
                return attrs
        raise serializers.ValidationError(
            {
                'stages': ProcessMsg.PROCESS_STAGES_REQUIRED
            }
        )

    @classmethod
    def validate_global_app(cls, attrs):
        if attrs and isinstance(attrs, list):
            app_ids = [item['application'] for item in attrs]
            if len(app_ids) == len(set(app_ids)):
                return attrs
            raise serializers.ValidationError(
                {
                    'global_app': ProcessMsg.GLOBAL_APPLICATION_DUPLICATE
                }
            )
        return []

    def validate(self, validated_data):
        apply_start = validated_data.get('apply_start', self.instance.apply_start)
        apply_finish = validated_data.get('apply_finish', self.instance.apply_finish)
        if apply_start and apply_finish:
            if apply_finish > apply_start:
                return validated_data
            raise serializers.ValidationError(
                {
                    'apply_finish': ProcessMsg.FINISH_MUST_LARGE_START
                }
            )

        for_opp = validated_data.get('for_opp', self.instance.for_opp)
        app_ids = ProcessConfigCreateSerializer.get_application_for_process(for_opp=for_opp)
        for stage_data in validated_data.get('stages', self.instance.stages):
            for app_data in stage_data.get('application', []):
                if app_data.get('application', None) not in app_ids:
                    raise serializers.ValidationError(
                        {
                            'stages': ProcessMsg.SOME_APPLICATION_NOT_SUPPORT
                        }
                    )
        for app_data in validated_data.get('global_app', self.instance.global_app):
            if app_data.get('application', None) not in app_ids:
                raise serializers.ValidationError(
                    {
                        'stages': ProcessMsg.SOME_APPLICATION_NOT_SUPPORT
                    }
                )
        return validated_data

    class Meta:
        model = ProcessConfiguration
        fields = ('title', 'remark', 'apply_start', 'apply_finish', 'is_active', 'for_opp', 'stages', 'global_app',)


class ProcessRuntimeListSerializer(serializers.ModelSerializer):
    config = serializers.SerializerMethodField()

    @classmethod
    def get_config(cls, obj):
        if obj.config:
            return {
                'id': obj.config_id,
                'title': obj.config.title,
                'remark': obj.config.remark,
                'for_opp': obj.config.for_opp,
            }
        return {}

    employee_created = serializers.SerializerMethodField()

    @classmethod
    def get_employee_created(cls, obj):
        if obj.employee_created:
            return {
                'id': obj.employee_created_id,
                'full_name': obj.employee_created.get_full_name(),
                'avatar_img': obj.employee_created.avatar_img.url if obj.employee_created.avatar_img else None,
            }
        return {}

    amount_stages = serializers.SerializerMethodField()

    @classmethod
    def get_amount_stages(cls, obj):
        return len(obj.stages)

    stage_current = serializers.SerializerMethodField()

    @classmethod
    def get_stage_current(cls, obj):
        if obj.stage_current:
            return {
                'id': obj.stage_current.id,
                'title': obj.stage_current.title,
                'remark': obj.stage_current.remark,
                'order_number': obj.stage_current.order_number
            }
        return {}

    opp = serializers.SerializerMethodField()

    @classmethod
    def get_opp(cls, obj):
        if obj.opp:
            return {
                'id': obj.opp.id,
                'title': obj.opp.title
            }
        return {}

    class Meta:
        model = Process
        fields = (
            'id', 'title', 'remark', 'config',
            'was_done', 'date_done', 'employee_created',
            'stage_current', 'amount_stages', 'opp',
            'date_created',
        )


class ProcessRuntimeDetailSerializer(serializers.ModelSerializer):
    config = serializers.SerializerMethodField()

    @classmethod
    def get_config(cls, obj):
        if obj.config:
            return {
                'id': obj.config_id,
                'title': obj.config.title,
                'remark': obj.config.remark,
                'for_opp': obj.config.for_opp,
            }
        return {}

    stages = serializers.SerializerMethodField()

    @staticmethod
    def state_of_stages(current_order_number, stage_order_number):
        if stage_order_number < current_order_number:
            return 'DONE'
        if stage_order_number == current_order_number:
            return 'CURRENT'
        return 'COMING'

    @classmethod
    def get_stages(cls, obj):
        current_order_number = -1
        if obj.stage_current:
            current_order_number = obj.stage_current.order_number

        return [
            {
                'id': obj_stage.id,
                'title': obj_stage.title,
                'remark': obj_stage.remark,
                'is_system': obj_stage.is_system,
                'system_code': obj_stage.system_code,
                'application': [
                    {
                        'id': obj_app.id,
                        'title': obj_app.title,
                        'remark': obj_app.remark,
                        'application': obj_app.application_id,
                        'app_label': obj_app.application.app_label,
                        'mode_code': obj_app.application.model_code,
                        'amount': obj_app.amount,
                        'min': obj_app.min,
                        'max': obj_app.max,
                        'was_done': obj_app.was_done,
                        'amount_approved': obj_app.amount_approved,
                    } for obj_app in
                    ProcessStageApplication.objects.select_related('application').filter(
                        process=obj, stage=obj_stage
                    ).order_by('order_number')
                ],
                'state': cls.state_of_stages(current_order_number, obj_stage.order_number),
                'order_number': obj_stage.order_number,
            } for obj_stage in ProcessStage.objects.filter(process=obj).order_by('order_number')
        ]

    global_app = serializers.SerializerMethodField()

    @classmethod
    def get_global_app(cls, obj):
        return [
            {
                'id': obj_app.id,
                'title': obj_app.title,
                'remark': obj_app.remark,
                'application': obj_app.application_id,
                'app_label': obj_app.application.app_label,
                'mode_code': obj_app.application.model_code,
                'amount': obj_app.amount,
                'min': obj_app.min,
                'max': obj_app.max,
                'was_done': obj_app.was_done,
                'amount_approved': obj_app.amount_approved,
            } for obj_app in
            ProcessStageApplication.objects.filter(process=obj, stage__isnull=True).order_by('order_number')
        ]

    stage_current = serializers.SerializerMethodField()

    @classmethod
    def get_stage_current(cls, obj):
        if obj.stage_current:
            return obj.stage_current_id
        return None

    opp = serializers.SerializerMethodField()

    @classmethod
    def get_opp(cls, obj):
        if obj.opp:
            return {
                'id': obj.opp_id,
                'title': obj.opp.title,
                'code': obj.opp.code,
            }
        return None

    class Meta:
        model = Process
        fields = (
            'id', 'title', 'remark', 'config', 'stage_current', 'stages', 'global_app', 'opp', 'employee_created_id',
        )


class ProcessRuntimeCreateSerializer(serializers.ModelSerializer):
    config = serializers.UUIDField()

    @classmethod
    def validate_config(cls, attrs):
        if attrs and TypeCheck.check_uuid(attrs):
            process_config_obj = ProcessRuntimeControl.get_process_config(process_config_id=attrs, for_opp=False)
            if process_config_obj.for_opp is True:
                raise ValueError(
                    {
                        'config': ProcessMsg.NOT_SUPPORT_WITHOUT_OPP
                    }
                )
            return process_config_obj
        raise serializers.ValidationError(
            {
                'config': ProcessMsg.PROCESS_NOT_FOUND
            }
        )

    def create(self, validated_data):
        title = validated_data.pop('title', '')
        remark = validated_data.pop('remark', '')
        config = validated_data.pop('config', None)
        instance = ProcessRuntimeControl.create_process_from_config(
            title=title, remark=remark, config=config, **validated_data
        )
        ProcessRuntimeControl(process_obj=instance).play_process()
        return instance

    class Meta:
        model = Process
        fields = ('title', 'remark', 'config')


class ProcessDocListSerializer(serializers.ModelSerializer):
    employee_created = serializers.SerializerMethodField()

    @classmethod
    def get_employee_created(cls, obj):
        if obj.employee_created:
            return {
                'id': obj.employee_created.id,
                'first_name': obj.employee_created.first_name,
                'last_name': obj.employee_created.last_name,
                'full_name': obj.employee_created.get_full_name(),
                'avatar_img': obj.employee_created.avatar_img.url if obj.employee_created.avatar_img else None,
            }
        return {}

    class Meta:
        model = ProcessDoc
        fields = ('id', 'title', 'date_created', 'employee_created', 'system_status', 'date_status')


class ProcessStageApplicationListSerializer(serializers.ModelSerializer):
    application = serializers.SerializerMethodField()

    @classmethod
    def get_application(cls, obj):
        if obj.application:
            return {
                'id': obj.application.id,
                'title': obj.application.title,
                'title_i18n': trans(obj.application.title),
            }
        return {}

    process = serializers.SerializerMethodField()

    @classmethod
    def get_process(cls, obj):
        if obj.process:
            return {
                'id': obj.process.id,
                'title': obj.process.title,
                'opp_id': obj.process.opp_id,
            }
        return {}

    opp = serializers.SerializerMethodField()

    @classmethod
    def get_opp(cls, obj):
        if obj.process and obj.process.opp:
            return {
                'id': obj.process.opp_id,
                'title': obj.process.opp.title,
                'code': obj.process.opp.code,
            }
        return None

    class Meta:
        model = ProcessStageApplication
        fields = ('id', 'title', 'application', 'process', 'opp')


class ProcessStageApplicationDetailSerializer(serializers.ModelSerializer):
    doc_list = serializers.SerializerMethodField()

    @classmethod
    def get_doc_list(cls, obj):
        doc_objs = ProcessDoc.objects.select_related('employee_created').filter_current(
            fill__tenant=True,
            fill__company=True,
            process=obj.process,
            stage_app=obj
        )
        return ProcessDocListSerializer(doc_objs, many=True).data

    class Meta:
        model = ProcessStageApplication
        fields = ('id', 'title', 'doc_list')


class ProcessStageApplicationUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        runtime_cls = ProcessRuntimeControl(process_obj=instance.process)
        runtime_cls.log(
            title='Confirmation of completion of application',
            code='STAGE_APP_COMPLETE',
            stage=instance.stage,
            app=instance,
            employee_created_id=instance.employee_modified_id,
        )
        runtime_cls.check_stages_current(from_stages_app=instance)
        return instance

    class Meta:
        model = ProcessStageApplication
        fields = ('was_done',)


class ProcessRuntimeDataMatchFromStageSerializer(serializers.ModelSerializer):
    # 'opp': {
    #                         'id': obj_app.process.opp_id,
    #                         'title': obj_app.process.opp.title,
    #                         'code': obj_app.process.opp.code,
    #                     } if obj_app.process and obj_app.process.opp else {},
    #                     'process': {
    #                         'id': obj_app.process.id,
    #                         'title': obj_app.process.title,
    #                         'remark': obj_app.process.remark,
    #                     },
    #                     'process_stage_app': {
    #                         'id': obj_app.id,
    #                         'title': obj_app.title,
    #                         'remark': obj_app.remark,
    #                         'application': {
    #                             'id': obj_app.application.id,
    #                             'title': obj_app.application.title,
    #                             'title_i18n': trans(obj_app.application.title),
    #                         },
    #                     } if obj_app else {},
    opp = serializers.SerializerMethodField()

    @classmethod
    def get_opp(cls, obj):
        if obj.process:
            if obj.process.opp:
                return {
                    'id': obj.process.opp_id,
                    'title': obj.process.opp.title,
                    'code': obj.process.opp.code
                }
        return {}

    process = serializers.SerializerMethodField()

    @classmethod
    def get_process(cls, obj):
        if obj.process:
            return {
                'id': obj.process_id,
                'title': obj.process.title,
                'remark': obj.process.remark,
            }
        return {}

    process_stage_app = serializers.SerializerMethodField()

    @classmethod
    def get_process_stage_app(cls, obj):
        if obj:
            return {
                'id': obj.id,
                'title': obj.title,
                'remark': obj.remark,
            }
        return {}

    class Meta:
        model = ProcessStageApplication
        fields = ('opp', 'process', 'process_stage_app')


class ProcessRuntimeDataMatchFromProcessSerializer(serializers.ModelSerializer):
    opp = serializers.SerializerMethodField()

    @classmethod
    def get_opp(cls, obj):
        if obj.opp_id:
            return {
                'id': obj.opp_id,
                'title': obj.opp.title,
                'code': obj.opp.code
            }
        return {}

    process = serializers.SerializerMethodField()

    @classmethod
    def get_process(cls, obj):
        if obj:
            return {
                'id': obj.id,
                'title': obj.title,
                'remark': obj.remark,
            }
        return {}

    process_stage_app = serializers.SerializerMethodField()

    def get_process_stage_app(self, obj):
        app_id = self.context.get('app_id', None)
        if app_id:
            obj_app = ProcessStageApplication.objects.filter(process=obj, application_id=app_id).first()
        else:
            obj_app = ProcessStageApplication.objects.filter(process=obj).first()
        if obj_app:
            return {
                'id': obj_app.id,
                'title': obj_app.title,
                'remark': obj_app.remark,
            }
        return {}

    class Meta:
        model = Process
        fields = ('opp', 'process', 'process_stage_app')


class ProcessRuntimeMembersSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    @classmethod
    def get_employee(cls, obj):
        if obj.employee:
            return obj.employee.get_detail_minimal()
        return {}

    employee_created = serializers.SerializerMethodField()

    @classmethod
    def get_employee_created(cls, obj):
        if obj.employee_created:
            return obj.employee_created.get_detail_minimal()
        return {}

    class Meta:
        model = ProcessMembers
        fields = ('id', 'employee', 'employee_created', 'date_created')


class ProcessRuntimeMembersCreateSerializer(serializers.ModelSerializer):
    employees = serializers.ListSerializer(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=10
    )

    @classmethod
    def validate_employees(cls, attrs):
        try:
            objs = Employee.objects.filter_current(fill__tenant=True, fill__company=True, id__in=attrs)
            if objs.count() == len(attrs):
                return objs
        except Employee.DoesNotExist:
            pass
        raise serializers.ValidationError({'employee': HrMsg.EMPLOYEE_NOT_FOUND})

    process = serializers.UUIDField()

    @classmethod
    def validate_process(cls, attrs):
        try:
            return Process.objects.get_current(fill__tenant=True, fill__company=True, pk=attrs)
        except Process.DoesNotExist:
            pass
        raise serializers.ValidationError({'process': ProcessMsg.PROCESS_NOT_FOUND})

    def create(self, validated_data):
        employees = validated_data.pop('employees', [])
        objs = []
        for obj in employees:
            obj, _created = ProcessMembers.objects.get_or_create(employee=obj, **validated_data)
            objs.append(
                obj
            )
        return objs

    class Meta:
        model = ProcessMembers
        fields = ('employees', 'process')


class ProcessRuntimeLogList(serializers.ModelSerializer):
    title_i18n = serializers.SerializerMethodField()

    @classmethod
    def get_title_i18n(cls, obj):
        return trans(obj.title)

    employee_created = serializers.SerializerMethodField()

    @classmethod
    def get_employee_created(cls, obj):
        if obj.employee_created:
            return obj.employee_created.get_detail_minimal()
        return {}

    stage = serializers.SerializerMethodField()

    @classmethod
    def get_stage(cls, obj):
        if obj.stage:
            return {
                'id': obj.stage.id,
                'title': obj.stage.title,
                'remark': obj.stage.remark,
            }
        return {}

    app = serializers.SerializerMethodField()

    @classmethod
    def get_app(cls, obj):
        if obj.app:
            return {
                'id': obj.app.id,
                'title': obj.app.title,
            }
        return {}

    doc = serializers.SerializerMethodField()

    @classmethod
    def get_doc(cls, obj):
        if obj.doc:
            return {
                'id': obj.doc.doc_id,
                'title': obj.doc.title,
            }
        return {}

    class Meta:
        model = ProcessActivity
        fields = ('title', 'title_i18n', 'code', 'employee_created', 'stage', 'app', 'doc', 'date_created')
