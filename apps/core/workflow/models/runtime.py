import json
from typing import Union, Literal
from uuid import UUID

from django.db import models
from django.utils import timezone

from apps.shared import (
    SimpleAbstractModel, WORKFLOW_CONFIG_MODE, TypeCheck,
)

from .config import (
    Workflow, Node,
)

__all__ = [
    'Runtime',
    'RuntimeStage',
    'RuntimeLog',
    'RuntimeAssignee',
]

STATE_RUNTIME = (
    (0, 'Created'),  # default
    (1, 'In Progress'),
    (2, 'Finish'),
    (3, 'Finish with flow non-apply'),
)
STATUS_RUNTIME = (
    (0, 'Waiting'),  # default
    (1, 'Success'),
    (2, 'Fail'),
    (3, 'Pending'),
)
STATE_RUNTIME_COLLAB = (
    (0, 'Created'),
    (1, 'Wait'),
    (2, 'Done'),
)

KIND_LOG_ACTIVITY = (
    (0, 'Login'),
    (1, 'In Doc'),
    (2, 'In Flow'),
)
ACTION_LOG_ACTIVITY = (
    (0, ''),
    (1, ''),
)
TASK_BACKGROUND_STATE = (
    ('PENDING', 'The task is waiting to be executed | task đang chờ để được thực thi'),
    ('STARTED', 'The task has started execution | task đã được bắt đầu thực thi'),
    ('SUCCESS', 'The task has successfully executed | task đã thực thi thành công'),
    ('FAILURE', 'The task has failed during execution | task đã thất bại trong quá trình thực thi'),
    ('RETRY', 'The task is being retried after a failure | task đang được thực hiện lại sau khi đã thất bại'),
    (
        'REVOKED',
        'The task has been cancelled before completion or execution | '
        'task đã bị hủy bỏ trước khi hoàn thành hoặc bị thực thi'
    ),
    ('IGNORED', 'The task was ignored and not executed | task bị bỏ qua và không được thực thi'),
)


