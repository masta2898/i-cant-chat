from django.urls import include, path

from website import views
from website.views import api, discord, news


app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout, name='logout'),

    path('api/', include([
        path('', api.api_root, name='api'),
        
        path('username-chat/', include([
            path('', api.change_username),
        ])),
        
        path('dynamic-username/', include([
            path('', api.dynamic_username_root),
        ])),
    ])),

    path('discord/', include([
        path('user/', discord.discord_user_info, name='user'),
        
        path('auth/', include([
            path('', discord.discord_auth, name='discord_auth'),
            path('url/', discord.discord_auth_url,
                 name='discord_auth_url'),
        ])),
    ])),

    path('news/', views.news.news_root, name='news'),
]