from copy import deepcopy
from functools import wraps

from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect
from django.urls import reverse

from apps.shared import ResponseController
from typing import TypedDict


class RequireAuthOptionType(TypedDict, total=False):
    is_render: bool
    view_401: str


class HandleRequireAuthOption:
    interval_error = 'The view have define option that need run check self.valid() before call get validated_data.'

    default_if_empty = {
        # key : default value
        'is_render': False,
        'view_401': 'view_handler404'
    }

    def default_by_type(self, key, _type):
        if key in self.default_if_empty:
            return self.default_if_empty[key]

        # another return by type if key out of default exist
        if isinstance(_type, str):
            return ''
        elif isinstance(_type, int):
            return 0
        return None

    def __init__(self, option):
        # config type
        self.key_annotation = RequireAuthOptionType.__annotations__
        self.key_require = getattr(RequireAuthOptionType, '__required_keys__', ())
        self.key_option = getattr(RequireAuthOptionType, '__optional_keys__', ())

        # option and result
        self.is_valid = None
        self.option = option
        self.option_result = deepcopy(self.default_if_empty)

    def valid(self):
        if isinstance(self.option, dict):
            for key in self.key_annotation:
                if key not in self.option:
                    self.option_result[key] = self.default_by_type(key, self.key_annotation[key])
                else:
                    self.option_result[key] = self.option[key]
            self.is_valid = True
        else:
            self.is_valid = False
        return self.is_valid

    def validated_data(self, flag: int or None = None):
        # one time call
        if flag and isinstance(flag, int) and flag > 1:
            raise ValueError(self.interval_error)

        # match with is_valid
        match self.is_valid:
            case True:
                return self.option_result
            case False:
                raise ValueError('The option of view that is incorrect type.')
            case None:
                self.valid()
                return self.validated_data(flag=flag + 1 if flag and isinstance(flag, int) else 1)
        raise ValueError('Decorator return type error.')


def requires_auth(option: RequireAuthOptionType):
    """
    Decorator requires authenticate
    :param option: Key-Value configuration
    :return: JSON or HTML
    """

    def decorator_function(func):
        @wraps(func)
        def wrapped_function(self_cls, request, *args, **kwargs):
            parsed_option = HandleRequireAuthOption(option=option).validated_data()
            if request.user and not isinstance(request.user, AnonymousUser):
                return func(self_cls, request, *args, **kwargs)
            if request.accepted_renderer.format == 'html':
                return redirect(reverse(parsed_option['view_401']))
            return ResponseController.unauthorized_401()

        return wrapped_function

    return decorator_function
