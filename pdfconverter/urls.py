from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # * defaul = "admin/"
    path(settings.ADMIN_PANEL_URL, admin.site.urls),
    # for apps
    path("", include("main.urls")),
    path("", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
