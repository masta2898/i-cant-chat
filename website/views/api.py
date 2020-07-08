from typing import Dict
from datetime import datetime
from collections import namedtuple

from django.http import JsonResponse
from django.utils.dateformat import format

from i_cant_chat.settings import DATETIME_FORMAT

from website.selectors import get_user_token
from website.services import ServiceError, discord
from website.models import DiscordToken, UsernameMessage


ApiResponse = namedtuple('ApiResponse', ['status', 'type', 'text'])


class ApiMethod:
    NOT_IMPLEMENTED_WARN = ApiResponse(
        status='warning',
        type='Not implemented',
        text='This function has not been implemented yet.'
    )

    NOT_AUTH_ERROR = ApiResponse(
        status='error',
        type='Not Authentiacted',
        text='You are not authenticated.'
    )

    WRONG_METHOD_ERROR = ApiResponse(
        status='error',
        type='Wrong method type',
        text='You should use POST method only.'
    )

    WRONG_ARGS_PASSED_ERROR = ApiResponse(
        status='error',
        type='Wrong arguments.',
        text='Wrong arguments passed to the API method.'
    )

    EMPTY_RESPONSE_ERROR = ApiResponse(
        status='error',
        type='Empty API response.',
        text='Got empty response from the API method.'
    )

    def __init__(self, method_args: set=set(), implemented: bool=True):
        self._method_args = method_args
        self._implemented = implemented

    @staticmethod
    def get_date():
        return format(datetime.now(), DATETIME_FORMAT)

    @staticmethod
    def api_response(func):
        def wrapper(*args, **kwargs):
            result:ApiResponse = func(*args, **kwargs)
            dict_result = result._asdict()
            dict_result["date"] = ApiMethod.get_date()
            return JsonResponse(dict_result)
        return wrapper

    def __call__(self, func):
        @ApiMethod.api_response
        def wrapper(*args, **kwargs) -> ApiResponse:
            request = args[0] # must be request
            if not self._implemented:
                return self.NOT_IMPLEMENTED_WARN

            if not request.user.is_authenticated:
                return self.NOT_AUTH_ERROR
            
            if request.method != "POST":
                return self.WRONG_METHOD_ERROR

            if not all(arg in request.POST.keys() for arg in self._method_args):
                return self.WRONG_ARGS_PASSED_ERROR

            for method_arg in self._method_args:
                kwargs[method_arg] = request.POST[method_arg]

            try:
                return func(*args, **kwargs) or self.EMPTY_RESPONSE_ERROR
            except ServiceError as e:
                return ApiResponse(status="error", type=e.text, text=e.details)
        return wrapper


@ApiMethod(implemented=False)
def api_root(request):
    pass


@ApiMethod({"username"})
def change_username(request, username=""):
    discord_user_id = request.user.username
    token: DiscordToken = get_user_token(discord_user_id)

    if token is None:
        return ApiResponse(
            status="error",
            type="Ошибка получения токена.",
            text=f"Токен пользователя {discord_user_id} не найден в базе."
        )

    if token.is_expired:
        discord.refresh_token(token)
    
    username_message: UsernameMessage = discord.create_username_message(
        token, username
    )

    return ApiResponse(
        status="success",
        type="Никнейм успешно изменен.",
        text=username_message.text
    )


@ApiMethod(implemented=False)
def dynamic_username_root(request):
    pass
