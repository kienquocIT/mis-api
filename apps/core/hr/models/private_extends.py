__all__ = [
    'SYNC_STATE',
    'PermOption',
    'PermissionAbstractModel',
]

from typing import TypedDict

from django.db import models

from apps.shared.permissions.util import PermissionController

SYNC_STATE = (
    (0, 'Fail'),
    (1, 'Success'),
    (2, 'Pending'),
)


class PermOption(TypedDict, total=False):
    option: int


class PermissionAbstractModel(models.Model):
    distribution_plan_cls_code = 'hr.DistributionPlan'
    distribution_app_cls_code = 'hr.DistributionApplication'

    permission_simple_sample = {
        'hr.employee.view': {
            '{range}': '{range_data}'
        }
    }

    # by ID
    permission_by_id_sample = {
        'hr.employee.view': [],
        'hr.employee.edit': [],
        '{app_label}.{model_code}.{perm_code}': ['{doc_id}'],
    }
    permission_by_id = models.JSONField(default=dict, verbose_name='Special Permissions with ID Doc')

    # by be configured
    permission_by_configured_sample = [
        {
            "id": "e388f95e-457b-4cf6-8689-0171e71fa58f",
            "app_id": "50348927-2c4f-4023-b638-445469c66953",
            "app_data": {
                "id": "50348927-2c4f-4023-b638-445469c66953",
                "title": "Employee",
                "code": "employee",
            },
            "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",
            "plan_data": {
                "id": "395eb68e-266f-45b9-b667-bd2086325522",
                "title": "HRM",
                "code": "hrm",
            },
            "create": True, "view": True, "edit": False, "delete": False, "range": "4",
        }
    ]
    permission_by_configured = models.JSONField(
        default=list, verbose_name='Permissions was configured by Administrator',
    )

    # by opportunity
    permission_by_opp_sample_before_sync = {
        '{opp_id}': [
            {
                "id": "e388f95e-457b-4cf6-8689-0171e71fa58f",
                "app_id": "50348927-2c4f-4023-b638-445469c66953",
                "app_data": {
                    "id": "50348927-2c4f-4023-b638-445469c66953",
                    "title": "Employee",
                    "code": "employee",
                },
                "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",
                "plan_data": {
                    "id": "395eb68e-266f-45b9-b667-bd2086325522",
                    "title": "HRM",
                    "code": "hrm",
                },
                "create": True, "view": True, "edit": False, "delete": False,
                "range": "{'me'|'all'}",
            }
        ],
    }
    permission_by_opp_sample = {
        '{opp_id}': {
            'hr.employee.view': {
                'me': {},
                'all': {},
            }
        }
    }
    permission_by_opp = models.JSONField(
        default=dict, verbose_name='Permission was configured at Opportunity',
    )

    # by project
    permission_by_project_sample = {
        '{project_id}': [
            {
                "id": "e388f95e-457b-4cf6-8689-0171e71fa58f",
                "app_id": "50348927-2c4f-4023-b638-445469c66953",
                "app_data": {
                    "id": "50348927-2c4f-4023-b638-445469c66953",
                    "title": "Employee",
                    "code": "employee",
                },
                "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",
                "plan_data": {
                    "id": "395eb68e-266f-45b9-b667-bd2086325522",
                    "title": "HRM",
                    "code": "hrm",
                },
                "create": True, "view": True, "edit": False, "delete": False,
                "range": "{'me'|'all'}",
            }
        ]
    }
    permission_by_project = models.JSONField(
        default=dict, verbose_name='Permission was configured at Project',
    )

    # as sum data permissions
    permissions_parsed_sample = {
        'hr.employee.view': {
            '4': {},
            'ids': {
                '{doc_id}': {},
            },
            'opp': {
                '{opp_id}': {
                    'me': {},
                    'all': {},
                },
            },
            'prj': {
                '{project_id}': {
                    'me': {},
                    'all': {},
                },
            },
        },
        'hr.employee.edit': {'4': {}},
        '{app_label}.{model_code}.{perm_code}': {'{range_code}': {}},
    }
    permissions_parsed = models.JSONField(default=dict, verbose_name='Data was parsed')

    # summary keys
    permission_keys = ('permission_by_id', 'permission_by_configured')

    def get_app_allowed(self) -> tuple[list[str], list[str]] | str:
        """
        Return to array application list (ID) that instance was allowed!
        Returns:
            list[str] : app ids allowed
            str: Employee ID caller get app from distribution
        """
        raise NotImplementedError

    def sync_parsed_to_main(self):
        raise NotImplementedError

    def call_sync(self):
        if hasattr(self, 'sync_parsed_to_main') and callable(self.sync_parsed_to_main):
            self.sync_parsed_to_main()
            return True
        return False

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    def _remove_ids_empty(self):
        for permit_code, permit_ids in dict(self.permission_by_id).items():
            if not permit_ids:
                del self.permission_by_id[permit_code]

    def append_permit_by_ids(self, app_label, model_code, perm_code, doc_id, tenant_id):
        if app_label and model_code and perm_code:
            key = f'{app_label}.{model_code}.{perm_code}'.lower()

            self._remove_ids_empty()

            permission_by_id = self.permission_by_id

            if key not in permission_by_id:
                permission_by_id[key] = {}
            permission_by_id[key] = {**permission_by_id[key], str(doc_id): {}}

            self.permission_by_id = permission_by_id
            self.permissions_parsed = PermissionController(tenant_id=tenant_id).get_permission_parsed(
                instance=self
            )
            super().save(update_fields=['permission_by_id', 'permissions_parsed'])
            self.call_sync()
        return self

    def _remove_opp_empty(self):
        for opp_id, permit_opp_data in dict(self.permission_by_opp).items():
            if not permit_opp_data:
                del self.permission_by_opp[opp_id]

    def append_permit_by_opp(self, tenant_id, opp_id, perm_config):
        if opp_id and tenant_id:
            self.permission_by_opp[str(opp_id)] = perm_config
            self._remove_opp_empty()
            self.permissions_parsed = PermissionController(tenant_id=tenant_id).get_permission_parsed(instance=self)
            super().save(update_fields=['permission_by_opp', 'permissions_parsed'])
            self.call_sync()
        return self

    def remove_permit_by_opp(self, tenant_id,  opp_id):
        if opp_id and str(opp_id) in self.permission_by_opp and tenant_id:
            del self.permission_by_opp[opp_id]
            self._remove_opp_empty()
            self.permissions_parsed = PermissionController(tenant_id=tenant_id).get_permission_parsed(instance=self)
            super().save(update_fields=['permission_by_opp', 'permissions_parsed'])
            self.call_sync()
        return self

    def _remove_prj_empty(self):
        for prj_id, permit_prj_data in dict(self.permission_by_project).items():
            if not permit_prj_data:
                del self.permission_by_opp[prj_id]

    def append_permit_by_prj(self, tenant_id, prj_id, perm_config):
        if prj_id and tenant_id:
            self.permission_by_project[prj_id] = perm_config
            self._remove_prj_empty()
            self.permissions_parsed = PermissionController(tenant_id=tenant_id).get_permission_parsed(instance=self)
            super().save(update_fields=['permission_by_project', 'permissions_parsed'])
            self.call_sync()
        return self

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
