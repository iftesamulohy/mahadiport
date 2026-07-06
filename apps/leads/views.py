from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .forms import LeadForm


@require_POST
def submit(request):
    """HTMX endpoint: validate + save a lead, return a partial to swap in place."""
    form = LeadForm(request.POST)

    # Honeypot: if a bot filled the hidden `website` field, silently pretend
    # success without saving anything.
    if form.is_spam:
        return _success_response(request)

    if form.is_valid():
        lead = form.save(commit=False)
        lead.source_path = form.cleaned_data.get("source_path", "")[:300]
        lead.save()
        _notify(lead)
        return _success_response(request)

    # Invalid — re-render the form partial with inline errors (HTMX swaps it back).
    return _form_response(request, form, status=422)


def _success_response(request):
    from django.shortcuts import render

    return render(request, "partials/lead_success.html")


def _form_response(request, form, status=200):
    from django.shortcuts import render

    return render(request, "partials/lead_form.html", {"lead_form": form}, status=status)


def _notify(lead):
    """Email Mahadi about a new lead (console backend in dev)."""
    try:
        body = render_to_string("emails/new_lead.txt", {"lead": lead})
        send_mail(
            subject=f"New lead: {lead.name} ({lead.phone})",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.LEAD_NOTIFY_EMAIL],
            fail_silently=True,
        )
    except Exception:
        # Never let a notification failure break the user's submission.
        pass
