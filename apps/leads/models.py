from django.db import models


class Lead(models.Model):
    # Monthly Meta ad budget in USD (budgets are managed in dollars).
    BUDGET_CHOICES = [
        ("<200", "Under $200"),
        ("200-1000", "$200–$1,000"),
        ("1000+", "$1,000+"),
        ("na", "Not sure yet"),
    ]

    name = models.CharField(max_length=160)
    # Phone is primary in the BD context — required; email optional.
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    business = models.CharField(
        max_length=200, blank=True, help_text="What do you sell?"
    )
    monthly_budget = models.CharField(
        max_length=12, blank=True, choices=BUDGET_CHOICES
    )
    message = models.TextField(blank=True)
    source_path = models.CharField(
        max_length=300, blank=True, help_text="Which page/section the lead came from."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.phone}"
