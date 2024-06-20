from typing import Union

from drf_yasg import openapi
from rest_framework import serializers, status

from .controllers import ResponseController
from .exceptions import ConvertErrors

__all__ = [
    'get_response_schema',
    'init_response',
]


def init_response(
        resp_ser: serializers.Serializer,
        resp_status=None,
        resp_key=None,
        resp_sample=None,
) -> dict[
    Union[int, str], openapi.Response
]:
    if not resp_status:
        resp_status = status.HTTP_200_OK

    if not resp_sample:
        resp_sample = {}

    if resp_status == status.HTTP_200_OK:
        if not resp_key:
            resp_key = 'result'
        resp_sample = ResponseController.success_200(data=resp_sample, key_data=resp_key).data

    return {
        resp_status: openapi.Response(
            description='SUCCESS',
            schema=resp_ser,
            examples={
                'application/json': resp_sample
            }
        )
    }


class SubHttp400RespSerializer(serializers.Serializer):  # noqa
    field = serializers.CharField()
    msg = serializers.CharField()


class Http400RespSerializer(serializers.Serializer):  # noqa
    errors = SubHttp400RespSerializer()


class BaseSystemErrorSerializer(serializers.Serializer):  # noqa
    status = serializers.IntegerField()
    detail = serializers.CharField()


class Http401RespSerializer(serializers.Serializer):  # noqa
    errors = BaseSystemErrorSerializer()


class Http403RespSerializer(serializers.Serializer):  # noqa
    errors = BaseSystemErrorSerializer()


class Http500RespSerializer(serializers.Serializer):  # noqa
    errors = BaseSystemErrorSerializer()


def get_response_schema(
        resp_ser: serializers.Serializer,
        resp_status=None,
        resp_key=None,
        resp_sample=None,
        exclude_status: list[Union[int, str]] = None,
        kwargs: dict = None
) -> dict:
    if not exclude_status:
        exclude_status = []

    if not kwargs:
        kwargs = {}

    system_response = {}
    if 'all' not in exclude_status:
        if status.HTTP_401_UNAUTHORIZED not in exclude_status:
            system_response[status.HTTP_401_UNAUTHORIZED] = openapi.Response(
                description='Unauthorized',
                schema=Http401RespSerializer(),
                examples={
                    'application/json': ConvertErrors().convert(
                        ResponseController.unauthorized_401().data,
                        status.HTTP_401_UNAUTHORIZED
                    ),
                }
            )

        if status.HTTP_403_FORBIDDEN not in exclude_status:
            system_response[status.HTTP_403_FORBIDDEN] = openapi.Response(
                description='Forbidden',
                schema=Http403RespSerializer(),
                examples={
                    'application/json': ConvertErrors().convert(
                        ResponseController.forbidden_403().data,
                        status.HTTP_403_FORBIDDEN
                    ),
                },
            )

        if status.HTTP_500_INTERNAL_SERVER_ERROR not in exclude_status:
            system_response[status.HTTP_500_INTERNAL_SERVER_ERROR] = openapi.Response(
                description='Server Error',
                schema=Http500RespSerializer(),
                examples={
                    'application/json': ConvertErrors().convert(
                        ResponseController.internal_server_error_500().data,
                        status.HTTP_500_INTERNAL_SERVER_ERROR
                    ),
                },
            )

        if status.HTTP_400_BAD_REQUEST not in exclude_status:
            system_response[status.HTTP_400_BAD_REQUEST] = openapi.Response(
                description='Server Error',
                schema=Http400RespSerializer(),
                examples={
                    'application/json': ConvertErrors().convert(
                        {'field_a': ['This field is required']},
                        status.HTTP_400_BAD_REQUEST
                    ),
                },
            )

    return {
        **system_response,
        **init_response(
            resp_ser=resp_ser,
            resp_status=resp_status,
            resp_key=resp_key,
            resp_sample=resp_sample,
        ),
        **kwargs
    }
