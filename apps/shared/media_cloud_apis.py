from typing import Callable, TypedDict, Union

import requests

from requests_toolbelt import MultipartEncoder
from django.db.models import Model
from django.conf import settings
from django.http import response
from django.utils.text import slugify
from rest_framework import status

from .extends.utils import StringHandler, FORMATTING

API_URL_MEDIA_REFRESH_TOKEN = 'auth/refresh'
API_URL_LOGIN = 'auth/login'

REQUEST_TIMEOUT = 1 + 60

__all__ = [
    'APIUtil',
    'MediaForceAPI',
    'ServerMediaAPI',
    'MediaApiUrls',
]

"""share all popular class function for use together purpose"""


class RespDict(TypedDict, total=False):
    """response dictionary type"""
    state: Callable[[bool or None], bool or None]
    status: Callable[[int or None], int or None]
    result: Callable[[list or dict], list or dict]
    errors: Callable[[dict], dict]
    page_size: Callable[[int], int]
    page_count: Callable[[int], int]
    page_next: Callable[[int], int]
    page_previous: Callable[[int], int]
    all: Callable[[dict], dict]


# pylint: disable=R0902
class RespData:
    """
    Object convert response data
        state: bool : state call API
        result: dict or list : data
        errors: dict : errors server return
    """

    def __init__(
            self,
            _state=None, _result=None, _errors=None, _status=None,
            _page_size=None, _page_count=None, _page_next=None, _page_previous=None,
    ):
        """
        Properties will keep type of attribute that is always correct
        Args: attribute of Http Response
            _state: status_code | success: 200 - 200 | fail: others
            _result: .json()['result'] | 'result' is default
                     | You can custom key - confirm with API Docs
            _errors: .json()['errors'] | 'errors' is default
                     | You can custom key - confirm with API Docs
        """
        self._state = _state if _state is not None else False
        self._result = _result if _result is not None else {}
        self._errors = _errors if _errors is not None else {}
        self._status = _status if _status is not None else status.HTTP_500_INTERNAL_SERVER_ERROR
        self._page_size = _page_size if _page_size is not None else 0
        self._page_count = _page_count if _page_count is not None else 0
        self._page_next = _page_next if _page_next is not None else 0
        self._page_previous = _page_previous if _page_previous is not None else 0

    @property
    def state(self) -> bool:
        """property state"""
        if isinstance(self._state, int):
            if 200 <= self._state < 300:
                return True
            return False
        if settings.RAISE_EXCEPTION_DEBUG is False:
            return False
        raise AttributeError(
            f'[Response Data Parser][STATE] '
            f'convert process is incorrect when it return {type(self._state)}'
            f'({str(self._state)[:30]}) '
            f'instead of BOOLEAN types.'
        )

    @property
    def result(self) -> dict or list:
        """result property"""
        if isinstance(self._result, (dict, list)):
            return self._result
        if settings.RAISE_EXCEPTION_DEBUG is False:
            return {}
        raise AttributeError(
            f'[Response Data Parser][RESULT] '
            f'convert process is incorrect when it return {type(self._result)}'
            f'({str(self._result)[:30]}) '
            f'instead of LIST or DICT types.'
        )

    @property
    def errors(self) -> dict:
        """property errors"""
        if isinstance(self._errors, dict):
            return self._errors
        if settings.RAISE_EXCEPTION_DEBUG is False:
            return {}
        raise AttributeError(
            f'[Response Data Parser][ERRORS] '
            f'convert process is incorrect when it return {type(self._errors)}'
            f'({str(self._errors)[:30]}) '
            f'instead of DICT types.'
        )

    @property
    def status(self) -> int:
        """property status"""
        if isinstance(self._status, int):
            return self._status
        if settings.RAISE_EXCEPTION_DEBUG is False:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        raise AttributeError(
            f'[Response Data Parser][STATUS] '
            f'convert process is incorrect when it return {type(self._errors)}'
            f'({str(self._errors)[:30]}) '
            f'instead of INTEGER types.'
        )

    @property
    def page_size(self) -> int:
        """property page size"""
        if isinstance(self._page_size, int):
            return self._page_size
        if settings.RAISE_EXCEPTION_DEBUG is False:
            return 0
        raise AttributeError(
            f'[Response Data Parser][PAGE_SIZE] '
            f'convert process is incorrect when it return {type(self._errors)}'
            f'({str(self._errors)[:30]}) '
            f'instead of INTEGER types.'
        )

    @property
    def page_count(self) -> int:
        """property page count"""
        if isinstance(self._page_count, int):
            return self._page_count
        if settings.RAISE_EXCEPTION_DEBUG is False:
            return 0
        raise AttributeError(
            f'[Response Data Parser][PAGE_COUNT] '
            f'convert process is incorrect when it return {type(self._errors)}'
            f'({str(self._errors)[:30]}) '
            f'instead of INTEGER types.'
        )

    @property
    def page_next(self) -> int:
        """property next"""
        if isinstance(self._page_next, int):
            return self._page_next
        if settings.RAISE_EXCEPTION_DEBUG is False:
            return 0
        raise AttributeError(
            f'[Response Data Parser][PAGE_NEXT] '
            f'convert process is incorrect when it return {type(self._errors)}'
            f'({str(self._errors)[:30]}) '
            f'instead of INTEGER types.'
        )

    @property
    def page_previous(self) -> int:
        """property page prev"""
        if isinstance(self._page_previous, int):
            return self._page_previous
        if settings.RAISE_EXCEPTION_DEBUG is False:
            return 0
        raise AttributeError(
            f'[Response Data Parser][PAGE_PREVIOUS] '
            f'convert process is incorrect when it return {type(self._errors)}'
            f'({str(self._errors)[:30]}) '
            f'instead of INTEGER types.'
        )

    def get_full_data(self, func_change_data: RespDict = None) -> dict:
        """get all record API"""
        data_all = DictFillResp({}).fill_full(self)  # call fill data to dict
        allow_change_keys = data_all.keys()
        if func_change_data:
            for key, func_call in func_change_data.items():
                if key == 'all':
                    data_all = func_call(data_all)
                elif key in allow_change_keys:
                    data_all[key] = func_call(data_all[key])
        return data_all


