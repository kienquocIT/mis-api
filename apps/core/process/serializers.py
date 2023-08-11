from collections import defaultdict

from rest_framework import serializers

from apps.core.process.models import Function, Process, ProcessStep


class FunctionProcessListSerializer(serializers.ModelSerializer):
    function = serializers.SerializerMethodField()

    class Meta:
        model = Function
        fields = (
            'id',
            'function',
            'is_free',
            'is_in_process',
            'is_default'
        )

    @classmethod
    def get_function(cls, obj):
        if obj.function:
            return {
                'id': obj.function_id,
                'title': obj.function.title,
            }
        return {}


class ProcessDetailSerializer(serializers.ModelSerializer):
    process_step_datas = serializers.SerializerMethodField()

    class Meta:
        model = Process
        fields = (
            'process_step_datas',
        )

    @classmethod
    def get_process_step_datas(cls, obj):
        steps = ProcessStep.objects.filter(process=obj)

        grouped_steps = defaultdict(list)
        for step in steps:
            grouped_steps[step.order].append(step)
        list_step = []
        for order, step_list in grouped_steps.items():
            step_dict = {str(step.id): {
                'function_id': step.function_id,
                'function_title': step.function_title,
                'is_current': step.is_current,
                'is_completed': step.is_completed,
                'order': step.order,
                'subject': step.subject,
            } for step in step_list}
            list_step.append(step_dict)
        return list_step


class ProcessStepFunctionSerializer(serializers.ModelSerializer):
    function_id = serializers.UUIDField(required=True)
    subject = serializers.CharField(allow_blank=True)
    is_current = serializers.BooleanField()
    is_completed = serializers.BooleanField()

    class Meta:
        model = ProcessStep
        fields = (
            'function_id',
            'function_title',
            'subject',
            'is_current',
            'is_completed',
        )

    @classmethod
    def validate_function_id(cls, value):
        if value:
            try:
                Function.objects.get_current(
                    fill__company=True,
                    id=value
                )
                return str(value)
            except Function.DoesNotExist:
                raise serializers.ValidationError({'function': 'Does not exist'})
        return None


class ProcessStepSerializer(serializers.Serializer):
    step = ProcessStepFunctionSerializer(many=True)


class ProcessUpdateSerializer(serializers.ModelSerializer):
    process_step_datas = ProcessStepSerializer(many=True)

    class Meta:
        model = Process
        fields = (
            'process_step_datas',
        )

    @classmethod
    def update_step_process(cls, instance, data):
        ProcessStep.objects.filter(process=instance).delete()
        bulk_data = []
        process_step_datas = []
        cnt = 1
        for step in data:
            temp_list = {}
            for function in step['step']:
                process_step = ProcessStep(
                    process=instance,
                    function_id=function['function_id'],
                    function_title=function['function_title'],
                    subject=function['subject'],
                    order=cnt,
                    is_current=function['is_current'],
                    is_completed=function['is_completed']
                )
                function['order'] = cnt
                temp_list[str(process_step.id)] = function
                bulk_data.append(
                    process_step
                )
            process_step_datas.append(temp_list)
            cnt += 1
        ProcessStep.objects.bulk_create(bulk_data)
        return process_step_datas

    def update(self, instance, validated_data):
        process_step_datas = validated_data.get('process_step_datas', [])
        validated_data['process_step_datas'] = self.update_step_process(instance, process_step_datas)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ProcessStepDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStep
        fields = '__all__'


class SkipProcessStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStep
        fields = ()

    def update(self, instance, validated_data):
        if not instance.is_current:
            raise serializers.ValidationError({'detail': 'Ban chi co the skip step current'})

        if instance.is_completed:
            raise serializers.ValidationError({'detail': 'Step nay da completed roi'})

        instance.skip_step()
        return instance


class SetProcessStepCurrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ()

    def update(self, instance, validated_data):
        if instance.is_completed:
            raise serializers.ValidationError({'detail': 'Step này đã completed không thể set current'})
        if instance.is_current:
            raise serializers.ValidationError({'detail': 'Bạn đang ở step này'})
        instance.set_current()
        return instance
