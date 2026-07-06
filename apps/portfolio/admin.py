from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from .models import (
    CaseStudy,
    CaseStudyMetric,
    Experience,
    ExperiencePoint,
    Skill,
    SkillCategory,
    StatCounter,
    Testimonial,
)


class ExperiencePointInline(TranslationTabularInline):
    model = ExperiencePoint
    extra = 1


@admin.register(Experience)
class ExperienceAdmin(TranslationAdmin):
    list_display = ("role", "company", "start_label", "end_label", "is_current", "order")
    list_editable = ("order", "is_current")
    inlines = [ExperiencePointInline]


class SkillInline(admin.TabularInline):
    # Skill names are technical/brand terms — not translated.
    model = Skill
    extra = 1


@admin.register(SkillCategory)
class SkillCategoryAdmin(TranslationAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)
    inlines = [SkillInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "proficiency", "order")
    list_editable = ("proficiency", "order")
    list_filter = ("category",)


class CaseStudyMetricInline(TranslationTabularInline):
    model = CaseStudyMetric
    extra = 1


@admin.register(CaseStudy)
class CaseStudyAdmin(TranslationAdmin):
    list_display = ("title", "client_type", "is_featured", "order")
    list_editable = ("is_featured", "order")
    # Note: slug is set manually — prepopulated_fields can't target a translated
    # field under modeltranslation.
    inlines = [CaseStudyMetricInline]


@admin.register(Testimonial)
class TestimonialAdmin(TranslationAdmin):
    list_display = ("name", "role_company", "order")
    list_editable = ("order",)


@admin.register(StatCounter)
class StatCounterAdmin(TranslationAdmin):
    list_display = ("label", "value", "suffix", "order")
    list_editable = ("value", "suffix", "order")
