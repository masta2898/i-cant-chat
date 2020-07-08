from django.contrib import admin
from django.urls import include, path

from .settings import DEBUG

admin_url = 'admin/' if DEBUG else "vhod/tolko/dlya/geev/ah/ty/pidoras/suka/TRUMP/VECHEN/"

urlpatterns = [
    path('', include('website.urls')),
    path(admin_url, admin.site.urls),
]

handler403 = 'website.views.error_403'
handler404 = 'website.views.error_404'
handler500 = 'website.views.error_500'