class Runtime(SimpleAbstractModel):
    """
    Runtime of all document.
    Filter by workflow/doc_id (don't filter by tenant, company)
    """

    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )

    doc_id = models.UUIDField(verbose_name='Document was runtime')
    doc_title = models.TextField(
        blank=True,
        verbose_name='Title of Doc',
        help_text='Title get from Doc Obj when create runtime obj'
    )
    app = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        verbose_name='App of DocID',
    )
    app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}'
    )
    doc_params = models.JSONField(
        default=dict,
        verbose_name='Params parsed of doc runtime'
    )
    doc_employee_inherit = models.ForeignKey(
        'hr.Employee',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Employee inherit of Document",
        help_text='Data from Runtime first time',
        related_name='employee_inherit_of_runtime',
    )
    doc_employee_created = models.ForeignKey(
        'hr.Employee',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Employee created of Document",
        help_text='Data from Runtime first time',
        related_name='employee_created_of_runtime',
    )
    flow = models.ForeignKey(
        Workflow,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Workflow applied'
    )
    state = models.IntegerField(
        choices=STATE_RUNTIME,
        default=0,
        verbose_name='State of stage runtime',
    )
    status = models.IntegerField(
        choices=STATUS_RUNTIME,
        default=0,
        verbose_name='Status of document runtime'
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at time',
    )
    date_finished = models.DateTimeField(null=True, help_text='The records finish at time')
    stage_currents = models.ForeignKey(
        'RuntimeStage',
        null=True,
        on_delete=models.SET_NULL,
        related_name='stage_currently_of_runtime',
        verbose_name='Stage Currently'
    )
    task_bg_state = models.CharField(
        max_length=10,
        choices=TASK_BACKGROUND_STATE,
        default='PENDING',
        verbose_name='State Task BG',
        help_text='Sate run of task background'
    )

    start_mode = models.PositiveSmallIntegerField(
        choices=WORKFLOW_CONFIG_MODE,
        default=None,
        null=True,
    )
    # document pined
    doc_pined = models.ForeignKey(
        'log.DocPined',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Doc Pined relate',
        related_name='runtime_of_doc_pined',
    )
    # employee ID list was appended view permit
    viewer_append = models.ManyToManyField(
        'hr.Employee',
        through='RuntimeViewer',
        symmetrical=False,
        related_name='employee_viewer_append',
        verbose_name='All employee ID Viewer',
        help_text='All employee ID was append view permit',
    )

    def save(self, *args, **kwargs):
        if kwargs.get('force_insert', False) and self.app:
            self.app_code = f'{self.app.app_label}.{self.app.code}'
        super().save(*args, **kwargs)

    def append_viewer(self, employee_obj):
        if employee_obj:
            RuntimeViewer.objects.get_or_create(runtime=self, employee=employee_obj, is_active=True)
        return self

    @classmethod
    def check_document_in_progress(
            cls,
            workflow_id: Union[UUID, str],
            state_or_count: Literal['state', 'count'] = 'state',
    ) -> Union[bool, int]:
        """
        Check document is not finish process.
        Returns:
            Boolean
                True: Exist document is not finish
                False: All document finished process
        """
        if state_or_count == 'state':
            # return cls.objects.filter(flow_id=workflow_id).exclude(status=2).exists()
            return cls.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                flow_id=workflow_id,
            ).exclude(state__in=[2, 3], status__in=[1, 2]).exists()
        if state_or_count == 'count':
            # return cls.objects.filter(flow_id=workflow_id).exclude(status=2).count()
            return cls.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                flow_id=workflow_id,
            ).exclude(state__in=[2, 3], status__in=[1, 2]).count()
        raise AttributeError('state_or_count value must be choice in [state, count].')

    @classmethod
    def get_document_in_progress(
            cls,
            workflow_id: Union[UUID, str],
            obj_or_data: Literal['obj', 'data'] = 'obj',
    ) -> list[Union[dict, models.Model]]:
        if obj_or_data == 'obj':
            return cls.objects.filter(flow_id=workflow_id).exclude(status=2)
        if obj_or_data == 'data':
            return list(
                cls.objects.filter(flow_id=workflow_id).exclude(status=2).values(
                    'id', 'doc_id', 'app', 'flow_id', 'state', 'status', 'date_created', 'date_finished'
                )
            )
        return []

    @staticmethod
    def parse_zone_and_properties(zone_and_properties: list[any]):
        code_arr = []
        if zone_and_properties and isinstance(zone_and_properties, list):
            for item in zone_and_properties:
                for detail in item['properties_detail']:
                    code_arr.append(detail['code'])
        return code_arr

    def find_task_id_get_zones(
            self,
            task_id: Union[UUID, str],
            employee_id: Union[UUID, str]
    ) -> (bool, Union[None, list[any]]):
        if TypeCheck.check_uuid(task_id):
            try:
                runtime_assignee_obj = RuntimeAssignee.objects.get(pk=task_id, employee_id=employee_id)
                if runtime_assignee_obj.stage and runtime_assignee_obj.stage.runtime_id == self.id:
                    return True, self.parse_zone_and_properties(runtime_assignee_obj.zone_and_properties)
            except RuntimeAssignee.DoesNotExist:
                return False, None
        return False, None

    class Meta:
        verbose_name = 'Runtime'
        verbose_name_plural = 'Runtime'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
        unique_together = ('doc_id', 'app')


