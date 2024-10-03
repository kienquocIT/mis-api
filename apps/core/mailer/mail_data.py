__all__ = ['MailDataResolver']


APP_MAP_URL = {
    'quotation.quotation': 'quotation/detail/',
    'saleorder.saleorder': 'saleorder/detail/',
    'cashoutflow.advancepayment': 'cashoutflow/advance-payment/detail/',
    'cashoutflow.payment': 'cashoutflow/payment/detail/',
}

APP_MAP_TITLE = {
    'quotation.quotation': 'Chức năng: Báo giá',
    'saleorder.saleorder': 'Chức năng: Đơn hàng',
    'cashoutflow.advancepayment': 'Chức năng: Tạm ứng',
    'cashoutflow.payment': 'Chức năng: Thanh toán',
}

WORKFLOW_TYPE_MAP_TXT = {
    # 0: trans('You have a new task.'),
    0: 'Bạn có một phiếu chức năng mới cần xử lý.',
    # 1: trans('Your document was returned.'),
    1: 'Phiếu chức năng của bạn bị trả về.',
    # 2: trans('Your document was approved.'),
    2: 'Phiếu chức năng của bạn được chấp thuận.',
    # 3: trans('Your document was rejected.'),
    3: 'Phiếu chức năng của bạn bị từ chối.',
}


class MailDataResolver:
    @classmethod
    def welcome(cls, user_obj):
        return {
            '_user': {
                'full_name': user_obj.get_full_name(),
                'user_name': user_obj.username,
            },
        }

    @classmethod
    def otp_verify(cls, user_obj, otp):
        return {
            'full_name': user_obj.get_full_name(),
            'user_name': user_obj.username,
            '_otp': str(otp) if otp else '',
        }

    @classmethod
    def calendar(cls):
        return {}

    @classmethod
    def workflow(cls, runtime_obj, workflow_type):
        application_title = ''
        application_url = ''
        doc_id = ''
        if runtime_obj.app:
            application_title = APP_MAP_TITLE.get(runtime_obj.app_code, '')
        if runtime_obj.app_code:
            application_url = APP_MAP_URL.get(runtime_obj.app_code, '')
        if runtime_obj.doc_id:
            doc_id = str(runtime_obj.doc_id)
        return {
            '_workflow': {
                'wf_title': WORKFLOW_TYPE_MAP_TXT.get(workflow_type, ''),
                'wf_application_title': application_title,
                'wf_application_url': f'{application_url}{doc_id}',
                'wf_doc_id': str(doc_id),
                'wf_common_text': 'Đi đến chi tiết:'
            },
        }
