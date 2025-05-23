import io
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.hr.models import Employee
from apps.shared.extends.tests import AdvanceTestCase


class KMSDocumentApprovalTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()
        url_emp = reverse("EmployeeListAll")
        response = self.client.get(url_emp, format='json')
        employee_obj = Employee.objects.get(id=response.data['result'][0]['id'])
        self.employee = employee_obj
        self.company = employee_obj.company

        # attachment
        data = {
            'file': (io.BytesIO(b"file test KMS document approval"), 'test_doc_apr.txt')
        }
        attach_response = self.client.post(reverse("FilesUpload"), data=data, content_type='multipart/form-data')
        self.assertEqual(attach_response.status_code, 201)
        self.attach = attach_response

        # doc type
        data_doc_type = {
            'title': 'loại tài liệu 01',
            'code': 'TYPEC01'
        }
        dtype_res = self.client.post(reverse("KSMDocumentTypeList"), data_doc_type, format='json')
        self.assertEqual(dtype_res.status_code, 201)
        self.doc_type = dtype_res

        # content group
        data_con_grp = {
            'title': 'nhóm nội dung 01',
            'code': 'CONGRP01'
        }
        cgrp_res = self.client.post(reverse("KSMContentGroupList"), data_con_grp, format='json')
        self.assertEqual(cgrp_res.status_code, 201)
        self.con_grp = cgrp_res

    def test_create_new_doc_apr(self):
        data = {
            'title': 'test create new doc apr',
            'remark': 'mô tả tài liệu cho cong ty',
            'attached_list': [{
                'attachment': [self.attach.id],
                'title': 'test list cho doc approval',
                'document_type': self.doc_type.id,
                'content_group': self.con_grp.id,
                'security_lv': 1,
                'published_place': '',
                'effective_date': '',
                'expired_date': '',
            }],
            'internal_recipient': [{

            }]
        }
