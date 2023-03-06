from typing import Union
from uuid import UUID

from django.db.models import Q


class PermCheck:
    perm_key_id = 'by_id'
    perm_key_configured = 'by_configured'

    def __init__(self, employee_id: Union[UUID, str], permissions: dict):
        self.employee_id = employee_id
        self.permissions = permissions
        self.perm_configured = permissions.get(self.perm_key_configured, {})
        self.perm_ids = permissions.get(self.perm_key_id, {})

    def for_list(self, code_perm) -> Q:
        q_configured = None
        if code_perm in self.perm_configured:
            data_configured = self.perm_configured[code_perm]
            if 'option' in data_configured:
                match data_configured['option']:
                    case 1:
                        q_configured = Q(
                            Q(employee_created=str(self.employee_id)),
                            Q.OR,
                            Q(employee_inherit=str(self.employee_id))
                        )
                    case 2:
                        ...
                    case 3:
                        ...
                    case 4:
                        ...

        q_ids = None
        if code_perm in self.perm_ids:
            data_ids = self.perm_ids[code_perm]
            if isinstance(data_ids, list):
                q_ids = Q(id__in=data_ids)

        if q_configured and q_ids:
            q_result = Q(q_configured, Q.OR, q_ids)
        elif q_configured:
            q_result = q_configured
        elif q_ids:
            q_result = q_ids
        else:
            q_result = None
        return q_result if q_result else None

    # def for_id(self, doc_obj, new_data=None) -> bool:
    #     print(self.employee_id)
    #     return True
