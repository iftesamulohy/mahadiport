"""URL configuration for the Mahadi portfolio project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django_bangla_admin.sites import urls as admin_urls

from apps.core import views as core_views
from apps.core.sitemaps import sitemaps

urlpatterns = [
    # Themed admin (django-bangla-admin); mirrors every @admin.register model.
    path("admin/", admin_urls),
    path("i18n/", include("django.conf.urls.i18n")),  # set_language endpoint
    path("leads/", include("apps.leads.urls")),
    path("robots.txt", core_views.robots_txt, name="robots"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", include("apps.portfolio.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (dashboard-styled 404 — see §12 Phase 6).
handler404 = "apps.core.views.handler404"