class DictFillResp(dict):
    """fill data for response request"""

    def fill_state(self, resp: RespData):
        """get state"""
        self[settings.UI_RESP_KEY_STATE] = resp.state
        return self

    def fill_status(self, resp: RespData):
        """get status"""
        self[settings.UI_RESP_KEY_STATUS] = resp.status
        return self

    def fill_result(self, resp: RespData):
        """get result"""
        self[settings.UI_RESP_KEY_RESULT] = resp.result
        return self

    def fill_errors(self, resp: RespData):
        """get errors"""
        self[settings.UI_RESP_KEY_ERRORS] = resp.errors
        return self

    def fill_page_size(self, resp: RespData):
        """get page size"""
        self[settings.UI_RESP_KEY_PAGE_SIZE] = resp.page_size
        return self

    def fill_page_count(self, resp: RespData):
        """get page count"""
        self[settings.UI_RESP_KEY_PAGE_COUNT] = resp.page_count
        return self

    def fill_page_next(self, resp: RespData):
        """get page next"""
        self[settings.UI_RESP_KEY_PAGE_NEXT] = resp.page_next
        return self

    def fill_page_previous(self, resp: RespData):
        """get page prev"""
        self[settings.UI_RESP_KEY_PAGE_PREVIOUS] = resp.page_previous
        return self

    def fill_full(self, resp):
        """add all method"""
        self.fill_state(resp)
        self.fill_status(resp)
        self.fill_result(resp)
        self.fill_errors(resp)
        self.fill_page_count(resp)
        self.fill_page_next(resp)
        self.fill_page_previous(resp)
        return self


