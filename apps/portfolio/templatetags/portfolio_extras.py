from django import template

register = template.Library()


@register.filter
def times(value, arg):
    """Multiply — used for staggered reveal delays."""
    try:
        return int(value) * int(arg)
    except (TypeError, ValueError):
        return 0


@register.filter
def decimals(value):
    """Number of decimal places to display for a stat/metric value.
    Whole numbers show none; fractional values show one."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return 0
    return 0 if f == int(f) else 1
