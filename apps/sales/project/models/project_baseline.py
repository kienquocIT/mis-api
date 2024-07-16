__all__ = ['ProjectBaseline']

import json
from django.db import models

from apps.shared import DataAbstractModel


class ProjectBaseline(DataAbstractModel):
    project_related = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_project_related",
    )
    project_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            {
                "id": "ce0c0422-ffb8-4891-aaf7-c54bc7f17d9a",
                "title": "Kietht edit and update",
                "code": "PJ008",
                "start_date": "2024-07-23 00:00:00",
                "finish_date": "2024-07-27 00:00:00",
                "completion_rate": 0,
                "project_pm": {
                    "id": "ddbaf4ba-1f1a-487f-a37d-b6847c1bf901",
                    "code": "EMP14",
                    "full_name": "Huỳnh Tuấn Kiệt"
                },
                "employee_inherit": {
                    "id": "8b930c65-2794-4904-89db-e7b992f49554",
                    "code": "EMP0004",
                    "full_name": "Hồ Vân Quỳnh"
                },
                "system_status": 1,
                "works": [
                    {
                        "id": "587fc1fb-df7f-4694-883b-4f330ebecb09",
                        "title": "Công việc 01",
                        "work_status": 0,
                        "date_from": "2024-07-02T00:00:00",
                        "date_end": "2024-07-07T00:00:00",
                        "order": 1,
                        "group": "",
                        "relationships_type": None,
                        "dependencies_parent": "",
                        "progress": 0,
                        "weight": 10,
                        "expense_data": {
                            "tax": 100,
                            "price": 1000,
                            "total_after_tax": 1100
                        }
                    }
                ],
                "groups": [],
                "members": [
                    {
                        "id": "ddbaf4ba-1f1a-487f-a37d-b6847c1bf901",
                        "first_name": "Kiệt",
                        "last_name": "Huỳnh Tuấn",
                        "full_name": "Huỳnh Tuấn Kiệt",
                        "email": "ldhoa2002@gmail.com",
                        "avatar": None,
                        "is_active": True
                    }
                ],
                "workflow_runtime_id": None,
                "is_change": False,
                "document_root_id": None,
                "document_change_order": None,
                "status": 200
            }
        ),
        verbose_name='Project data'
    )
    member_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            [
                {
                    "id": "ef3ab1bb-e699-4250-ac6d-aefacb77385e",
                    "date_modified": "2024-07-01 09:54:39",
                    "permit_view_this_project": True,
                    "permit_add_member": True,
                    "permit_add_gaw": True,
                    "permission_by_configured": [
                        {
                            "id": "0031870a-db7d-4deb-bba6-a9ea8b713a0c",
                            "edit": True,
                            "view": True,
                            "range": "1",
                            "space": "0",
                            "app_id": "e66cfb5a-b3ce-4694-a4da-47618f53de4c",
                            "create": True,
                            "delete": True
                        }
                    ],
                    "status": 200
                },
            ]
        ),
        verbose_name='Member data list'
    )
    member_perm_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            {
                "ef3ab1bb-e699-4250-ac6d-aefacb77385e": [{
                    'id': "ef3ab1bb-e699-4250-ac6d-aefacb77385e",
                    'date_modified': "2024-07-01 09:54:39",
                    'permit_view_this_project': True,
                    'permit_add_member': True,
                    'permit_add_gaw': True,
                    'permission_by_configured': [{
                        "id": "0031870a-db7d-4deb-bba6-a9ea8b713a0c", "edit": True,
                        "view": True, "range": "1", "space": "0",
                        "app_id": "e66cfb5a-b3ce-4694-a4da-47618f53de4c", "create": True,
                        "delete": True
                    }],
                },
                ]
            }
        ),
        verbose_name='Employee perm data list'
    )
    work_task_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            [
                {
                    'id': '',
                    'task': {'id': '', 'title': 'lorem ipsum', 'code': 'XX0X'},
                    'work': {'id': '', 'title': 'lorem ipsum', 'code': 'XX0X'},
                    'percent': 0,
                    'assignee': {'id': '', 'full_name': 'Nguyen van A'},
                    'work_before': {'id': '', 'title': 'lorem ipsum', 'code': 'XX0X'},
                }
            ]
        ),
        verbose_name='Work task list'
    )
    work_expense_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            [
                {
                    "id": "29801e4c-225b-44a7-b739-a69f84ecc49e",
                    "title": "lorem ipsum dolor sit amet",
                    "expense_name": {},
                    "expense_item": {
                        "id": "90357742-baa9-4a17-a20a-ace15483e111",
                        "title": "Chi phí nhân công phát triển PM"
                    },
                    "uom": {
                        "id": "a16e3b9e-2f4a-442e-bc54-b6ec18569d3c",
                        "title": "Second"
                    },
                    "quantity": 1,
                    "expense_price": 1000,
                    "tax": {
                        "id": "12628b53-7248-4f3b-9ec1-19590a41ecff",
                        "title": "VAT10%",
                        "rate": 10
                    },
                    "sub_total": 1000,
                    "sub_total_after_tax": 1100,
                    "is_labor": False
                },
            ]
        )
    )
    baseline_version = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.system_status == 3:
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
            else:
                kwargs.update({'update_fields': ['code']})
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Project baseline'
        verbose_name_plural = 'Project baseline'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
