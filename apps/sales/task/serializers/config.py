from rest_framework import serializers

from apps.sales.task.models import OpportunityTaskStatus, OpportunityTaskConfig, OpportunityTask

__all__ = [
    'TaskConfigDetailSerializer', 'TaskConfigUpdateSerializer'
]


class TaskConfigDetailSerializer(serializers.ModelSerializer):
    list_status = serializers.SerializerMethodField()

    @classmethod
    def get_list_status(cls, obj):
        task_list = []
        tasks_stt = OpportunityTaskStatus.objects.filter(
            task_config=obj
        )
        if tasks_stt.exists():
            for status in tasks_stt:
                count = OpportunityTask.objects.filter(task_status=status, is_delete=False).count()
                task_list.append(
                    {
                        'id': str(status.id),
                        'name': status.title,
                        'translate_name': status.translate_name,
                        'order': status.order,
                        'is_edit': status.is_edit,
                        'count': count,
                        'task_color': status.task_color
                    }
                )
        return task_list

    class Meta:
        model = OpportunityTaskConfig
        fields = ('id', 'list_status', 'is_edit_date', 'is_edit_est', 'is_in_assign', 'in_assign_opt', 'is_out_assign',
                  'out_assign_opt')


class TaskConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTaskConfig
        fields = ('list_status', 'is_edit_date', 'is_edit_est', 'is_in_assign', 'in_assign_opt', 'is_out_assign',
                  'out_assign_opt')

    @classmethod
    def handle_task_before(cls, obj_status, instance):
        # lấy id to do status
        todo_status = OpportunityTaskStatus.objects.filter(
            task_config=instance,
            task_kind=1
        ).first()

        # lấy task theo obj_status
        task_lst = OpportunityTask.objects.filter(
            task_status=obj_status
        )
        task_edited = []
        if task_lst.count():
            for task in task_lst:
                task.task_status = todo_status
                task_edited.append(task)
            OpportunityTask.objects.bulk_update(task_edited, fields=['task_status'])

    @classmethod
    def update_task_status(cls, lst_status, instance):
        if lst_status and isinstance(lst_status, list):
            has_status = []
            new_status = []
            dict_status = {}
            for item in lst_status:
                if item['id']:
                    has_status.append(
                        OpportunityTaskStatus(
                            id=str(item['id']),
                            title=item['name'],
                            translate_name=item['translate_name'],
                            order=item['order'],
                            task_color=item['task_color'],
                        )
                    )
                    dict_status[item['id']] = item
                else:
                    new_status.append(
                        OpportunityTaskStatus(
                            title=item['name'],
                            translate_name=item['translate_name'],
                            order=item['order'],
                            is_edit=True,
                            task_config=instance,
                            task_color=item['task_color'],
                        )
                    )

            # update status step by step
            #
            # 1 xử lý các stt bị xoá
            # 2 update các stt đang có
            # 3 tạo mới các status chưa có

            check_stt_list = OpportunityTaskStatus.objects.filter(task_config=instance, is_edit=1)
            if check_stt_list.count():
                for stt in check_stt_list:
                    stt_id = str(stt.id)
                    if stt_id not in dict_status:
                        cls.handle_task_before(stt, instance)
                        stt.delete()
            OpportunityTaskStatus.objects.bulk_update(has_status, fields=['title', 'translate_name', 'order',
                                                                          'task_color'])
            OpportunityTaskStatus.objects.bulk_create(new_status)

    def update(self, instance, validated_data):
        status_lst = validated_data['list_status']
        self.update_task_status(status_lst, instance)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance
