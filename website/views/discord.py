from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse

from website.services import ServiceError, discord
from website.selectors import get_discord_user, get_username_messages
from website.views import error_403, error_500
from website.models import DiscordToken, DiscordUser


def _get_absolute_url(request, url_name: str) -> str:
    # Discord doesn't like trailing '/' symbol.
    return request.build_absolute_uri(reverse(url_name))[:-1]


def discord_auth_url(request):
    test_redirect_uri = _get_absolute_url(request, 'website:discord_auth')
    auth_url = discord.get_auth_url(test_redirect_uri)
    return redirect(auth_url)


def discord_auth(request):
    code = request.GET.get('code', None)
    if code is None:
        return error_500(request, details="Нет кода для аутентификации.")

    try:
        redirect_uri = _get_absolute_url(request, 'website:discord_auth')
        token: DiscordToken = discord.create_token(code, redirect_uri)
        user: DiscordUser = discord.create_user(token)
        login(request, user)
        return redirect('website:index')
    except ServiceError as e:
        return error_500(request, details=str(e))


def discord_user_info(request):
    if not request.user.is_authenticated:
        return error_403(request, details="Необходимо войти с помощью Discord.")

    # request.user.username should be equal to 
    # request.user.discord_user.discord_user_id, if it is not - 
    # None will be returned
    discord_user_id = request.user.username
    return render(request, 'website/user.html', context={
        'discord_user': get_discord_user(discord_user_id),
        'last_messages': get_username_messages(discord_user_id, 5)
    })
