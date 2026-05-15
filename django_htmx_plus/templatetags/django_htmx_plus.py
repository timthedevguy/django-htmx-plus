from django.utils.safestring import SafeString
from django.utils.html import format_html
from django.templatetags.static import static
from django.template import Library, Context

register = Library()


@register.simple_tag(takes_context=True)
def htmx_plus_script(context: Context) -> str:
    parts = [
        static("django_htmx_plus/django-htmx-plus.js"),
        (context.get("nonce", None) or "")
    ]

    return format_html('<script src="{}" type="module"{}></script>', *parts)