from modeltranslation.translator import TranslationOptions, register

from .models import SiteSettings


@register(SiteSettings)
class SiteSettingsTR(TranslationOptions):
    fields = (
        "tagline",
        "hero_eyebrow",
        "hero_headline",
        "hero_subtext",
        "meta_description",
        "location",
    )
