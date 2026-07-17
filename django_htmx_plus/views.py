from django.db.models import QuerySet
from django.template.defaultfilters import capfirst
from django.views.generic import ListView
from typing import Tuple
from urllib.parse import urlencode
from typing import Dict, Any, List

from django_htmx_plus.utils import build_orm_filter_dict, build_filter_query_str, build_filters_context

# TODO: Add optoins to sepcifiy paging stops in dropdown
class HtmxListView(ListView):
    """A Django ListView with HTMX support for filtering, sorting, and pagination.

    Extends Django's ListView to provide seamless HTMX integration, including
    dynamic filtering, column-based ordering, and elided pagination with query
    string preservation.

    Attributes:
        hx_target_id (str): The HTML element ID that HTMX will target for partial updates.
        fields (Tuple[str, ...]): A tuple of model field names allowed for filtering,
            sorting, and inclusion in the queryset values. There is no wildcard/bypass —
            every field a view needs to expose must be listed explicitly. ``"pk"`` is
            always added automatically (see :meth:`get_fields`) so that rows remain
            uniquely identifiable even when not explicitly listed; templates hide the
            ``pk`` column by default unless ``show_pk`` is truthy in the context.
        enable_history (bool): Whether the ``header_cell``/``pager`` components should push
            sort/filter/page changes onto the browser history (``hx-push-url``). Defaults to
            ``False``; set to ``True`` to enable browser history integration for this view.
        hidden_fields (Tuple[str, ...]): Field names (from :meth:`get_fields`) that should
            still be included in the queryset projection and passed to the template, but
            marked ``visible: False`` so ``<c-tables.htmx_table />`` skips rendering their
            column. Defaults to ``()``.

    To post-process rows before they reach the template (e.g. annotate or reshape
    values), override :meth:`get_transform_data` rather than :meth:`get_context_data`.
    """

    hx_target_id: str = ""
    fields: Tuple[str, ...] = ()
    labels: Dict = {}
    enable_history: bool = False
    order_by: str | None = None
    hidden_fields: Tuple[str, ...] = ()

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
        self.default_paginate_by: int = 10

    def setup(self, request, *args, **kwargs):
        """Initialize view attributes from the incoming request.

        Parses query parameters to build filter dictionaries, query strings, and
        the active ordering field. If ``order_by`` isn't present in the query string,
        or names a field not in the allowlist, ``self.order_by`` is left unchanged
        (its class-level default, or ``None`` if unset) — there is no automatic
        fallback to ``"pk"``.

        If ``paginate_by`` is present in the query string, it overrides ``self.paginate_by``
        for this request (parsed with a plain ``int()`` — no clamping to a min/max or to
        the ``<c-tables.htmx_table />`` selector's preset options).

        Args:
            request: The incoming HTTP request object.
            *args: Additional positional arguments passed to the parent ``setup``.
            **kwargs: Additional keyword arguments passed to the parent ``setup``.
        """
        super(HtmxListView, self).setup(request, *args, **kwargs)
        self.filter = self.get_filters()
        self.query = build_filter_query_str(request.GET)
        self.filter_query = self.query
        self.order_by = getattr(self, "order_by", None)
        self.default_paginate_by = self.paginate_by

        if "paginate_by" in self.request.GET and self.paginate_by > 0:
            try:
                self.paginate_by = int(self.request.GET["paginate_by"])
            except ValueError:
                self.paginate_by = self.default_paginate_by

        if "order_by" in request.GET:
            candidate = request.GET.get('order_by')
            if self._is_order_by_allowed(candidate):
                self.order_by = candidate
                self.query += f"&order_by={self.order_by}"

    def get_fields(self):
        """Return the allowed field list, guaranteeing ``"pk"`` is always included.

        Mutates and returns ``self.fields``, prepending ``"pk"`` when it is
        missing so that filtering, ordering, and the queryset's ``.values()``
        projection always have access to a unique row identifier, even for
        views that don't explicitly list ``"pk"`` in their ``fields``.

        Returns:
            Tuple[str, ...]: The (possibly amended) allowed field names.
        """
        if "pk" not in self.fields:
            self.fields = ("pk",) + self.fields

        return self.fields

    def get_hidden_fields(self):
        """Return the field names that should be hidden from ``<c-tables.htmx_table />``.

        Returns:
            Tuple[str, ...]: Field names still included in the queryset and context,
            but marked ``visible: False`` for the table template.
        """
        return self.hidden_fields

    def get_filters(self):
        return build_orm_filter_dict(self.request.GET, self.get_fields())

    def get_query(self):
        return self.query

    def get_order_by(self):
        return self.order_by

    def get_hx_target_id(self):
        return self.hx_target_id

    def get_filter_query(self):
        return self.filter_query

    def get_labels(self):
        return self.labels

    def get_filters_data(self):
        return build_filters_context(self.get_filters())

    def get_queryset(self):
        """Return the filtered and ordered queryset for the view.

        Applies any active filters from ``self.filter`` to the base queryset and
        orders the result by ``self.order_by``. The queryset is always returned as
        a ``ValuesQuerySet`` restricted to :meth:`get_fields` (always including
        ``"pk"``), ensuring that columns not listed in ``fields`` are never
        fetched from the database.

        If you override this method to provide a custom or dynamic queryset (e.g.
        a different manager, joins, per-user filtering, annotations), you should
        either apply ``self.filter`` and ``self.order_by`` to it yourself, or call
        ``return self.queryset_values(queryset)`` at the end of your override to
        apply them automatically.

        Returns:
            QuerySet: A filtered and ordered ``ValuesQuerySet`` limited to
            :meth:`get_fields`.
        """
        qs = self.queryset
        if not qs and self.model:
            qs = self.model.objects.all()
        return self.queryset_values(qs)


    def queryset_values(self, qs: QuerySet) -> QuerySet | None:
        """Apply the htmx-plus filter/order_by/values pipeline to a queryset.

        Applies any active filters from ``self.filter``, orders by ``self.order_by``,
        and restricts the projection to :meth:`get_fields` (always including
        ``"pk"``). Call this from an overridden :meth:`get_queryset` after
        constructing a custom base queryset, to opt into the same automatic
        filter/order_by/values behavior as the default implementation.

        Args:
            qs (QuerySet): The queryset to filter, order, and project.

        Returns:
            QuerySet: A filtered and ordered ``ValuesQuerySet`` limited to
            :meth:`get_fields`.
        """
        if self.filter:
            qs = qs.filter(**self.filter)
        if self.order_by:
            pk_order = "pk"
            if self.order_by.startswith("-"):
                pk_order = "-pk"

            qs = qs.order_by(self.order_by, pk_order)
        return qs.values(*self.get_fields())


    def _is_order_by_allowed(self, order_by: str) -> bool:
        """Check whether a user-supplied ordering field is permitted.

        The field name is extracted by stripping a leading ``-`` (descending
        indicator). The field is then checked against ``self.fields``, so callers
        cannot bypass the allowlist via related-model traversal (e.g. ``allowed_field__secret``).

        Args:
            order_by (str): The raw ``order_by`` value from the query string,
                optionally prefixed with ``-`` for descending order.

        Returns:
            bool: ``True`` if the field is in the allowlist, ``False`` otherwise.
        """
        field = order_by.lstrip('-')
        return field in self.get_fields()

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
            - ``hx_target_id`` (str): The HTMX target element ID.
            - ``query`` (str): Full query string including the ``order_by`` parameter.
            - ``filter_query`` (str): Query string containing only filter parameters.
            - ``filters`` (dict): Template-ready representation of active filters.
            - ``fields`` (list): One ``{"name", "label", "visible"}`` dict per field
              from :meth:`get_fields` (always including ``"pk"``). ``label`` is the
              entry from :meth:`get_labels` if present and truthy, otherwise the field
              name run through :func:`~django.template.defaultfilters.capfirst`.
              ``visible`` is ``False`` for any field returned by :meth:`get_hidden_fields`.
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

        context["order_by"] = self.get_order_by()
        context["path"] = self.request.path
        context["hx_target_id"] = self.get_hx_target_id()
        context["query"] = self.get_query()
        context["filter_query"] = self.get_filter_query()
        context["filters"] = self.get_filters_data()
        context["enable_history"] = self.enable_history
        context["default_paginate_by"] = self.default_paginate_by

        labels = self.get_labels()

        context["fields"] = []
        hidden_fields = self.get_hidden_fields()
        for field in fields:
            field_def = {
                "name": field,
                "label": labels.get(field) or capfirst(field),
                "visible": True
            }

            if field in hidden_fields:
                field_def["visible"] = False

            context["fields"].append(field_def)

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
