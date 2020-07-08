from typing import Iterable
from website.models import DiscordUser, DiscordToken, UsernameMessage


def get_discord_user(discord_user_id: str) -> DiscordUser:
    try:
        return DiscordUser.objects.get(discord_user_id=discord_user_id)
    except DiscordUser.DoesNotExist:
        return None


def get_user_token(discord_user_id: str) -> DiscordToken:
    try:
        return DiscordToken.objects \
            .select_related('discord_user') \
            .get(discord_user__discord_user_id=discord_user_id)
    except DiscordUser.DoesNotExist:
        return None


def get_username_messages(discord_user_id: str, count: int) -> Iterable[UsernameMessage]:
    return UsernameMessage.objects \
        .order_by('-sent') \
        .select_related('discord_user') \
        .filter(discord_user__discord_user_id=discord_user_id)[:count]
