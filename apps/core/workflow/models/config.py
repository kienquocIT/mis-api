from django.db import models
from jsonfield import JSONField

from apps.shared import TenantCoreModel, WorkflowMsg, OPTION_COLLABORATOR

WORKFLOW_ACTION = (
    (0, WorkflowMsg.ACTION_CREATE),
    (1, WorkflowMsg.ACTION_APPROVE),
    (2, WorkflowMsg.ACTION_REJECT),
    (3, WorkflowMsg.ACTION_RETURN),
    (4, WorkflowMsg.ACTION_RECEIVE),
    (5, WorkflowMsg.ACTION_TODO),
)


class Workflow(TenantCoreModel):
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        verbose_name="application",
        related_name="workflow_application",
        null=True
    )
    code_application = models.TextField(
        verbose_name="code application",
        null=True,
        help_text="code of application in base"
    )
    is_active = models.BooleanField(
        verbose_name='active status',
        default=True
    )
    is_multi_company = models.BooleanField(
        verbose_name='Multi company',
        default=False
    )
    is_define_zone = models.BooleanField(
        verbose_name='Define zone',
        default=False
    )

    # [{0: "rename1"}, {1: "rename2"}, ....]
    actions_rename = JSONField(
        default=[],
        help_text="use for show rename of actions in specific workflow"
    )
    is_in_use = models.BooleanField(
        null=True,
        help_text="to know what workflow is currently config for application"
    )

    class Meta:
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Zone(TenantCoreModel):
    workflow = models.ForeignKey(
        'workflow.Workflow',
        on_delete=models.CASCADE,
        related_name="zone_workflow",
        null=False
    )
    remark = models.TextField(
        verbose_name="Description",
        blank=True,
        null=True
    )
    property_list = JSONField(
        verbose_name="property list",
        default=[]
    )
    order = models.IntegerField(
        null=True
    )

    class Meta:
        verbose_name = 'Zone in workflow'
        verbose_name_plural = 'Zone in workflow'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Node(TenantCoreModel):
    workflow = models.ForeignKey(
        'workflow.Workflow',
        on_delete=models.CASCADE,
        verbose_name="workflow",
        related_name="node_workflow",
        null=True
    )
    remark = models.TextField(
        verbose_name="Description",
        null=True,
        blank=True
    )
    actions = JSONField(
        verbose_name="actions",
        default=[],
        help_text="actions of node"
    )
    is_system = models.BooleanField(
        verbose_name="is system",
        default=False,
        help_text="check if is nodes system",
    )
    code_node_system = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="code nodes system: Initial, Approve, Complete,...",
    )
    option_collaborator = models.SmallIntegerField(
        verbose_name="collaborator options",
        choices=OPTION_COLLABORATOR,
        default=0,
        help_text="option choose collaborator: In form, Out form, In workflow"
    )
    # use for option_collaborator In form
    field_select_collaborator = models.CharField(
        max_length=550,
        blank=True,
        null=True,
        help_text="field has data employees in document, option 1"
    )
    # use for option_collaborator Out form
    collaborator_list = JSONField(
        verbose_name="employees",
        default=[],
        help_text="list employees, option 2"
    )
    zone = JSONField(
        verbose_name="zone",
        default=[],
        help_text="list zones of collaborator"
    )
    order = models.IntegerField(
        null=True
    )

    """
    data of field condition:
        [
            {
                'action': 1,
                'min_collaborator': 2
            },
            {
                'action': 2,
                'min_collaborator': 1
            },
            {
                'action': 3,
                'min_collaborator': 'else'
            }
        ]
    """
    condition = JSONField(
        verbose_name="Condition",
        blank=True,
        null=True,
        default=[]
    )

    class Meta:
        verbose_name = 'Node'
        verbose_name_plural = 'Nodes'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Collaborator(TenantCoreModel):
    node = models.ForeignKey(
        'workflow.Node',
        on_delete=models.CASCADE,
        verbose_name="node",
        related_name="collaborator_node",
        null=True
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="employee",
        related_name="collaborator_employee",
        null=True
    )
    zone = JSONField(
        verbose_name="zone",
        default=[],
        help_text="list zones of collaborator"
    )

    class Meta:
        verbose_name = 'Collaborator'
        verbose_name_plural = 'Collaborators'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Association(TenantCoreModel):
    workflow = models.ForeignKey(
        'workflow.Workflow',
        on_delete=models.CASCADE,
        verbose_name="workflow",
        related_name="association_workflow",
        null=True
    )
    node_in = models.ForeignKey(
        'workflow.Node',
        on_delete=models.CASCADE,
        verbose_name="node input",
        related_name="transition_node_input",
    )
    node_out = models.ForeignKey(
        'workflow.Node',
        on_delete=models.CASCADE,
        verbose_name="node output",
        related_name="transition_node_output",
    )

    """
    data of field condition:
        [
            {'left': 'a', 'math': 'is', 'right': 'b', 'type': 'string'},
            'AND',
            {'left': 'a', 'math': 'is', 'right': 'b', 'type': 'string'},
            'AND',
            [
                {'left': 'b', 'math': '=', 'right': 1, 'type': 'number'},
                'OR',
                {'left': 'b', 'math': '=', 'right': 0, 'type': 'number'},
                'OR',
            ],
            'AND',
            [
                {'left': 'c', 'math': 'is', 'right': True, 'type': 'boolean'},
                'AND',
                {'left': 'c', 'math': 'is', 'right': False, 'type': 'boolean'},
                'AND',
            ],
            'AND',
        ]
    """
    condition = JSONField(
        verbose_name="Condition",
        blank=True,
        null=True,
        default=[]
    )

    class Meta:
        verbose_name = 'Association'
        verbose_name_plural = 'Associations'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
