from django.db import models
from jsonfield import JSONField

from apps.shared import TenantCoreModel


WORKFLOW_ACTION = (
    (0, "Create"),
    (1, "Approve"),
    (2, "Reject"),
    (3, "Return"),
    (4, "Receive"),
    (5, "To do"),
)


class Workflow(TenantCoreModel):
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
    name = models.TextField(
        verbose_name="name",
        required=True
    )
    remark = models.TextField(
        verbose_name="description",
        required=False
    )
    zone_field = JSONField(
        verbose_name="zone field",
        required=True,
        default=[]
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
    remarks = models.TextField(
        verbose_name="remarks",
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
        help_text="nodes of system: Initial, Approve, Complete,...",
        default=False,
    )
    option_audit = models.SmallIntegerField(
        verbose_name="audit options",
        default=0,
        help_text="option choose audit: In form, Out form, In workflow"
    )

    # use for option_audit in [In form, Out form]
    employee_list = JSONField(
        verbose_name="employees",
        default=[],
        help_text="list employees, depend on option"
    )
    zone = JSONField(
        verbose_name="zone",
        default=[],
        help_text="list zones of audit"
    )

    class Meta:
        verbose_name = 'Node'
        verbose_name_plural = 'Nodes'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Audit(TenantCoreModel):
    node = models.ForeignKey(
        'workflow.Node',
        on_delete=models.CASCADE,
        verbose_name="node",
        related_name="audit_node",
        null=True
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="employee",
        related_name="audit_employee",
        null=True
    )
    zone = JSONField(
        verbose_name="zone",
        default=[],
        help_text="list zones of audit"
    )

    class Meta:
        verbose_name = 'Audit'
        verbose_name_plural = 'Audits'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Transition(TenantCoreModel):
    node_input = models.ForeignKey(
        'workflow.Node',
        on_delete=models.CASCADE,
        verbose_name="node input",
        related_name="transition_node_input",
        null=True
    )
    node_output = models.ForeignKey(
        'workflow.Node',
        on_delete=models.CASCADE,
        verbose_name="node output",
        related_name="transition_node_output",
        null=True
    )
    condition = JSONField(
        verbose_name="Condition",
        blank=True,
        null=True,
        default=[]
    )

    class Meta:
        verbose_name = 'Transition'
        verbose_name_plural = 'Transitions'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

