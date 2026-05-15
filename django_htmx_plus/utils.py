import ast
from typing import List, Dict, Any, Tuple

from django_htmx_plus.types import Filter


def build_filter_dict(query_params: Dict[str, Any], allowed_fields: Tuple[str, ...] | None) -> dict:
    """Build a filter dictionary from query parameters, restricted to allowed fields.

    Parses query parameters of the form ``field_name.filter_type=value`` and
    converts them into a Django ORM-compatible filter dict. Only fields present
    in ``allowed_fields`` are processed; unknown filter suffixes are silently
    dropped rather than forwarded to the ORM.

    The ``field_name`` portion is the *root* field name only — traversal via
    ``__`` within the field name segment is not permitted. This prevents callers
    from bypassing the allowlist via related-model lookups (e.g.
    ``related__secret.eq=value``).

    Args:
        query_params (dict): A dictionary of raw query parameters, typically
            ``request.GET``.
        allowed_fields (Tuple[str, ...] | None): A tuple of permitted field names.
            Pass ``("__all__",)`` or an empty tuple/``None`` to allow all fields.

    Returns:
        dict: A dictionary suitable for passing directly to ``QuerySet.filter()``.
    """
    filter_dict = {}
    unrestricted = not allowed_fields or "__all__" in allowed_fields
    for key, value in query_params.items():
        if "." in key:
            field_name, filter_type = key.split(".", 1)
            # Block traversal: field_name must be a plain field, not a __ path
            if "__" in field_name:
                continue
            if unrestricted or field_name in allowed_fields:
                if filter_type.upper() in Filter.__members__:
                    filter_value = Filter.__members__[filter_type.upper()].value
                    if isinstance(value, str):
                        try:
                            filter_dict[f"{field_name}__{filter_value}"] = ast.literal_eval(value)
                        except ValueError:
                            filter_dict[f"{field_name}__{filter_value}"] = value
                    else:
                        filter_dict[f"{field_name}__{filter_value}"] = value
                # Unknown filter suffixes are silently ignored instead of being
                # forwarded to the ORM with an invalid key.
    return filter_dict


def build_query_str(query_params: dict) -> str:
    """Build a URL query string from filter-style query parameters.

    Iterates over ``query_params`` and includes only entries whose key contains
    a ``.`` (i.e. ``field_name.filter_type`` pairs). The ``order_by`` and other
    plain parameters are intentionally excluded.

    Args:
        query_params (dict): A dictionary of raw query parameters, typically
            ``request.GET``.

    Returns:
        str: An ampersand-joined query string of the form
            ``field.filter=value&field2.filter=value2``, or an empty string if
            no matching parameters are present.
    """
    items = []
    for key, value in query_params.items():
        if "." in key:
            items.append(f"{key}={value}")
    return "&".join(items)

def build_filters_template_dict(filter: dict) -> dict:
    """Convert an ORM filter dict into a template-friendly mapping.

    Strips the Django ORM lookup suffix (everything from the first ``__``
    onward) from each key so that templates receive plain field names as keys.
    For example, ``{"name__icontains": "Alice"}`` becomes ``{"name": "Alice"}``.

    Args:
        filter (dict): A dictionary of ORM filter expressions as returned by
            :func:`build_filter_dict`.

    Returns:
        dict: A dictionary mapping plain field names to their filter values.
    """
    results = {}
    for key, value in filter.items():
        results[key.split("__")[0]] = value
    return results

def split_and_strip(content: str) -> List[str]:
    """Split and normalise a multi-line string into a list of non-empty lines.

    Strips leading/trailing spaces from each line, normalises Windows-style
    line endings (``\\r\\n``) to Unix-style (``\\n``), removes non-breaking
    space characters (``\\xa0`` and ``\\xc2``), and discards any lines that are
    empty after stripping.

    Args:
        content (str): The raw multi-line string to process.

    Returns:
        List[str]: A list of cleaned, non-empty lines from ``content``.
    """
    lines = [
        line.strip(" ").replace("\xa0", "").replace("\xc2", "")
        for line in content.strip(" ").replace("\r\n", "\n").split("\n")
    ]
    return [line for line in lines if line]