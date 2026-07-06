"""Force English as the default language on first visit.

Django's LocaleMiddleware resolves the active language in this order:
language cookie → Accept-Language header → settings.LANGUAGE_CODE. That means a
visitor whose browser prefers Bangla would see the site in Bangla before ever
touching the switcher. English is our intended default (foreign clients), so
when no explicit choice has been made yet (no language cookie), we neutralise
the Accept-Language header and let it fall back to LANGUAGE_CODE ("en").

Once the visitor picks a language via the switcher, set_language writes the
cookie — we leave that untouched, so their choice (incl. Bangla) persists.
This middleware must run BEFORE django.middleware.locale.LocaleMiddleware.
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class DefaultEnglishMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if settings.LANGUAGE_COOKIE_NAME not in request.COOKIES:
            request.META["HTTP_ACCEPT_LANGUAGE"] = "en"
