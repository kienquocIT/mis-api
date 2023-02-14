from django.contrib.auth.models import Permission

from ..translations import APIMsg
from ..constant import PERMISSION_OPTION


class PermissionSerializer:
    OPTION_IDX_ALLOWED = [x[0] for x in PERMISSION_OPTION]
