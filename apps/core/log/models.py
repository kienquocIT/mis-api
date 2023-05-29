from django.db import models
from django.utils import timezone

from apps.shared import SimpleAbstractModel

__all__ = ['LogActivity']

LOG_LEVEL = (
    (0, 'Success'),
    (1, 'Failure'),
    (2, 'Info'),
    (3, 'Error')
)

LOG_ACTIONS = (
    (0, 'Information'),
    (1, 'Create'),
    (2, 'Change'),
    (3, 'Delete'),
    (4, 'Cancel'),
)

LOG_FLOW_ACTIONS = (
    (0, 'Information'),
    (1, 'Next'),
    (2, 'Approved'),
    (3, 'Reject'),
    (4, 'Return'),
    (5, 'Edit'),
)


class LogActivity(SimpleAbstractModel):
    doc_id = models.UUIDField(null=True, verbose_name='Log of the document ID')
    app = models.ForeignKey(
        'base.Application',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Log of feature app',
    )
    level = models.IntegerField(choices=LOG_LEVEL, verbose_name='LEVEL of log')
    action = models.IntegerField(choices=LOG_ACTIONS, verbose_name='Name of event')
    flow_action = models.IntegerField(choices=LOG_FLOW_ACTIONS, null=True, verbose_name='Action name user submit in WF')
    flow_station = models.CharField(max_length=150, blank=True)
    msg_extras = models.TextField(blank=True, verbose_name='Help text display for this log')

    is_system = models.BooleanField(default=False, verbose_name='Flag classify log user or system')
    actor_id = models.UUIDField(null=True, verbose_name='Actor of request')
    actor_data = models.JSONField(default={})
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )

    class Meta:
        verbose_name = 'Log Data'
        verbose_name_plural = 'Log Data'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
