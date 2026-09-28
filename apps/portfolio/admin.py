from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from .models import (
    CaseStudy,
    CaseStudyMetric,
    CaseStudyScreenshot,
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


class CaseStudyScreenshotInline(TranslationTabularInline):
    model = CaseStudyScreenshot
    extra = 1
    fields = ("preview", "image", "kind", "caption", "order")
    readonly_fields = ("preview",)

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.image:
            return "—"
        return format_html(
            '<a href="{0}" target="_blank" rel="noopener">'
            '<img src="{0}" alt="" style="height:64px;max-width:120px;'
            'object-fit:cover;border-radius:6px;border:1px solid #ddd"></a>',
            obj.image.url,
        )


@admin.register(CaseStudy)
class CaseStudyAdmin(TranslationAdmin):
    list_display = ("title", "client_type", "screenshot_count", "is_featured", "order")
    list_editable = ("is_featured", "order")
    # Note: slug is set manually — prepopulated_fields can't target a translated
    # field under modeltranslation.
    inlines = [CaseStudyMetricInline, CaseStudyScreenshotInline]

    @admin.display(description="Screenshots")
    def screenshot_count(self, obj):
        return obj.screenshots.count()


@admin.register(Testimonial)
class TestimonialAdmin(TranslationAdmin):
    list_display = ("name", "role_company", "order")
    list_editable = ("order",)


@admin.register(StatCounter)
class StatCounterAdmin(TranslationAdmin):
    list_display = ("label", "value", "suffix", "order")
    list_editable = ("value", "suffix", "order")
