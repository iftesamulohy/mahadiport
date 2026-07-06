from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(TranslationAdmin):
    fieldsets = (
        ("Identity", {"fields": ("site_name", "tagline")}),
        ("Hero", {"fields": ("hero_eyebrow", "hero_headline", "hero_subtext")}),
        (
            "Contact",
            {
                "fields": (
                    "email",
                    "phone",
                    "location",
                    "whatsapp_number",
                    "facebook_url",
                    "linkedin_url",
                    "cv_file",
                )
            },
        ),
        (
            "SEO & Tracking",
            {"fields": ("meta_pixel_id", "meta_description", "og_image")},
        ),
    )

    def has_add_permission(self, request):
        # Singleton — only one row allowed.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
