from django.db.models import QuerySet
from django.views.generic import ListView
from typing import Tuple
from urllib.parse import urlencode
from typing import Dict, Any, List

from django_htmx_plus.utils import build_filter_dict, build_query_str, build_filters_template_dict


class HtmxListView(ListView):
    """A Django ListView with HTMX support for filtering, sorting, and pagination.

    Extends Django's ListView to provide seamless HTMX integration, including
    dynamic filtering, column-based ordering, and elided pagination with query
    string preservation.

    Attributes:
        target_id (str): The HTML element ID that HTMX will target for partial updates.
        fields (Tuple[str, ...]): A tuple of model field names to include in the queryset
            values. Use ``("__all__",)`` or leave empty to return full model instances.
            ``"pk"`` is always added automatically (see :meth:`get_fields`) so that rows
            remain uniquely identifiable even when not explicitly listed; templates hide
            the ``pk`` column by default unless ``show_pk`` is truthy in the context.
        enable_history (bool): Whether the ``header_cell``/``pager`` components should push
            sort/filter/page changes onto the browser history (``hx-push-url``). Defaults to
            ``False``; set to ``True`` to enable browser history integration for this view.

    To post-process rows before they reach the template (e.g. annotate or reshape
    values), override :meth:`get_transform_data` rather than :meth:`get_context_data`.
    """

    target_id = ""
    fields: Tuple[str, ...] = ()
    labels: {}
    enable_history: bool = False

    def __init__(self):
        """Initialise instance-level defaults for filter, query, and ordering state.

        Sets safe default values so that attributes are always defined, even if
        :meth:`setup` has not yet been called (e.g. during class introspection or
        testing). All values are overwritten by :meth:`setup` on every real request.
        """
        super().__init__()
        self.filter = {}
        self.query = ""
        self.filter_query = ""
        self.order_by = "pk"

    def setup(self, request, *args, **kwargs):
        """Initialize view attributes from the incoming request.

        Parses query parameters to build filter dictionaries, query strings, and
        the active ordering field. Falls back to ``"pk"`` if no ordering is specified.

        Args:
            request: The incoming HTTP request object.
            *args: Additional positional arguments passed to the parent ``setup``.
            **kwargs: Additional keyword arguments passed to the parent ``setup``.
        """
        super(HtmxListView, self).setup(request, *args, **kwargs)
        self.filter = build_filter_dict(request.GET, self.fields)
        self.query = build_query_str(request.GET)
        self.filter_query = self.query
        self.order_by = getattr(self, "order_by", None)

        if "order_by" in request.GET:
            candidate = request.GET.get('order_by')
            if self._is_order_by_allowed(candidate):
                self.order_by = candidate

        if not self.order_by:
            self.order_by = "pk"

        self.query += f"&order_by={self.order_by}"

    def get_fields(self):
        """Return the allowed field list, guaranteeing ``"pk"`` is always included.

        Mutates and returns ``self.fields``, prepending ``"pk"`` when it is
        missing so that filtering, ordering, and the queryset's ``.values()``
        projection always have access to a unique row identifier, even for
        views that don't explicitly list ``"pk"`` in their ``fields``. Has no
        effect when ``fields`` is ``"__all__"``, since no projection or
        allowlist restriction applies in that case.

        Returns:
            Tuple[str, ...]: The (possibly amended) allowed field names.
        """
        if self.fields != "__all__" and "pk" not in self.fields:
            self.fields = ("pk",) + self.fields

        return self.fields

    def get_queryset(self):
        """Return the filtered and ordered queryset for the view.

        Applies any active filters from ``self.filter`` to the base queryset and
        orders the result by ``self.order_by``. When :meth:`get_fields` returns a
        non-empty tuple that does not contain ``"__all__"``, the queryset is
        returned as a ``ValuesQuerySet`` restricted to those fields (always
        including ``"pk"``), ensuring that columns not listed in ``fields`` are
        never fetched from the database.

        Returns:
            QuerySet: A filtered and ordered queryset, or a ``ValuesQuerySet``
            limited to ``self.fields`` when an explicit field list is provided.
        """
        qs = super(HtmxListView, self).get_queryset()

        if hasattr(self, 'filter') and self.filter:
            qs = qs.filter(**self.filter)
        if hasattr(self, 'order_by') and self.order_by:
            qs = qs.order_by(self.order_by)

        fields = self.get_fields()

        if not fields or "__all__" in fields:
            return qs

        return qs.values(*fields)

    def _is_order_by_allowed(self, order_by: str) -> bool:
        """Check whether a user-supplied ordering field is permitted.

        The field name is extracted by stripping a leading ``-`` (descending
        indicator). The field is then checked against ``self.fields``, so callers
        cannot bypass the allowlist via related-model traversal (e.g. ``allowed_field__secret``).

        Args:
            order_by (str): The raw ``order_by`` value from the query string,
                optionally prefixed with ``-`` for descending order.

        Returns:
            bool: ``True`` if the field is permitted or no allowlist is active,
                ``False`` otherwise.
        """
        fields = self.get_fields()

        if not fields:
            return False

        if fields and "__all__" in fields:
            return True

        field = order_by.lstrip('-')
        return field in fields

    def get_context_data(self, **kwargs):
        """Build and return the template context dictionary.

        Adds HTMX- and pagination-related context variables, including the current
        query string (without the ``page`` parameter), elided page range, ordering
        state, request path, and active filters.

        Args:
            **kwargs: Additional keyword arguments forwarded to the parent
                ``get_context_data``.

        Returns:
            dict: The context dictionary containing the following extra keys:

            - ``object_list`` (list): The page's rows, passed through
              :meth:`get_transform_data` for any subclass post-processing.
            - ``query_params`` (str): URL-encoded query string excluding ``page``.
            - ``page_range`` (iterator): Elided page range (only present when
              ``paginate_by`` is set).
            - ``order_by`` (str): The currently active ordering field.
            - ``path`` (str): The current request path.
            - ``target_id`` (str): The HTMX target element ID.
            - ``query`` (str): Full query string including the ``order_by`` parameter.
            - ``filter_query`` (str): Query string containing only filter parameters.
            - ``filters`` (dict): Template-ready representation of active filters.
            - ``fields`` (dict): ``keys`` (from :meth:`get_fields`, always including
              ``"pk"``) and ``labels``.
            - ``enable_history`` (bool): Whether sort/filter/page links should push
              browser history entries (``hx-push-url``).
        """
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.get_transform_data(context['object_list'])

        fields = self.get_fields()

        query_params = {p: v for p, v in self.request.GET.items() if p != 'page'}
        context["query_params"] = urlencode(query_params, doseq=True)

        if hasattr(self, 'paginate_by') and self.paginate_by:
            if not hasattr(self, 'elided_each_side'):
                self.elided_each_side = 1

            if not hasattr(self, 'elided_ends'):
                self.elided_ends = 1

            context["page_range"] = context["paginator"].get_elided_page_range(
                number=context["page_obj"].number, on_each_side=self.elided_each_side, on_ends=self.elided_ends
            )
            context["paginator"].allow_empty_first_page = True

        context["order_by"] = self.order_by
        context["path"] = self.request.path
        context["target_id"] = self.target_id
        context["query"] = self.query
        context["filter_query"] = self.filter_query
        context["filters"] = build_filters_template_dict(self.filter)
        context["enable_history"] = self.enable_history

        fields = {
            "keys": fields,
            "labels": self.labels,
        }
        context["fields"] = fields

        return context

    def get_transform_data(self, objects: QuerySet) -> List[Dict[str, Any]]:
        """Post-process the page's rows before they are added to the context.

        Called by :meth:`get_context_data` with the paginated ``object_list``.
        The default implementation just materialises the queryset into a list;
        override this in a subclass to annotate, reshape, or otherwise transform
        each row (e.g. adding computed display fields) without having to
        re-implement pagination or filtering.

        Args:
            objects (QuerySet): The current page's queryset (or values queryset).

        Returns:
            List[Dict[str, Any]]: The rows to render, in the order they should
            appear in the table.
        """
        return list(objects)
