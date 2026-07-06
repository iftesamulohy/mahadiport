from django.db import models


class SingletonModel(models.Model):
    """Base for singleton config models — always pk=1, cannot be deleted."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Singletons are not deletable.
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    site_name = models.CharField(max_length=120, default="Md Mahadi Hasan")
    # Translatable text fields carry no default= — modeltranslation treats a base
    # value equal to the field default as "unset", which corrupts the default
    # language. These are always populated by the seed / admin instead.
    tagline = models.CharField(
        max_length=200,
        blank=True,
        help_text='Short one-liner, e.g. "I make ad spend accountable."',
    )
    hero_eyebrow = models.CharField(max_length=120, blank=True)
    hero_headline = models.CharField(max_length=200, blank=True)
    hero_subtext = models.TextField(blank=True)

    email = models.EmailField(default="mahadihasanshawons@gmail.com")
    phone = models.CharField(max_length=40, default="+8801328885839")
    location = models.CharField(max_length=160, blank=True)

    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(
        max_length=40,
        blank=True,
        help_text="Digits only, for wa.me link (e.g. 8801328885839)",
    )
    cv_file = models.FileField(upload_to="cv/", blank=True)

    meta_pixel_id = models.CharField(max_length=40, blank=True)
    og_image = models.ImageField(upload_to="og/", blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    @property
    def whatsapp_link(self):
        num = "".join(ch for ch in self.whatsapp_number if ch.isdigit())
        return f"https://wa.me/{num}" if num else ""
