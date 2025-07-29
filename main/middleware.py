from django.utils import translation
from django.http.request import HttpRequest
from django.conf import settings

class ForceAdminLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # check admin page
        if request.path.startswith(f"/{settings.ADMIN_PANEL_URL}"):
            # set language for admin page
            translation.activate(settings.ADMIN_PANEL_LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.ADMIN_PANEL_LANGUAGE_CODE

        response = self.get_response(request)

        # Reset translation
        translation.deactivate()

        return response
