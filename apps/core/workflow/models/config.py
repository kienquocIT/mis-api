from django.db import models

from apps.shared import MasterDataAbstractModel, OPTION_COLLABORATOR, SimpleAbstractModel, WORKFLOW_CONFIG_MODE, \
    WORKFLOW_IN_WF_OPTION, WORKFLOW_IN_WF_POSITION


class WorkflowConfigOfApp(MasterDataAbstractModel):
    # title is title of app
    # code is code of app
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        verbose_name="application",
        related_name="workflow_config_of_application",
        null=True
    )
    mode = models.SmallIntegerField(
        choices=WORKFLOW_CONFIG_MODE,
        default=0,
        verbose_name='Mode feature in workflow',
    )
    error_total = models.SmallIntegerField(
        default=0,
        verbose_name='Error total in feature',
    )
    workflow_currently = models.ForeignKey(
        'workflow.Workflow',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Workflow applied of feature',
    )

    def before_save(self, *args, **kwargs):
        if kwargs.get('force_insert', False):
            if self.application:
                self.title = self.application.title
                self.code = self.application.code
        return True

    def save(self, *args, **kwargs):
        self.before_save(*args, **kwargs)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Workflow of Apps'
        verbose_name_plural = 'Workflow of Apps'
        ordering = ('title',)
        unique_together = ('company', 'application')
        default_permissions = ()
        permissions = ()


class Workflow(MasterDataAbstractModel):
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

    # [{0: "rename1"}, {1: "rename2"}, ....] (0, 1, 2... is option actions)
    actions_rename = models.JSONField(
        default=list,
        help_text="use for show rename of actions in specific workflow"
    )
    is_applied = models.BooleanField(
        default=False,
        help_text="to know what workflow is currently applied for application"
    )
    date_applied = models.DateField(
        null=True,
        help_text="date applied this workflow for application"
    )

    class Meta:
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Zone(MasterDataAbstractModel):
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
    properties = models.ManyToManyField(
        'base.ApplicationProperty',
        through='ZoneProperties',
        symmetrical=False,
        related_name='zones_map_properties',
    )
    property_list = models.JSONField(
        verbose_name="property list",
        default=list
    )
    order = models.IntegerField(
        null=True
    )

    class Meta:
        verbose_name = 'Zone in workflow'
        verbose_name_plural = 'Zone in workflow'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ZoneProperties(SimpleAbstractModel):
    app_property = models.ForeignKey(
        'base.ApplicationProperty',
        on_delete=models.CASCADE
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Zone Property'
        verbose_name_plural = 'Zones Properties'
        default_permissions = ()
        permissions = ()


class Node(MasterDataAbstractModel):
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
    actions = models.JSONField(
        verbose_name="actions",
        default=list,
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
        help_text="code nodes system: initial, approved, completed,...",
    )
    option_collaborator = models.SmallIntegerField(
        verbose_name="collaborator options",
        choices=OPTION_COLLABORATOR,
        default=0,
        help_text="option choose collaborator: In form, Out form, In workflow"
    )

    # data collab_in_form
    # {
    #     'property': {'id', 'title', 'code'},
    #     'zone': [{'id', 'title', 'order'}]
    # }
    collab_in_form = models.JSONField(
        default=dict,
        help_text="use for option in form"
    )

    # data collab_out_form
    # {
    #     'employee_list': [{'id', 'full_name'}],
    #     'zone': [{'id', 'title', 'order'}]
    # }
    collab_out_form = models.JSONField(
        default=dict,
        help_text="use for option out form"
    )

    # data collab_in_workflow
    # [
    #     {
    #         'employee': {'id', 'full_name', 'role'},
    #         'zone': [{'id', 'title', 'order'}]
    #     },
    #     {
    #         'employee': {'id', 'full_name', 'role'},
    #         'zone': [{'id', 'title', 'order'}]
    #     }
    # ]
    collab_in_workflow = models.JSONField(
        default=list,
        help_text="use for option in workflow"
    )

    zones_initial_node = models.ManyToManyField(
        Zone,
        through='InitialNodeZone',
        symmetrical=False,
        related_name='initial_node_map_zones',
    )
    # ['zoneID1', 'zoneID2', ....]
    zone_initial_node = models.JSONField(
        verbose_name="zone",
        default=list,
        help_text="list zones of initial node"
    )
    zones_hidden_initial_node = models.ManyToManyField(
        Zone,
        through='InitialNodeZoneHidden',
        symmetrical=False,
        related_name='initial_node_map_zones_hidden',
    )
    # ['zoneID1', 'zoneID2', ....]
    zone_hidden_initial_node = models.JSONField(
        verbose_name="init zone hidden",
        default=list,
        help_text="list zones hidden of initial node"
    )
    is_edit_all_zone = models.BooleanField(
        default=False,
        help_text='flag to know collaborator can edit whole document (not check zone)'
    )

    order = models.IntegerField(
        null=True
    )

    # data of condition:
    #     [
    #         {
    #             'action': 1,
    #             'min_collaborator': 2
    #         },
    #         {
    #             'action': 2,
    #             'min_collaborator': 1
    #         },
    #         {
    #             'action': 3,
    #             'min_collaborator': 'else'
    #         }
    #     ]
    condition = models.JSONField(
        verbose_name="Condition",
        blank=True,
        null=True,
        default=list
    )
    # data of coordinates:
    # {"top": 1231.5, "left": 1234.5}
    coordinates = models.JSONField(
        verbose_name="coordinates",
        default=dict
    )

    class Meta:
        verbose_name = 'Node'
        verbose_name_plural = 'Nodes'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class Association(MasterDataAbstractModel):
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
    node_in_data = models.JSONField(
        default=dict,
    )
    node_out_data = models.JSONField(
        default=dict,
    )

    # data of field condition:
    #     [
    #         {'left': 'a', 'math': 'is', 'right': 'b', 'type': 'string'},
    #         'AND',
    #         {'left': 'a', 'math': 'is', 'right': 'b', 'type': 'string'},
    #         'AND',
    #         [
    #             {'left': 'b', 'math': '=', 'right': 1, 'type': 'number'},
    #             'OR',
    #             {'left': 'b', 'math': '=', 'right': 0, 'type': 'number'},
    #             'OR',
    #         ],
    #         'AND',
    #         [
    #             {'left': 'c', 'math': 'is', 'right': True, 'type': 'boolean'},
    #             'AND',
    #             {'left': 'c', 'math': 'is', 'right': False, 'type': 'boolean'},
    #             'AND',
    #         ],
    #         'AND',
    #     ]
    condition = models.JSONField(
        verbose_name="Condition",
        blank=True,
        null=True,
        default=list
    )

    class Meta:
        verbose_name = 'Association'
        verbose_name_plural = 'Associations'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


# SUPPORT INITIAL NODE
class InitialNodeZone(SimpleAbstractModel):
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='init_node_zone_node'
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='init_node_zone_zone'
    )

    class Meta:
        verbose_name = 'Initial Node Zone'
        verbose_name_plural = 'Initial Node Zones'
        default_permissions = ()
        permissions = ()


