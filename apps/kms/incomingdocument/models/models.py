import json

from django.db import models
from apps.core.company.models import CompanyFunctionNumber
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel


SECURITY_LV = (
    (0, 'low'),
    (1, 'medium'),
    (2, 'high')
)

KIND = (
    (1, 'employee'),
    (2, 'group')
)

KIND_PERM = (
    (1, 'preview'),
    (2, 'viewer'),
    (3, 'editor'),
    (4, 'custom')
)


class KMSIncomingDocument(DataAbstractModel):
    pass




