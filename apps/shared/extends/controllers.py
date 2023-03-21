from typing import Literal
from rest_framework import status

from .response import cus_response
from ..translations import HttpMsg, ServerMsg

__all__ = ['ResponseController']


class ResponseController:
    """
    Support return response: unauthorized 401, forbidden 403, not found 404, ...
    @return: HttpResponse
    """

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
        if key_data in ['result', 'detail', ]:
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
