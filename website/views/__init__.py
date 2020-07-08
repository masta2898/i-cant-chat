from django.shortcuts import render, redirect
from django.contrib.auth import logout as default_logout

from website.selectors import get_discord_user, get_username_messages


def index(request):
    context = {}
    if request.user.is_authenticated:
        discord_user_id = request.user.username
        context["discord_user"] = get_discord_user(discord_user_id)
        context["last_messages"] = get_username_messages(discord_user_id, 5)

    return render(request, 'website/index.html', context=context)


def logout(request):
    default_logout(request)
    return redirect('website:index')


def error_403(request, exception=None, details=""):
    return render(request, 'website/error.html', status=403, context={
        'error': {
            'code': 403,
            'text': 'У вас нет прав для просмотра этой страницы.',
            'details': details
        }
    })


def error_404(request, exception=None):
    return render(request, 'website/error.html', status=404, context={
        'error': {
            'code': 404,
            'text': 'Страница не найдена.'
        }
    })


def error_500(request, exception=None, details=""):
    return render(request, 'website/error.html', status=500, context={
        'error': {
            'code': 500,
            'text': 'Внутренняя ошибка приложения.',
            'details': details
        }
    })