class RuntimeStage(SimpleAbstractModel):
    """
    Stage in Doc's timeline... All station that Doc's timeline was passed.
    Node information was recorded to node_data (don't miss node data when related node was destroyed)
    Timeline arrange in order by ASC (ascending)
    """

    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )

    # overview of stage | management
    runtime = models.ForeignKey(
        Runtime,
        on_delete=models.CASCADE,
        verbose_name='All Node by Runtime',
    )

    # Important infor of Stage
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        verbose_name='Relate to Config Node. node_data get data from this',
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Title copy from node',
    )
    code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Code copy from node',
    )
    node_data = models.JSONField(
        default=dict,
        verbose_name='Detail of Config Node at this created',
        help_text=json.dumps(
            {"id": "", "title": "", "code": "", "date_created": ""}
        ),
    )
    actions = models.JSONField(
        default=dict,
        verbose_name='Action code array',
        help_text='Collect from Node.actions'
    )
    exit_node_conditions = models.JSONField(
        default=dict,
        verbose_name='Condition for exit node',
        help_text='Collect data from Node.condition)',
    )
    association_passed = models.ForeignKey(
        'workflow.Association',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Association was passed',
        help_text='Association selected when create stage from node'
    )
    association_passed_data = models.JSONField(
        default=dict,
        verbose_name='Storage data of association passed',
        help_text=json.dumps(
            {
                "id": "", "node_in": {"id": "", "title": "", "code": ""},
                "node_out": {"id": "", "title": "", "code": ""}, "condition": []
            }
        )
    )
    assignee_count = models.SmallIntegerField(
        default=0,
        verbose_name='Employee Count',
        help_text='Counter of assignee_and_zone, count employee',
    )
    assignee_and_zone = models.ManyToManyField(
        'hr.Employee',
        through='RuntimeAssignee',
        symmetrical=False,
        related_name='assignee_and_zone_of_runtime_stage',
        verbose_name='Employee + Zone need action in this stage',
        help_text='Assignee have task with properties zone',
    )
    assignee_and_zone_data = models.JSONField(
        default=dict,
        verbose_name='Summary assignee and zone data',
        help_text=json.dumps(
            {'employee_id': [{"id": "", "title": "", "remark": "", "properties": ['application_property_id']}]}
        )
    )

    # utils
    order = models.IntegerField(
        default=0,
        verbose_name='Order Number step in Runtime, Stage arrange in order by ASC (ascending)',
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='Node was created at time',
    )
    date_exit = models.DateTimeField(
        null=True,
        help_text='Node was exited at time',
    )
    from_stage = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Stage Before (from node)',
        related_name='stage_stage_before',
    )
    to_stage = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Stage After (to node)',
        related_name='stage_stage_after',
    )

    # utils
    log_count = models.SmallIntegerField(
        verbose_name='Total log of Stage',
        help_text='Support display UX of FE',
        default=0
    )

    @classmethod
    def generate_order(cls, runtime_obj) -> int:
        """
        Get max order of RUNTIME OBJ.
        Then return it plus one.
        Args:
            runtime_obj:    Runtime Object.

        Returns: Integer Number (max + 1)

        """
        order_list = cls.objects.filter(runtime=runtime_obj).values_list('order', flat=True)
        return max(order_list) + 1 if len(order_list) > 0 else 1

    def set_association_passed_data(self):
        if self.association_passed:
            self.association_passed_data = {
                "id": str(self.association_passed.id),
                "node_in": {
                    "id": str(self.association_passed.node_in.id),
                    "title": self.association_passed.node_in.title,
                    "code": self.association_passed.node_in.code,
                } if self.association_passed.node_in else {},
                "node_out": {
                    "id": str(self.association_passed.node_out.id),
                    "title": self.association_passed.node_out.title,
                    "code": self.association_passed.node_out.code,
                } if self.association_passed.node_out else {},
                "condition": self.association_passed.condition,
            }
        return True

    def before_save(self, force_insert=False):
        if force_insert and self.runtime:
            self.tenant = self.runtime.tenant
            self.company = self.runtime.company
            self.order = self.generate_order(self.runtime)
        self.set_association_passed_data()

    def save(self, *args, **kwargs):
        self.before_save(kwargs.get('force_insert', False))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Runtime Node'
        verbose_name_plural = 'Runtime Node'
        ordering = ('-order',)
        default_permissions = ()
        permissions = ()