class InitialNodeZoneHidden(SimpleAbstractModel):
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='init_node_zone_hidden_node'
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='init_node_zone_hidden_zone'
    )

    class Meta:
        verbose_name = 'Initial Node Zone Hidden'
        verbose_name_plural = 'Initial Node Zones Hidden'
        default_permissions = ()
        permissions = ()


# SUPPORT IN FORM
class CollaborationInForm(MasterDataAbstractModel):
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
    )
    app_property = models.ForeignKey(
        'base.ApplicationProperty',
        on_delete=models.CASCADE
    )
    zone = models.ManyToManyField(
        Zone,
        through='CollaborationInFormZone',
        symmetrical=False,
        related_name='collab_in_forms_map_zones'
    )
    zone_hidden = models.ManyToManyField(
        Zone,
        through='CollaborationInFormZoneHidden',
        symmetrical=False,
        related_name='collab_in_forms_map_zones_hidden'
    )
    is_edit_all_zone = models.BooleanField(
        default=False,
        help_text='flag to know collaborator can edit whole document (not check zone)'
    )

    class Meta:
        verbose_name = 'Collab in form'
        verbose_name_plural = 'Collab in form'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class CollaborationInFormZone(SimpleAbstractModel):
    collab = models.ForeignKey(
        CollaborationInForm,
        on_delete=models.CASCADE,
        related_name='in_form_zone_collab'
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='in_form_zone_zone'
    )

    class Meta:
        verbose_name = 'Collab in form zone'
        verbose_name_plural = 'Collab in form zones'
        default_permissions = ()
        permissions = ()


