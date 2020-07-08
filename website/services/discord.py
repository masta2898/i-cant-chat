from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from website.services import ServiceError
from website.services.discord_api import API, DiscordApiError, DiscordTokenType
from website.models import DiscordToken, DiscordUser, UsernameMessage


def get_auth_url(redirect_uri: str) -> str:
    return API.get_auth_url(redirect_uri)


def create_token(code: str, redirect_uri: str) -> DiscordToken:
    try:
        token: DiscordTokenType = API.get_access_token(code, redirect_uri)
    except DiscordApiError as e:
        raise ServiceError("Ошибка получения токена.", str(e))

    token_object, created = DiscordToken.objects.get_or_create(
        access_token=token.access_token,
        defaults={
            'token_type': token.token_type,
            'expires_in': timedelta(seconds=int(token.expires_in)),
            'refresh_token': token.refresh_token,
            'scope': token.scope,
            'redirect_uri': redirect_uri
        }
    )

    return token_object


def refresh_token(token: DiscordToken):
    """Modifies @token if everything is going ok, returns NO_ERROR"""
    # do not perform this operation if token is not expired
    if not token.is_expired:
        return

    try:
        new_token: DiscordTokenType = API.refresh_token(
            token.refresh_token,
            token.redirect_uri
        )

        token.access_token = new_token.access_token
        token.refresh_token = new_token.refresh_token
        token.expires_in = timedelta(seconds=int(new_token.expires_in))
        token.save()
    except DiscordApiError as e:
        raise ServiceError("Ошибка обновления токена.", str(e))


def unexpired_token_required(func):
    def wrapper(*args, **kwargs):
        token = args[0]

        if not (isinstance(token, DiscordToken)):
            raise ServiceError(
                "Неверный тип токена.",
                f"Попытка воспользоваться токеном с типом {type(token)}."
            )

        if token.is_expired:
            raise ServiceError(
                "Срок использования токена истек.",
                "Попытка воспользоваться токеном с истекшим сроком давности."
            )

        return func(*args, **kwargs)
    return wrapper


@unexpired_token_required
def create_user(token: DiscordToken) -> DiscordUser:
    try:
        user: DiscordUserType = API.get_user(token.access_token)
    except DiscordApiError as e:
        raise ServiceError(
            "Ошибка получения информации о владельце токена.", str(e)
        )

    try:
        user_object = User.objects.get(username=user.id)
    except User.DoesNotExist:
        user_object = User(username=user.id)
        user_object.save()
        user_object.discord_user.token = token

    # remove old token if it has been updated
    old_token = user_object.discord_user.token
    if old_token.is_expired:
        old_token.delete()
    
    user_object.discord_user.token = token
    user_object.discord_user.username = user.username
    user_object.discord_user.avatar = user.avatar
    user_object.save()

    return user_object


@unexpired_token_required
def create_username_message(token: DiscordToken, username: str) -> UsernameMessage:
    username_message = UsernameMessage(
        discord_user=token.discord_user, text=username
    )

    try:
        username_message.full_clean()
    except ValidationError as e:
        raise ServiceError(
            "Ошибка форматирования никнейма", ",".join(e)
        )

    try:
        user: DiscordUserType = API.change_username(token.access_token, username)
        username_message.save()
        return username_message
    except DiscordApiError as e:
        raise ServiceError("Ошибка изменения никнейма.", str(e))