class RuntimeAssignee(SimpleAbstractModel):
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )

    stage = models.ForeignKey(
        RuntimeStage,
        on_delete=models.CASCADE,
        related_name='assignee_of_runtime_stage',
        verbose_name='Assignee in Stage',
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='all_runtime_assignee_of_employee',
        verbose_name='Employee selected',
    )
    zone_and_properties = models.JSONField(
        default=dict,
        verbose_name='Zone detail and Properties ID of Zone | collect from Zone() and ApplicationProperties()',
        help_text=json.dumps(
            [{"id": "", "title": "", "remark": "", "properties": ['application_property_id']}]
        ),
    )
    action_perform = models.JSONField(
        default=list,
        verbose_name='Is action code array that was performed by assignee',
        help_text='[0,1,2,3]'
    )
    is_done = models.BooleanField(
        default=False,
        verbose_name='Flag status Task of assignee',
        help_text='True if assignee finish your task, False if assignee need action finish with approve, next,...'
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at time',
    )

    # backup data
    employee_data = models.JSONField(
        default=dict,
        verbose_name='Employee backup data',
        help_text=json.dumps(
            {
                'id': '', 'first_name': '', 'last_name': '', 'full_name': '', 'avatar': '',
            }
        ),
    )

    def before_save(self, force_insert=False):
        if force_insert:
            if self.stage:
                self.tenant = self.stage.tenant
                self.company = self.stage.company
            if self.employee:
                self.employee_data = self.employee.get_detail_minimal()
        return True

    def save(self, *args, **kwargs):
        self.before_save(kwargs.get('force_insert', False))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Stage map Employee plus Zone'
        verbose_name_plural = 'Stage map Employee plus Zone'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RuntimeLog(SimpleAbstractModel):
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )

    is_system = models.BooleanField(
        default=False,
        verbose_name='Is system Log',
    )
    actor = models.ForeignKey(
        'hr.Employee',
        null=True,
        on_delete=models.SET_NULL
    )
    actor_data = models.JSONField(
        default=dict,
        verbose_name="Employee's data changed docs",
        help_text='{"id": "", "first_name": "", "last_name": "", "email": "", "avatar": "",}'
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='Log Activity was created at time',
    )
    runtime = models.ForeignKey(
        'Runtime',
        on_delete=models.CASCADE,
        verbose_name='All log of Runtime Doc',
    )
    stage = models.ForeignKey(
        'RuntimeStage',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Log in Stage Runtime | =null when Runtime create + Dont apply WF',
        related_name='log_of_stage_runtime',
    )
    kind = models.SmallIntegerField(
        choices=KIND_LOG_ACTIVITY,
        verbose_name='Flag filter doc for some main case: login history, doc history only, flow history only.',
        help_text='0: log from login, 1: log from doc, 2: log from workflow',
    )
    action = models.SmallIntegerField(
        verbose_name='Action choice that was used by actor',
    )
    msg = models.TextField(
        verbose_name='Message log action of actor',
        blank=True
    )

    class Meta:
        verbose_name = 'Log Activity'
        verbose_name_plural = 'Log Activity'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def before_save(self, force_insert=False):
        if force_insert:
            self.tenant = self.stage.tenant
            self.company = self.stage.company
            if self.actor:
                self.actor_data = {
                    "id": str(self.actor_id),
                    "first_name": str(self.actor.first_name),
                    "last_name": str(self.actor.last_name),
                    "full_name": str(self.actor.get_full_name()),
                    "email": str(self.actor.email),
                    "avatar": str(self.actor.avatar),
                }
            else:
                self.is_system = True

        if not self.runtime and self.stage:
            self.runtime = self.stage.runtime

        if self.stage:
            self.stage.log_count += 1
            self.stage.save(update_fields=['log_count'])

    def save(self, *args, **kwargs):
        self.before_save(force_insert=kwargs.get('force_insert', False))
        super().save(*args, **kwargs)


class RuntimeViewer(SimpleAbstractModel):
    runtime = models.ForeignKey(
        Runtime,
        on_delete=models.CASCADE,
        verbose_name='Runtime of Viewer',
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name='Employee of Viewer',
    )
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )

    class Meta:
        verbose_name = 'Viewer Append of Runtime'
        verbose_name_plural = 'Viewer Append of Runtime'
        ordering = ('-date_created',)
        unique_together = ('runtime', 'employee')
        default_permissions = ()
        permissions = ()
