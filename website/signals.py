from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from website.models import DiscordUser


@receiver(post_save, sender=User)
def create_discord_user(sender, instance, created, **kwargs):
    if created:
        discord_user = DiscordUser.objects.create(
            user=instance,
            discord_user_id=instance.username
        )
        discord_user.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.discord_user.save()