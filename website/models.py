from datetime import datetime

from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class DiscordToken(models.Model):
    """Discord's user token for authentication"""
    access_token = models.CharField(max_length=128)
    token_type = models.CharField(max_length=20)
    last_time_updated = models.DateTimeField(auto_now=True)
    expires_in = models.DurationField()
    refresh_token = models.CharField(max_length=128)
    scope = models.CharField(max_length=20)
    redirect_uri = models.TextField()

    @property
    def valid_till(self):
        return self.last_time_updated + self.expires_in
    
    @property
    def is_expired(self) -> bool:
        return self.valid_till < timezone.now()

    def __str__(self) -> str:
        return f"{self.access_token} \
        ({self.last_time_updated} - {self.valid_till})"


class DiscordUser(models.Model):
    """User auth credentials to use Discord API"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="discord_user"
    )
    token = models.OneToOneField(
        DiscordToken,
        on_delete=models.CASCADE,
        related_name="discord_user",
        null=True, blank=True
    )
    username = models.CharField(max_length=32, null=True, blank=True)
    discord_user_id = models.CharField(max_length=64, null=True, blank=True)
    avatar = models.CharField(max_length=512, null=True, blank=True)

    @property
    def avatar_url(self) -> str:
        image_base_url = "https://cdn.discordapp.com/"
        avatar_url = "embed/avatars/0.png"

        if self.discord_user_id and self.avatar: 
            avatar_url = f"avatars/{self.discord_user_id}/{self.avatar}."
            avatar_url += "gif" if str(self.avatar).startswith("a_") else "png"

        return image_base_url + avatar_url

    def __str__(self) -> str:
        return str(self.username or self.user.username)


class UsernameMessage(models.Model):
    """User's name as messages"""
    discord_user = models.ForeignKey(
        DiscordUser,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    text = models.CharField(max_length=32)
    sent = models.DateTimeField(auto_now_add=True)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)

        restricted_words = {
            "everyone", "here", "discordtag", "@", "#", ":", "`"
        }

        if not (2 <= len(self.text) <= 32):
            raise ValidationError(
                "Длинна никнейма должна быть от 2х до 32х симовлов."
            )


        if any(word in str(self.text).lower() for word in restricted_words):
            raise ValidationError(
                "Никнейм не должен содержать следующие символы: '" + 
                "', '".join(restricted_words) + "'."
            )

    def __str__(self) -> str:
        return f"({self.sent}) {self.text} by {self.discord_user}"