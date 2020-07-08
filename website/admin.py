from django.contrib import admin
from website.models import DiscordToken, DiscordUser, UsernameMessage


class DiscordTokenAdmin(admin.ModelAdmin):
    readonly_fields = (
        'last_time_updated', 'expires_in', 'is_expired', 'valid_till'
    )


class DiscordUserAdmin(admin.ModelAdmin):
    readonly_fields = ('avatar_url',)


admin.site.register(DiscordToken, DiscordTokenAdmin)
admin.site.register(DiscordUser, DiscordUserAdmin)
admin.site.register(UsernameMessage)