class CollaborationInFormZoneHidden(SimpleAbstractModel):
    collab = models.ForeignKey(
        CollaborationInForm,
        on_delete=models.CASCADE,
        related_name='in_form_zone_hidden_collab'

    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='in_form_zone_hidden_zone'
    )

    class Meta:
        verbose_name = 'Collab in form zone hidden'
        verbose_name_plural = 'Collab in form zones hidden'
        default_permissions = ()
        permissions = ()


# SUPPORT OUT FORM
class CollaborationOutForm(MasterDataAbstractModel):
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
    )
    employees = models.ManyToManyField(
        'hr.Employee',
        through='CollaborationOutFormEmployee',
        related_name='collab_out_forms_map_employees'
    )
    zone = models.ManyToManyField(
        Zone,
        through='CollaborationOutFormZone',
        related_name='collab_out_forms_map_zones'
    )
    zone_hidden = models.ManyToManyField(
        Zone,
        through='CollaborationOutFormZoneHidden',
        related_name='collab_out_forms_map_zones_hidden'
    )
    is_edit_all_zone = models.BooleanField(
        default=False,
        help_text='flag to know collaborator can edit whole document (not check zone)'
    )

    class Meta:
        verbose_name = 'Collab out form'
        verbose_name_plural = 'Collab out form'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class CollaborationOutFormEmployee(SimpleAbstractModel):
    collab = models.ForeignKey(
        CollaborationOutForm,
        on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Collab out form employee'
        verbose_name_plural = 'Collab out form employees'
        default_permissions = ()
        permissions = ()


class CollaborationOutFormZone(SimpleAbstractModel):
    collab = models.ForeignKey(
        CollaborationOutForm,
        on_delete=models.CASCADE,
        related_name='out_form_zone_collab'
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='out_form_zone_zone'
    )

    class Meta:
        verbose_name = 'Collab out form zone'
        verbose_name_plural = 'Collab out form zones'
        default_permissions = ()
        permissions = ()


class CollaborationOutFormZoneHidden(SimpleAbstractModel):
    collab = models.ForeignKey(
        CollaborationOutForm,
        on_delete=models.CASCADE,
        related_name='out_form_zone_hidden_collab'
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='out_form_zone_hidden_zone'
    )

    class Meta:
        verbose_name = 'Collab out form zone hidden'
        verbose_name_plural = 'Collab out form zones hidden'
        default_permissions = ()
        permissions = ()


# SUPPORT IN WORKFLOW
class CollabInWorkflow(MasterDataAbstractModel):
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
    )
    in_wf_option = models.SmallIntegerField(
        choices=WORKFLOW_IN_WF_OPTION,
        verbose_name='in wf option',
        help_text='option to select collab in WF (by position/ by employee/...)',
    )
    position_choice = models.SmallIntegerField(
        choices=WORKFLOW_IN_WF_POSITION,
        null=True,
        verbose_name='position choice (in_wf_option==1)',
        help_text='position choice (1st manager, 2nd manager,...) help to get exact employee of Node when Runtime',
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='employee (in_wf_option==2)',
        help_text='exact employee of Node when Runtime',
    )
    zone = models.ManyToManyField(
        Zone,
        through='CollabInWorkflowZone',
        related_name='collab_in_workflows_map_zones'
    )
    zone_hidden = models.ManyToManyField(
        Zone,
        through='CollabInWorkflowZoneHidden',
        related_name='collab_in_workflows_map_zones_hidden'
    )
    is_edit_all_zone = models.BooleanField(
        default=False,
        help_text='flag to know collaborator can edit whole document (not check zone)'
    )

    class Meta:
        verbose_name = 'Collab in workflow'
        verbose_name_plural = 'Collab in workflow'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class CollabInWorkflowZone(SimpleAbstractModel):
    collab = models.ForeignKey(
        CollabInWorkflow,
        on_delete=models.CASCADE,
        related_name='in_wf_zone_collab'
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='in_wf_zone_zone'
    )

    class Meta:
        verbose_name = 'Collab in workflow zone'
        verbose_name_plural = 'Collab in workflow zones'
        default_permissions = ()
        permissions = ()


class CollabInWorkflowZoneHidden(SimpleAbstractModel):
    collab = models.ForeignKey(
        CollabInWorkflow,
        on_delete=models.CASCADE,
        related_name='in_wf_zone_hidden_collab'
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='in_wf_zone_hidden_zone'
    )

    class Meta:
        verbose_name = 'Collab in workflow zone hidden'
        verbose_name_plural = 'Collab in workflow zones hidden'
        default_permissions = ()
        permissions = ()