class APIUtil:
    """class with all method and default setup for request API calling"""

    @staticmethod
    def employee_force_update_token(employee_obj, token_data: dict):
        access_token = token_data.get('access_token', None)
        access_token_expired = token_data.get('access_token_expired', None)
        refresh_token = token_data.get('refresh_token', None)
        refresh_token_expired = token_data.get('refresh_token_expired', None)

        field_updates = []

        if access_token:
            employee_obj.media_access_token = access_token
            field_updates.append('media_access_token')
        if access_token_expired:
            employee_obj.media_access_token_expired = access_token_expired
            field_updates.append('media_access_token_expired')
        if refresh_token:
            employee_obj.media_refresh_token = refresh_token
            field_updates.append('media_refresh_token')
        if refresh_token_expired:
            employee_obj.media_refresh_token_expired = refresh_token_expired
            field_updates.append('media_refresh_token_expired')

        if field_updates:
            employee_obj.save(
                update_fields=field_updates
            )

        if access_token:
            return access_token
        return None

    key_auth = settings.API_KEY_AUTH
    prefix_token = settings.API_PREFIX_TOKEN
    key_response_data = settings.API_KEY_RESPONSE_DATA
    key_response_err = settings.API_KEY_RESPONSE_ERRORS
    key_response_status = settings.API_KEY_RESPONSE_STATUS
    key_response_page_size = settings.API_KEY_RESPONSE_PAGE_SIZE
    key_response_page_count = settings.API_KEY_RESPONSE_PAGE_COUNT
    key_response_page_next = settings.API_KEY_RESPONSE_PAGE_NEXT
    key_response_page_previous = settings.API_KEY_RESPONSE_PAGE_PREVIOUS

    def __init__(self, employee_obj: Model = None):
        self.employee_obj = employee_obj

    @classmethod
    def key_authenticated(cls, media_access_token: str) -> dict:
        """
        Return dict for update headers | Authorization header + Bearer + Access Token.
        Args:
            media_access_token:

        Returns:

        """
        return {cls.key_auth: f'{cls.prefix_token} {media_access_token}'}

    @classmethod
    def get_new_token(cls, media_refresh_token, employee_obj) -> str or None:
        """
        Call API refresh token
        Args:
            employee_obj:
            media_refresh_token: media_refresh_token in User Object

        Returns:

        """
        if media_refresh_token:
            resp_obj = ServerMediaAPI(
                url=API_URL_MEDIA_REFRESH_TOKEN,
                is_secret_api=True,
            ).post(
                data={'refresh': media_refresh_token}
            )
            if resp_obj.state and resp_obj.result and isinstance(resp_obj.result, dict):
                return cls.employee_force_update_token(employee_obj, resp_obj.result)
        return None

    @classmethod
    def get_new_token_by_login(cls, employee_obj):
        resp_obj = ServerMediaAPI(
            url=API_URL_LOGIN,
            is_secret_api=True,
        ).post(
            data={
                "username": employee_obj.media_username,
                "password": employee_obj.media_password,
            }
        )
        if resp_obj.state and resp_obj.result and isinstance(resp_obj.result, dict):
            token = resp_obj.result.get('token', {})
            if token:
                return cls.employee_force_update_token(employee_obj, token)
        return None

    @classmethod
    def media_refresh_token(cls, employee_obj: Model, return_data=False) -> Union[dict, str]:
        """
        Call get refresh token after update media_access_token to User Model
        Args:
            return_data:
            employee_obj: (User Model) : get media_refresh_token from user -> call
            -> update media_access_token -> save

        Returns: (dict) : it for update to headers before call API

        """
        media_access_token = cls.get_new_token(
            media_refresh_token=getattr(employee_obj, 'media_refresh_token', None),
            employee_obj=employee_obj,
        )
        if media_access_token:
            employee_obj.media_access_token = media_access_token
            employee_obj.save()
            if return_data:
                return media_access_token
            return {'Authorization': f'Bearer {media_access_token}'}
        re_login_token = cls.get_new_token_by_login(employee_obj=employee_obj)
        if re_login_token:
            employee_obj.media_access_token = media_access_token
            employee_obj.save()
            if return_data:
                return media_access_token
            return {'Authorization': f'Bearer {media_access_token}'}
        if return_data:
            return ''
        return {}

    @classmethod
    def get_data_from_resp(cls, resp: response) -> RespData:
        """
        Parse Http Response to RespData Object
        Args:
            resp: (HttpResponse)

        Returns: RespData Object

        """
        if resp.status_code == 500:
            resp_json = {
                cls.key_response_err: {'detail': 'Server Error'},
            }
        elif resp.status_code == 204:
            return RespData(
                _state=resp.status_code,
                _result={},
                _status=resp.status_code,
            )
        else:
            resp_json = resp.json()
        return RespData(
            _state=resp.status_code,
            _result=resp_json.get(cls.key_response_data, {}),
            _errors=resp_json.get(cls.key_response_err, {}),
            _status=resp_json.get(cls.key_response_status, resp.status_code),
            _page_size=resp_json.get(cls.key_response_status, resp.status_code),
            _page_count=resp_json.get(cls.key_response_page_count, None),
            _page_next=resp_json.get(cls.key_response_page_next, None),
            _page_previous=resp_json.get(cls.key_response_page_previous, None),
        )

    def call_get(self, safe_url: str, headers: dict) -> RespData:
        """
        Support ServerAPI call to server get data (refresh token after recall if token is expires)
        Args:
            safe_url: (string) url parsed
            headers: (dict) headers add to request

        Returns: RespData object have attribute state, result, errors
            state: (bool) True if status_code is range (200, 300) else False : Is success call
            result: (dict or list) : is Response Data from API
            errors: (dict) : is Error Data from API
        """
        resp = requests.get(url=safe_url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 401:
            if self.employee_obj:
                # refresh token
                headers_upgrade = self.media_refresh_token(employee_obj=self.employee_obj)
                if headers_upgrade:
                    headers.update(headers_upgrade)
                    resp = requests.get(url=safe_url, headers=headers, timeout=REQUEST_TIMEOUT)
        return self.get_data_from_resp(resp)

    def call_post(self, safe_url: str, headers: dict, data: dict) -> RespData:
        """
        Support ServerAPI call to server with POST method.
        (refresh token after recall if token is expires)
        Args:
            safe_url: (string) url parsed
            headers: (dict) headers add to request
            data: (dict) body data of request

        Returns: RespData object have attribute state, result, errors
            state: (bool) True if status_code is range (200, 300) else False : Is success call
            result: (dict or list) : is Response Data from API
            errors: (dict) : is Error Data from API
        """
        if headers['content-type'] == 'application/json':
            resp = requests.post(
                url=safe_url,
                headers=headers,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
        else:
            resp = requests.post(
                url=safe_url,
                headers=headers,
                data=data,
                timeout=REQUEST_TIMEOUT
            )
        if resp.status_code == 401:
            if self.employee_obj:
                # refresh token
                headers_upgrade = self.media_refresh_token(employee_obj=self.employee_obj)
                if headers_upgrade:
                    headers.update(headers_upgrade)
                    resp = requests.post(
                        url=safe_url, headers=headers, json=data,
                        timeout=REQUEST_TIMEOUT
                    )
        return self.get_data_from_resp(resp)

    def call_put(self, safe_url: str, headers: dict, data: dict) -> RespData:
        """
        Support ServerAPI call to server with PUT method.
        (refresh token after recall if token is expires)
        Args:
            safe_url: (string) url parsed
            headers: (dict) headers add to request
            data: (dict) body data of request

        Returns: RespData object have attribute state, result, errors
            state: (bool) True if status_code is range (200, 300) else False : Is success call
            result: (dict or list) : is Response Data from API
            errors: (dict) : is Error Data from API
        """
        resp = requests.put(
            url=safe_url, headers=headers, json=data,
            timeout=REQUEST_TIMEOUT
        )
        if resp.status_code == 401:
            if self.employee_obj:
                # refresh token
                headers_upgrade = self.media_refresh_token(employee_obj=self.employee_obj)
                if headers_upgrade:
                    headers.update(headers_upgrade)
                    resp = requests.put(
                        url=safe_url, headers=headers, json=data,
                        timeout=REQUEST_TIMEOUT
                    )
        return self.get_data_from_resp(resp)

    def call_delete(self, safe_url: str, headers: dict, data: dict) -> RespData:
        """
        Support ServerAPI call to server with DELETE method.
        (refresh token after recall if token is expires)
        Args:
            safe_url: (string) url parsed
            headers: (dict) headers add to request
            data: (dict) body data of request

        Returns: RespData object have attribute state, result, errors
            state: (bool) True if status_code is range (200, 300) else False : Is success call
            result: (dict or list) : is Response Data from API
            errors: (dict) : is Error Data from API
        """
        resp = requests.delete(
            url=safe_url, headers=headers, json=data,
            timeout=REQUEST_TIMEOUT
        )
        if resp.status_code == 401:
            if self.employee_obj:
                # refresh token
                headers_upgrade = self.media_refresh_token(employee_obj=self.employee_obj)
                if headers_upgrade:
                    headers.update(headers_upgrade)
                    resp = requests.delete(
                        url=safe_url, headers=headers, json=data,
                        timeout=REQUEST_TIMEOUT
                    )
        return self.get_data_from_resp(resp)


class ServerMediaAPI:
    """
    Public class and call from views/utils
    """

    def __init__(self, url, **kwargs):
        self.employee = kwargs.get('employee', None)
        if url.startswith('\\'):
            self.url = settings.MEDIA_DOMAIN + url[1:]
        else:
            self.url = settings.MEDIA_DOMAIN + url

        self.is_secret_api = kwargs.get('is_secret_api', False)

        self.content_type = kwargs.get('content_type', 'application/json')
        self.accept_language = kwargs.get('accept_language', 'vi')

    @property
    def headers(self) -> dict:
        """
        Setup headers for request
        Returns: Dict
            'content-type': 'application/json',
            ...
        """
        data = {
            'content-type': self.content_type,
            'Accept-Language': self.accept_language,
        }
        if self.employee and getattr(self.employee, 'media_access_token', None):
            data.update(APIUtil.key_authenticated(media_access_token=self.employee.media_access_token))

        if self.is_secret_api:
            data.update(
                {
                    settings.MEDIA_KEY_FLAG: 'true',
                    settings.MEDIA_KEY_SECRET_TOKEN_API: settings.MEDIA_SECRET_TOKEN_API,
                }
            )

        return data

    def get(self, data=None):
        """
        Support call request API with GET method.
        Args:
            data: (dict) : will url encode and append to real url ()

        Returns: APIUtil --> call_get()
        """
        safe_url = self.url
        if data and isinstance(data, dict):
            url_encode = [f"{key}={val}" for key, val in data.items()]
            safe_url += f'?{"&".join(url_encode)}'
        return APIUtil(employee_obj=self.employee).call_get(safe_url=safe_url, headers=self.headers)

    def post(self, data) -> RespData:
        """
        Support call request API with POST method.
        Args:
            data: (dict): body data of request

        Returns: APIUtil --> call_post()
        """
        if isinstance(data, (dict, MultipartEncoder)):
            return APIUtil(employee_obj=self.employee).call_post(
                safe_url=self.url,
                headers=self.headers,
                data=data
            )
        raise ValueError('Body data for POST request must be dictionary')

    def put(self, data) -> RespData:
        """
        Support call request API with PUT method.
        Args:
            data: (dict): body data of request

        Returns: APIUtil --> call_put()
        """
        if isinstance(data, dict):
            return APIUtil(employee_obj=self.employee).call_put(
                safe_url=self.url,
                headers=self.headers,
                data=data
            )
        raise ValueError('Body data for POST request must be dictionary')

    def delete(self, data: dict = dict) -> RespData:
        """
        Support call request API with DELETE method.
        Args:
            data: (dict): body data of request

        Returns: APIUtil --> call_delete()
        """
        return APIUtil(employee_obj=self.employee).call_delete(
            safe_url=self.url,
            headers=self.headers,
            data=data if data and isinstance(data, dict) else {}
        )


class StringUrl(str):  # pylint: disable=too-few-public-methods
    """convert str url"""

    def push_id(self, _id):
        """return url with id"""
        return f'{self}/{_id}'

    def fill_key(self, **kwargs):
        """return kwargs with format"""
        # 'abc/{a1}/{b1}/{c1}' + kwargs={"a1": "1", "b1": 2, "c1": 3}
        # Return ==> 'abc/1/2/3'
        return self.format(**kwargs)

    def fill_idx(self, *args):
        """return str with format"""
        # 'abc/{}/{}/{}' + args=[1, 2, 3]
        # Return ==> 'abc/1/2/3'
        return self.format(*args)


class MediaApiUrls:
    COMPANY_SYNC = StringUrl('sys/sync/company')
    EMPLOYEE_SYNC = StringUrl('sys/sync/employee')
    EMPLOYEE_UPLOAD_AVATAR = StringUrl('sys/f/avatar/upload')
    FILE_CHECK = StringUrl('sys/f/check')
    LINK_MEDIA = StringUrl('sys/f/link')
    UNLINK_MEDIA = StringUrl('sys/f/un-link')
    LOGIN_ACCESS_CODE = StringUrl('sys/sync/login-access-code')


class MediaForceAPI:
    @classmethod
    def parsed_company_code_to_media_tenant_code(cls, company_obj):
        return slugify(f'{settings.MEDIA_PREFIX_SITE}_{company_obj.tenant.code}_{company_obj.code}')

    @classmethod
    def parsed_employee_code_to_media_username(cls, employee_obj):
        email_arr = employee_obj.email.split("@")
        if len(email_arr) >= 2:
            person_name = email_arr[0]
        else:
            person_name = StringHandler.random_str(6)
        return slugify(
            f'{settings.MEDIA_PREFIX_SITE}_{employee_obj.company.code}_{person_name}_'
            f'{StringHandler.random_str(6)}'
        )

    @classmethod
    def call_sync_company(cls, company_obj):
        if settings.MEDIA_ENABLED is True:
            resp = ServerMediaAPI(
                url=MediaApiUrls.COMPANY_SYNC,
                is_secret_api=True,
            ).post(
                data={
                    "name": company_obj.title,
                    "code": cls.parsed_company_code_to_media_tenant_code(company_obj=company_obj),
                    "company_api": str(company_obj.id),
                }
            )
            company_obj.media_company_id = resp.result['id']
            company_obj.media_company_code = resp.result['code']
            company_obj.save(
                update_fields=['media_company_id', 'media_company_code'],
            )
            return True
        if settings.DEBUG is True:
            print('[Media] Skip sync company: ', str(company_obj))
        return False

    @classmethod
    def call_sync_employee(cls, employee_obj):
        if settings.MEDIA_ENABLED is True:
            company_obj = employee_obj.company
            username = cls.parsed_employee_code_to_media_username(employee_obj=employee_obj)
            passwd = StringHandler.random_str(32)

            resp = ServerMediaAPI(
                url=MediaApiUrls.EMPLOYEE_SYNC,
                is_secret_api=True,
            ).post(
                data={
                    "company": str(company_obj.media_company_id),
                    "username": username,
                    "password": passwd,
                }
            )
            employee_obj.media_username = username
            employee_obj.media_password = passwd
            employee_obj.media_user_id = resp.result['id']

            employee_obj.media_refresh_token = resp.result['token']['access_token']
            employee_obj.media_refresh_token_expired = FORMATTING.parse_to_datetime(
                resp.result['token']['access_token_expired']
            )

            employee_obj.media_access_token = resp.result['token']['refresh_token']
            employee_obj.media_access_token_expired = FORMATTING.parse_to_datetime(
                resp.result['token']['refresh_token_expired']
            )

            employee_obj.media_avatar_hash = resp.result['media_avatar_hash']

            employee_obj.save(
                update_fields=[
                    'media_username', 'media_password', 'media_user_id',
                    'media_refresh_token', 'media_access_token',
                    'media_avatar_hash',
                ],
            )
            return True
        if settings.DEBUG is True:
            print('[Media] Skip sync employee: ', str(employee_obj))
        return False

    @classmethod
    def call_upload_avatar(cls, employee_obj, f_img):
        if settings.MEDIA_ENABLED is True:
            m_data = MultipartEncoder(
                fields={'file': (f_img.name, f_img, f_img.content_type), 'owner': str(employee_obj.media_user_id)}
            )
            resp = ServerMediaAPI(
                url=MediaApiUrls.EMPLOYEE_UPLOAD_AVATAR,
                is_secret_api=True,
                content_type=m_data.content_type,
            ).post(data=m_data)
            return resp
        if settings.DEBUG is True:
            print('[Media] Skip upload avatar: ', str(employee_obj), str(f_img))
        return RespData(_state=False)

    @classmethod
    def get_file_check(cls, media_file_id, media_user_id) -> (bool, dict):
        # sys/f/check
        # {
        #     "media_file_id": "4a713342-a123-4a26-bcd9-f2abb659790e",
        #     "owner_id": "f21e2cda-4d6f-4142-bcb2-e3f985385c8f"
        # }
        if settings.MEDIA_ENABLED is True:
            resp = ServerMediaAPI(
                url=MediaApiUrls.FILE_CHECK,
                is_secret_api=True,
            ).post(
                data={
                    'media_file_id': media_file_id,
                    'owner_id': media_user_id,
                }
            )
            if resp.state:
                return True, resp.result
            return False, resp.errors
        if settings.DEBUG is True:
            print('[Media] Skip get file check: ', str(media_file_id), str(media_user_id))
        return False, RespData(_errors={'detail': 'Skipp get file check'}).errors

    @classmethod
    def regis_link_to_file(cls, media_file_id, api_file_id, api_app_code, media_user_id) -> (bool, dict):
        # sys/f/link
        # {
        #     "media_file_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        #     "api_file_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        #     "api_app_code": "string",
        #     "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        # }
        if settings.MEDIA_ENABLED is True:
            resp = ServerMediaAPI(
                url=MediaApiUrls.LINK_MEDIA,
                is_secret_api=True,
            ).post(
                data={
                    'media_file_id': str(media_file_id),
                    'api_file_id': str(api_file_id),
                    'api_app_code': str(api_app_code),
                    'owner_id': str(media_user_id),
                }
            )
            if resp.state:
                return True, resp.result
            return False, resp.errors
        if settings.DEBUG is True:
            print(
                '[Media] Skip regis link to file: ', str(media_file_id), str(api_file_id), str(api_app_code),
                str(media_user_id)
            )
        return False, RespData(_errors={'detail': 'Skipp regis link to file'}).errors

    @classmethod
    def destroy_link_to_file(cls, media_file_id, api_file_id, api_app_code, media_user_id) -> (bool, dict):
        # sys/f/un-link
        # {
        #     "media_file_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        #     "api_file_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        #     "api_app_code": "string",
        #     "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        # }
        if settings.MEDIA_ENABLED is True:
            resp = ServerMediaAPI(
                url=MediaApiUrls.UNLINK_MEDIA,
                is_secret_api=True,
            ).post(
                data={
                    'media_file_id': str(media_file_id),
                    'api_file_id': str(api_file_id),
                    'api_app_code': str(api_app_code),
                    'owner_id': str(media_user_id),
                }
            )
            if resp.state:
                return True, resp.result
            return False, resp.errors
        if settings.DEBUG is True:
            print(
                '[Media] Skip destroy link to file: ', str(media_file_id), str(api_file_id), str(api_app_code),
                str(media_user_id)
            )
        return False, RespData(_errors={'detail': 'Skipp destroy link to file'}).errors

    @classmethod
    def valid_access_code_login(cls, employee_media_id, company_media_id, user_agent, public_ip, access_id):
        # {
        #   "employee_media_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        #   "company_media_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        #   "user_agent": "string",
        #   "public_ip": "string",
        #   "access_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        # }
        if settings.MEDIA_ENABLED is True:
            resp = ServerMediaAPI(
                url=MediaApiUrls.LOGIN_ACCESS_CODE,
                is_secret_api=True,
            ).post(
                data={
                    'employee_media_id': str(employee_media_id),
                    'company_media_id': str(company_media_id),
                    'user_agent': str(user_agent),
                    'public_ip': str(public_ip),
                    'access_id': str(access_id),
                }
            )
            if resp.state:
                return True, resp.result
            return False, resp.errors
        if settings.DEBUG is True:
            print(
                '[Media] Skip valid access code login: ', str(employee_media_id), str(company_media_id), str(user_agent),
                str(public_ip), str(access_id)
            )
        return False, RespData(_errors={'detail': 'Skip valid access code login'}).errors
