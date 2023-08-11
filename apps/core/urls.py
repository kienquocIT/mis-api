from celery.result import AsyncResult
from django.urls import path, include
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.shared import TypeCheck, mask_view, ResponseController


class TaskBackgroundState(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        _id = kwargs.get('pk', None)
        if _id and TypeCheck.check_uuid(_id):
            state = str(AsyncResult(_id).state)
            return ResponseController.success_200(data={'state': state}, key_data='result')
        return ResponseController.notfound_404()


urlpatterns = [
    path('auth/', include('apps.core.auths.urls')),
    path('account/', include('apps.core.account.urls')),
    path('provisioning/', include('apps.core.provisioning.urls')),
    path('hr/', include('apps.core.hr.urls')),
    path('tenant/', include('apps.core.tenant.urls')),
    path('company/', include('apps.core.company.urls')),
    path('base/', include('apps.core.base.urls')),
    path('workflow/', include('apps.core.workflow.urls')),
    path('task-bg/<str:pk>', TaskBackgroundState.as_view(), name='TaskBackgroundState'),
    path('log/', include('apps.core.log.urls')),
    path('process/', include('apps.core.process.urls'))
]
