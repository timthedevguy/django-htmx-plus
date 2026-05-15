from django import template
from typing import Dict, Any


register = template.Library()

@register.filter(name="get_attr")
def get_attr(obj, attr_name):
    if not hasattr(obj, attr_name):
        return ''

    return getattr(obj, attr_name)


@register.filter(name="get_key_value")
def get_key_value(obj: Dict[str, Any], key: str):
    return obj.get(key, None)