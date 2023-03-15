from uuid import uuid4

from django.db import models


class Process(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)

    class Meta:
        default_permissions = ()
        permissions = ()
