from modeltranslation.translator import TranslationOptions, register

from .models import (
    CaseStudy,
    CaseStudyMetric,
    CaseStudyScreenshot,
    Experience,
    ExperiencePoint,
    SkillCategory,
    StatCounter,
    Testimonial,
)

# Note: company names, skill names (technical/brand terms), and currency values
# (before_val/after_val/prefix/suffix) are deliberately NOT translated — they
# read the same in both languages.


@register(Experience)
class ExperienceTR(TranslationOptions):
    fields = ("role", "location", "summary")


@register(ExperiencePoint)
class ExperiencePointTR(TranslationOptions):
    fields = ("text",)


@register(SkillCategory)
class SkillCategoryTR(TranslationOptions):
    fields = ("name",)


@register(CaseStudy)
class CaseStudyTR(TranslationOptions):
    fields = ("title", "client_type", "challenge", "approach", "result_text")


@register(CaseStudyMetric)
class CaseStudyMetricTR(TranslationOptions):
    fields = ("label",)


@register(CaseStudyScreenshot)
class CaseStudyScreenshotTR(TranslationOptions):
    fields = ("caption",)


@register(Testimonial)
class TestimonialTR(TranslationOptions):
    fields = ("quote", "role_company")


@register(StatCounter)
class StatCounterTR(TranslationOptions):
    fields = ("label",)
