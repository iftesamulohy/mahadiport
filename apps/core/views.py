from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("django.contrib.sitemaps.views.sitemap"))
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def handler404(request, exception):
    """Dashboard-styled 404 — 'This funnel has no conversions'."""
    return render(request, "404.html", status=404)
