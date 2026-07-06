from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.portfolio.models import CaseStudy


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "monthly"

    def items(self):
        return ["portfolio:home"]

    def location(self, item):
        return reverse(item)


class CaseStudySitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return CaseStudy.objects.all()

    def lastmod(self, obj):
        return obj.created_at


sitemaps = {
    "static": StaticViewSitemap,
    "cases": CaseStudySitemap,
}
