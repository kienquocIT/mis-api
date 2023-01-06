from datetime import datetime
from typing import Literal
from rest_framework import status

from .response import cus_response
from .translations import HttpMsg, ServerMsg, AuthMsg

DISPLAY_MIXIN_EXECUTE_TIME = True


def mixin_display_execute_time(func):
    def wrapper(*args, **kwargs):
        wrapper.__doc__ = func.__doc__
        if DISPLAY_MIXIN_EXECUTE_TIME:
            start_time = datetime.now()

            func_name = str(func.__name__)[:25]
            if len(func_name) < 25:
                func_name += ((25 - len(func_name)) // 4) * " .. "
                func_name += ' ' * ((25 - len(func_name)) % 4)
            func_name = f"[{func_name}]"
            # print(func_name, 'STARTING...')
            data = func(*args, **kwargs)
            delta_time = datetime.now() - start_time
            time_tracking = (
                    "\033[93m"
                    + (str(delta_time.seconds) + "." + str(delta_time.microseconds))[:6]
                    + "\033[0m"
            )
            print(func_name, ':', time_tracking, str(kwargs)[:90])
        else:
            data = func(*args, **kwargs)
        return data

    return wrapper


class RequestController:
    """
    Support handle data from request
    """

    @staticmethod
    def check_user_org(user_org: dict) -> bool:
        """
        Check user_org have required key, value, type .
        @param user_org:
        @return:
        """
        if user_org and isinstance(user_org, dict):
            return True
        return False


class ResponseController:
    """
    Support return response: unauthorized 401, forbidden 403, not found 404, ...
    @return: HttpResponse
    """

    msg_require_employee = AuthMsg.EMPLOYEE_REQUIRE

    @classmethod
    def success_200(
            cls,
            data: list or dict,
            key_data: Literal['result', 'detail', ''] = 'result',  # return data (must be dict) if key_data == ''
    ) -> cus_response:
        if key_data == '':
            if isinstance(data, dict):
                data.update({'status': status.HTTP_200_OK})
                return cus_response(data, status=status.HTTP_200_OK)
            return cls.internal_server_error_500(ServerMsg.ERR_KEY_DATA)
        elif key_data in ['result', 'detail', ]:
            return cus_response({key_data: data, 'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return cls.internal_server_error_500(
            f'Argument result_or_detail of success_200 must be choice in "list" or "detail". '
            f'Not {key_data}'
        )

    @classmethod
    def created_201(cls, data: dict) -> cus_response:
        return cus_response({"result": data, "status": status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)

    @classmethod
    def no_content_204(cls, msg=None) -> cus_response:
        return cus_response(
            {
                "status": status.HTTP_204_NO_CONTENT,
                "detail": msg if msg else HttpMsg.DELETE_SUCCESS,
            }, status=status.HTTP_204_NO_CONTENT,
        )

    @classmethod
    def bad_request_400(cls, msg=None) -> cus_response:
        return cus_response(
            {
                "status": status.HTTP_400_BAD_REQUEST,
                "detail": msg if msg else HttpMsg.DATA_INCORRECT,
            }, status=status.HTTP_400_BAD_REQUEST, is_errors=True,
        )

    @classmethod
    def unauthorized_401(cls, msg=None) -> cus_response:
        return cus_response(
            {
                "status": status.HTTP_401_UNAUTHORIZED,
                "detail": msg if msg else HttpMsg.LOGIN_EXPIRES,
            }, status=status.HTTP_401_UNAUTHORIZED, is_errors=True,
        )

    @classmethod
    def forbidden_403(cls, msg=None) -> cus_response:
        return cus_response(
            {
                "status": status.HTTP_403_FORBIDDEN,
                "detail": msg if msg else HttpMsg.FORBIDDEN,
            }, status=status.HTTP_403_FORBIDDEN, is_errors=True,
        )

    @classmethod
    def notfound_404(cls, msg=None) -> cus_response:
        return cus_response(
            {
                "status": status.HTTP_404_NOT_FOUND,
                "detail": msg if msg else HttpMsg.NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND, is_errors=True,
        )

    @classmethod
    def internal_server_error_500(cls, msg=None):
        return cus_response(
            {
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": str(msg) if msg else str(ServerMsg.SERVER_ERR)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR, is_errors=True
        )


# class PermissionController:
#     def __init__(
#             self,
#             org_id: str or UUID,
#             company_id: str or UUID,
#             department_id: str or UUID,
#             department_ids_children: List[str or UUID],
#             user_id: str or UUID,
#             employee_id: str or UUID,
#             is_admin_company: bool = False,
#             is_admin_org: bool = False,
#             *args, **kwargs
#     ):
#         self.org_id = org_id
#         self.company_id = company_id
#         self.department_id = department_id
#         self.department_ids_children = department_ids_children
#         self.user_id = user_id
#         self.employee_id = employee_id
#         self.is_admin_company = is_admin_company
#         self.is_admin_org = is_admin_org
#
#     def get_for_list(self, perm_code_name, use_org_company_filter, use_owner_filter) -> Q:
#         # if perm_code_name:
#         #     lookup = USER_PERM_MODEL.get_lookup_view_list(
#         #         user_id=self.user_id,
#         #         perm_code_name=perm_code_name,
#         #         user_org={
#         #             'user_id': self.user_id,
#         #             'employee_id': self.employee_id,
#         #             'org_id': self.org_id,
#         #             'company_id': self.company_id,
#         #             'department_id': self.department_id,
#         #             'department_child': self.department_ids_children,
#         #         },
#         #         use_org_company_filter=use_org_company_filter,
#         #         use_owner_filter=use_owner_filter,
#         #     )
#         # else:
#         #     lookup = Q()
#         # return lookup
#         return Q()
#
#     def get_for_create(self) -> Q:
#         print(self.org_id)
#         return Q()
#
#     def check_for_create(self, perm_full_code: str, body_data: dict) -> bool:
#         # if body_data and isinstance(body_data, dict):
#         #     if len(perm_full_code.split('_')) >= 3:
#         #         state = USER_PERM_MODEL.check_view_add(
#         #             user_id=self.user_id,
#         #             perm_code_name=perm_full_code,
#         #             user_org={
#         #                 'user_id': self.user_id,
#         #                 'employee_id': self.employee_id,
#         #                 'org_id': self.org_id,
#         #                 'company_id': self.company_id,
#         #                 'department_id': self.department_id,
#         #                 'department_child': self.department_ids_children,
#         #             },
#         #             body_data=body_data,
#         #         )
#         #         return state
#         return False
#
#     def check_for_retrieve(self, perm_full_code: str, obj_doc) -> bool:
#         # if obj_doc and hasattr(obj_doc, 'id') and len(perm_full_code.split('_')) >= 3:
#         #     return USER_PERM_MODEL.check_view_detail(
#         #         user_id=self.user_id,
#         #         perm_code_name=perm_full_code,
#         #         user_org={
#         #             'user_id': self.user_id,
#         #             'employee_id': self.employee_id,
#         #             'org_id': self.org_id,
#         #             'company_id': self.company_id,
#         #             'department_id': self.department_id,
#         #             'department_child': self.department_ids_children,
#         #         },
#         #         obj=obj_doc,
#         #     )
#         return False
#
#     def check_for_update(self, perm_full_code: str, body_data: dict, obj_doc) -> bool:
#         # if obj_doc and hasattr(obj_doc, 'id') and len(perm_full_code.split('_')) >= 3:
#         #     return USER_PERM_MODEL.check_view_update(
#         #         user_id=self.user_id,
#         #         perm_code_name=perm_full_code,
#         #         user_org={
#         #             'user_id': self.user_id,
#         #             'employee_id': self.employee_id,
#         #             'org_id': self.org_id,
#         #             'company_id': self.company_id,
#         #             'department_id': self.department_id,
#         #             'department_child': self.department_ids_children,
#         #         },
#         #         obj=obj_doc,
#         #         body_data=body_data,
#         #     )
#         return False
#
#     def check_for_destroy(self, perm_full_code: str, obj_doc) -> bool:
#         # if obj_doc and hasattr(obj_doc, 'id') and len(perm_full_code.split('_')) >= 3:
#         #     return USER_PERM_MODEL.check_view_delete(
#         #         user_id=self.user_id,
#         #         perm_code_name=perm_full_code,
#         #         user_org={
#         #             'user_id': self.user_id,
#         #             'employee_id': self.employee_id,
#         #             'org_id': self.org_id,
#         #             'company_id': self.company_id,
#         #             'department_id': self.department_id,
#         #             'department_child': self.department_ids_children,
#         #         },
#         #         obj=obj_doc,
#         #     )
#         return False
