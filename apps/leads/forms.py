from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Lead


class LeadForm(forms.ModelForm):
    # Honeypot — real users never see or fill this. Bots do.
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    # Captured from the page for context (which section/page the lead came from).
    source_path = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Lead
        fields = ["name", "phone", "email", "business", "monthly_budget", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": _("Your name"), "autocomplete": "name"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "01XXXXXXXXX",
                    "inputmode": "tel",
                    "autocomplete": "tel",
                }
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": _("you@example.com (optional)")}
            ),
            "business": forms.TextInput(
                attrs={"placeholder": _("e.g. fashion page, restaurant, service…")}
            ),
            "message": forms.Textarea(
                attrs={"rows": 3, "placeholder": _("Anything you want me to know?")}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = True
        self.fields["email"].required = False
        self.fields["monthly_budget"].required = False
        self.fields["monthly_budget"].label = "Monthly ad budget"
        self.fields["business"].label = "What do you sell?"
        # A blank first choice for the budget select.
        self.fields["monthly_budget"].choices = [
            ("", _("Select a range…"))
        ] + list(Lead.BUDGET_CHOICES)

    @property
    def is_spam(self):
        """True if the honeypot was filled."""
        return bool(self.data.get("website"))
