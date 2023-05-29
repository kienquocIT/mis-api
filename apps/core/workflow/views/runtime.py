from celery import uuid
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.core.workflow.models import Runtime, RuntimeStage, RuntimeLog, RuntimeAssignee
from apps.core.workflow.serializers.runtime import RuntimeTaskSerializer
from apps.shared import ResponseController, mask_view, call_task_background
from apps.core.workflow.utils.runtime import call_new_runtime, call_approval_task
from apps.core.workflow.utils.docs import DocHandler

__all__ = [
    'RuntimeDataView',
    'RuntimeDiagramView',
    'WorkflowRuntimeTest',
    'HistoryStage',
    'RuntimeTask',
]


class RuntimeDataView(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        # doc_id = kwargs.get('doc_id', None)
        # app = kwargs.get('app', None)
        doc_id = '00f2782d483c43be9022d5d2d4b3b692'
        app = 'saledata.contact'
        if doc_id and app:
            try:
                arr = app.split(".")
                runtime_obj = Runtime.objects.select_related('flow').get(
                    doc_id=doc_id,
                    app__app_label=arr[0], app__code=arr[1],
                )
            except Runtime.DoesNotExist:
                return ResponseController.notfound_404()
            task_id_list = RuntimeAssignee.objects.filter(
                stage=runtime_obj.stage_currents,
                employee_id=request.user.employee_current_id,
                is_done=False,
            ).values_list('id', flat=True)
            result = {
                'id': runtime_obj.id,
                'task_bg_id': runtime_obj.task_bg_id,
                'task_bg_state': runtime_obj.task_bg_state,
                'doc_id': runtime_obj.doc_id,
                'doc_title': runtime_obj.doc_title,
                'app_id': runtime_obj.app_id,
                'flow': {
                    "id": runtime_obj.flow.id,
                    "title": runtime_obj.flow.title,
                } if runtime_obj.flow else {},
                'state': runtime_obj.state,
                'runtime_status': runtime_obj.status,
                'stage_currents_id': runtime_obj.stage_currents_id if (
                        runtime_obj.stage_currents and runtime_obj.state != 2
                ) else {},
                'assignee_task_id': {} if len(task_id_list) <= 0 else {
                    'task_id': task_id_list[0],
                    'actions': runtime_obj.stage_currents.actions
                }
            }
            return ResponseController.success_200(data=result, key_data='result')
        return ResponseController.notfound_404()


class RuntimeDiagramView(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        doc_id = '00f2782d483c43be9022d5d2d4b3b692'
        app = 'saledata.contact'
        if doc_id and app:
            try:
                arr = app.split(".")
                runtime_obj = Runtime.objects.select_related('app', 'stage_currents').get(
                    doc_id=doc_id,
                    app__app_label=arr[0], app__code=arr[1],
                )
            except Runtime.DoesNotExist:
                return ResponseController.notfound_404()

            result = {
                'id': runtime_obj.id,
                'stages': [
                    {
                        "id": str(x.id),
                        "title": x.title,
                        "code": x.code,
                        "node_data": x.node_data,
                        "actions": x.actions,
                        "exit_node_conditions": x.exit_node_conditions,
                        "association_passed_data": x.association_passed_data,
                        "assignee_count": x.assignee_count,
                        "from_stage": {
                            "id": str(x.from_stage.id),
                            "title": x.from_stage.title,
                            "code": x.from_stage.code,
                        } if x.from_stage else {},
                        "to_stage": {
                            "id": str(x.to_stage.id),
                            "title": x.to_stage.title,
                            "code": x.to_stage.code,
                        } if x.to_stage else {},
                        "assignee_and_zone": [
                            {
                                "id": str(y.employee_id),
                                "full_name": str(y.employee.get_full_name()),
                                "zone_and_properties": y.zone_and_properties,
                            } for y in x.assignee_of_runtime_stage.all()
                        ],
                        "log_count": x.log_count,
                        "date_created": x.date_created
                    } for x in RuntimeStage.objects.select_related('from_stage', 'to_stage').prefetch_related(
                        'assignee_of_runtime_stage'
                    ).filter(runtime=runtime_obj)
                ],
            }
            return ResponseController.success_200(data=result, key_data='result')
        return ResponseController.notfound_404()


class WorkflowRuntimeTest(APIView):
    @swagger_auto_schema()
    def get(self, request, *args, **kwargs):
        print('Company ID: ', request.user.company_current_id)
        # print(
        #     RuntimeHandler().call_new(
        #         request.user.company_current_id,
        #         doc_id='00f2782d483c43be9022d5d2d4b3b692',
        #         app_code='saledata.contact',
        #     )
        # )
        doc_obj = DocHandler(doc_id='00f2782d483c43be9022d5d2d4b3b692', app_code='saledata.contact').get_obj(
            {
                'company_id': request.user.company_current_id
            }
        )
        print(doc_obj, request.user.company_current_id)
        if doc_obj:
            task_bg_id = uuid()
            call_task_background(
                call_new_runtime,
                *[
                    str(request.user.company_current_id),
                    '00f2782d483c43be9022d5d2d4b3b692',
                    'saledata.contact',
                    str(task_bg_id)
                ],
                task_id=task_bg_id,
            )
            return ResponseController.success_200(data={'hello': 'tao nè', 'task_bg_id': str(task_bg_id)})
        return ResponseController.notfound_404()


class HistoryStage(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True)
    def get(self, *args, pk, **kwargs):
        try:
            stage_obj = RuntimeStage.objects.prefetch_related('log_of_stage_runtime').get(pk=pk)
            log_objs = RuntimeLog.objects.select_related('actor').filter(stage=stage_obj)
            return ResponseController.success_200(
                data={
                    "id": stage_obj.id,
                    "title": stage_obj.title,
                    "code": stage_obj.code,
                    "histories": [
                        {
                            "assignee": {
                                "id": str(log.actor.id),
                                "full_name": log.actor.get_full_name()
                            } if log.actor else {},
                            "actor_data": log.actor_data,
                            "date_created": log.date_created,
                            "kind": log.kind,
                            "action": log.action,
                            "msg": log.msg,
                        }
                        for log in log_objs
                    ],
                }, key_data='result'
            )
        except RuntimeStage.DoesNotExist:
            pass
        return ResponseController.notfound_404()


class RuntimeTask(APIView):
    @swagger_auto_schema(request_body=RuntimeTaskSerializer)
    @mask_view(login_require=True)
    def put(self, request, *args, pk, **kwargs):
        ser = RuntimeTaskSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            obj = RuntimeAssignee.objects.get(pk=pk)
            call_approval_task(obj.id, request.user.employee_current_id)
            return ResponseController.success_200(data={'state': 'OK'}, key_data='result')
        except RuntimeAssignee.DoesNotExist:
            return ResponseController.notfound_404()
