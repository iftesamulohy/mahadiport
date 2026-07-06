from .models import SiteSettings


def site_settings(request):
    """Expose the singleton SiteSettings to every template as `site`."""
    return {"site": SiteSettings.get_solo()}
