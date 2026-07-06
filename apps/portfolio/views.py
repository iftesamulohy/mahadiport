from django.http import Http404
from django.shortcuts import get_object_or_404, render

from apps.leads.forms import LeadForm

from .models import CaseStudy, Experience, SkillCategory, StatCounter, Testimonial


def _homepage_context():
    return {
        "stats": StatCounter.objects.all(),
        "case_studies": CaseStudy.objects.prefetch_related("metrics").all(),
        "skill_categories": SkillCategory.objects.prefetch_related("skills").all(),
        "experiences": Experience.objects.prefetch_related("points").all(),
        "testimonials": Testimonial.objects.all(),
        "lead_form": LeadForm(),
    }


def home(request):
    """Homepage. If ?case=<slug> is present, the drawer pre-opens (deep-link)."""
    context = _homepage_context()
    context["open_case"] = request.GET.get("case", "")
    return render(request, "home.html", context)


def case_detail(request, slug):
    """Deep-linkable full page for a case study — renders home with drawer open."""
    case = get_object_or_404(CaseStudy, slug=slug)
    context = _homepage_context()
    context["open_case"] = case.slug
    return render(request, "home.html", context)


def case_panel(request, slug):
    """HTMX fragment: the case study detail panel loaded into the drawer."""
    case = get_object_or_404(
        CaseStudy.objects.prefetch_related("metrics"), slug=slug
    )
    return render(request, "partials/case_panel.html", {"case": case})


def skills_tab(request, slug):
    """HTMX fragment: the animated skills list for one category tab."""
    category = next(
        (
            c
            for c in SkillCategory.objects.prefetch_related("skills").all()
            if c.slug == slug
        ),
        None,
    )
    if category is None:
        raise Http404("Skill category not found")
    return render(request, "partials/skills_panel.html", {"category": category})
