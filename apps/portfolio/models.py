from django.db import models


class Experience(models.Model):
    company = models.CharField(max_length=160)
    role = models.CharField(max_length=160)
    location = models.CharField(max_length=160, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(
        null=True, blank=True, help_text="Leave blank for 'Present'."
    )
    summary = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "-start_date"]

    def __str__(self):
        return f"{self.role} @ {self.company}"

    @property
    def end_label(self):
        return self.end_date.strftime("%b %Y") if self.end_date else "Present"

    @property
    def start_label(self):
        return self.start_date.strftime("%b %Y")


class ExperiencePoint(models.Model):
    experience = models.ForeignKey(
        Experience, related_name="points", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:60]


class SkillCategory(models.Model):
    name = models.CharField(max_length=80)
    # Stable, language-independent slug (used in HTMX tab URLs). Derived from the
    # English name — must NOT depend on the translated name.
    slug = models.SlugField(max_length=80, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Skill categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            self.slug = slugify(self.name_en or self.name)
        super().save(*args, **kwargs)


class Skill(models.Model):
    category = models.ForeignKey(
        SkillCategory, related_name="skills", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=120)
    proficiency = models.PositiveSmallIntegerField(
        default=80, help_text="0–100, drives the animated meter."
    )
    icon = models.CharField(
        max_length=40, blank=True, help_text="Optional emoji or inline-SVG name."
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class CaseStudy(models.Model):
    title = models.CharField(max_length=200)
    client_type = models.CharField(
        max_length=120, help_text='e.g. "F-commerce (Fashion)" — anonymized is fine.'
    )
    slug = models.SlugField(unique=True)
    challenge = models.TextField()
    approach = models.TextField()
    result_text = models.TextField()
    cover_image = models.ImageField(upload_to="cases/", blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name_plural = "Case studies"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("portfolio:case_detail", args=[self.slug])


class CaseStudyMetric(models.Model):
    DIRECTION_CHOICES = [
        ("down_good", "Lower is better"),
        ("up_good", "Higher is better"),
    ]
    case_study = models.ForeignKey(
        CaseStudy, related_name="metrics", on_delete=models.CASCADE
    )
    label = models.CharField(max_length=80)  # "Cost per lead", "ROAS", "CTR"
    before_val = models.CharField(max_length=40)  # "$6.20"
    after_val = models.CharField(max_length=40)  # "$3.40"
    direction = models.CharField(
        max_length=12, choices=DIRECTION_CHOICES, default="down_good"
    )
    numeric_before = models.FloatField(
        null=True, blank=True, help_text="For count animation start."
    )
    numeric_after = models.FloatField(
        null=True, blank=True, help_text="For count animation end."
    )
    prefix = models.CharField(
        max_length=8, blank=True, help_text="e.g. $ (before the animated number)."
    )
    suffix = models.CharField(
        max_length=8, blank=True, help_text="e.g. x or % (after the animated number)."
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.label}: {self.before_val} → {self.after_val}"


class Testimonial(models.Model):
    name = models.CharField(max_length=120)
    role_company = models.CharField(max_length=160, blank=True)
    quote = models.TextField()
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    @property
    def initials(self):
        parts = [p for p in self.name.split() if p]
        return "".join(p[0] for p in parts[:2]).upper() or "?"


class StatCounter(models.Model):
    label = models.CharField(max_length=120)  # "Ad spend managed"
    value = models.FloatField()  # 1.2
    prefix = models.CharField(max_length=8, blank=True)  # optional "$"
    suffix = models.CharField(max_length=12, blank=True)  # "M+", "+", "%"
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.value}{self.suffix} {self.label}"
