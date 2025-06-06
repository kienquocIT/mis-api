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
        response = self.client.get(reverse("EmployeeListAll"), format='json')
        employee_obj = Employee.objects.get(id=response.data['result'][0]['id'])
        self.employee = employee_obj
        self.company = employee_obj.company

        # attachment
        data = {
            'file': (io.BytesIO(b"file test KMS document approval"), 'test_doc_apr.txt')
        }
        attach_response = self.client.post(reverse("FilesUpload"), data)
        self.assertEqual(attach_response.status_code, 201)
        self.attach = attach_response.data['result']

        # doc type
        data_doc_type = {
            'title': 'loại tài liệu 01',
            'code': 'TYPEC01'
        }
        dtype_res = self.client.post(reverse("KSMDocumentTypeList"), data_doc_type, format='json')
        self.assertEqual(dtype_res.status_code, 201)
        self.doc_type = dtype_res.data['result']

        # content group
        data_con_grp = {
            'title': 'nhóm nội dung 01',
            'code': 'CONGRP01'
        }
        con_grp_res = self.client.post(reverse("KSMContentGroupList"), data_con_grp, format='json')
        self.assertEqual(con_grp_res.status_code, 201)
        self.con_grp = con_grp_res.data['result']

    def test_create_new_doc_apr(self):
        employee_id = str(self.employee.id)
        data = {
            'title': 'test create new doc apr',
            'remark': 'mô tả tài liệu cho cong ty',
            'attached_list': [{
                'attachment': [str(self.attach['id'])],
                'title': 'test list cho doc approval',
                'document_type': str(self.doc_type['id']),
                'content_group': str(self.con_grp['id']),
                'security_lv': 1,
                'effective_date': '2025-05-23',
                'expired_date': '2025-12-23',
            }],
            'internal_recipient': [{
                'title': 'title recipient',
                'kind': 2,
                'employee_access': {
                    employee_id: {
                        'id': employee_id,
                        'full_name': self.employee.get_full_name(),
                        'code': str(self.employee.code)
                    }
                },
                'document_permission_list': [1, 2, 3, 4, 5, 6, 7],
                'expiration_date': '2025-06-20'
            }]
        }
        response = self.client.post(reverse('KMSDocumentApprovalRequestList'), data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_get_list_doc_apr(self):
        self.test_create_new_doc_apr()
        response = self.client.get(reverse('KMSDocumentApprovalRequestList'), format='json')
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )
        self.assertCountEqual(
            response.data['result'][0],
            ['id', 'title', 'remark', 'code', 'system_status'],
            check_sum_second=True,
        )
        return response

    def test_get_detail_doc_apr(self, pk=None):
        pk_url: str
        if pk is not None:
            pk_url = pk
        else:
            res = self.test_create_new_doc_apr()
            pk_url = res.data['result'].get('id', '')

        url = reverse('KMSDocumentApprovalRequestDetail', args=[pk_url])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, pk_url, None, response.status_code)
        return response

    def test_update_doc_apr(self):
        employee_id: str = str(self.employee.id)
        res = self.test_create_new_doc_apr()
        url = reverse('KMSDocumentApprovalRequestDetail', args=[res.data['result'].get('id', '')])
        detail_ = self.client.get(url, format='json')
        data_update = {
            'title': 'Test update doc approval',
            'remark': 'tài liệu này lưu hành nội bộ',
            'attached_list': [{
                'id': str(detail_.data['result'].get('attached_list')[0]['id']),
                'attachment': [str(self.attach['id'])],
                'title': 'test list cho doc approval',
                'document_type': str(self.doc_type['id']),
                'content_group': str(self.con_grp['id']),
                'security_lv': 1,
                'effective_date': '2025-05-23',
                'expired_date': '2025-12-23',
            }],
            'internal_recipient': [{
                'title': 'title recipient',
                'kind': 2,
                'employee_access': {
                    employee_id: {
                        'id': employee_id,
                        'full_name': self.employee.get_full_name(),
                        'code': str(self.employee.code)
                    }
                },
                'document_permission_list': [1, 2, 3, 4, 5, 6, 7],
                'expiration_date': '2025-06-20'
            }]
        }
        self.client.put(url, data_update, format='json')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        data_changed = self.client.get(url, format='json')
        self.assertEqual(data_changed.data['result']['title'], 'Test update doc approval')