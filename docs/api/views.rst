=====
Views
=====

The ``django_htmx_plus.views`` module provides enhanced list views with HTMX support.

HtmxListView
============

.. code-block:: python

    from django_htmx_plus.views import HtmxListView
    from myapp.models import Article

    class ArticleListView(HtmxListView):
        model = Article
        template_name = "articles/list.html"
        paginate_by = 10

A drop-in replacement for Django's ``ListView`` with built-in URL-based filtering, column sorting, and elided pagination.

Attributes
~~~~~~~~~~

.. attribute:: fields
    :type: Tuple[str, ...]

    The fields that are allowed for filtering and sorting. There is no wildcard/bypass
    value — every field a view needs to expose must be listed explicitly.

    ``"pk"`` is always added automatically if it isn't already present, so rows remain
    uniquely identifiable even if you don't list it explicitly. The
    ``<c-tables.htmx_table />`` component hides the ``pk`` column by default — pass
    ``show_pk=True`` in the context to render it.

    Default: ``()``

.. attribute:: labels
    :type: Dict[str, str] | None

    Custom display labels for fields in table headers and filter UI.

    Default: ``None``

.. attribute:: hidden_fields
    :type: Tuple[str, ...]

    Field names (must also appear in ``fields``) to keep in the queryset projection and
    context, but mark ``visible: False`` on so ``<c-tables.htmx_table />`` skips rendering
    their column. Useful for fields a view needs for :meth:`get_transform_data` but
    shouldn't display.

    Default: ``()``

.. attribute:: hx_target_id
    :type: str | None

    The HTMX target element ID for list updates. Used by Cotton components.

    Default: ``None``

.. attribute:: paginate_by
    :type: int

    Number of items per page for pagination. Can be overridden per-request via the
    ``?paginate_by=`` query parameter (see below) — when set on the view, the
    ``<c-tables.htmx_table />`` component renders a "Show N entries" selector that
    submits this parameter.

    Default: ``25``

.. attribute:: elided_each_side
    :type: int

    Number of page numbers shown on each side of the current page in the elided
    page range (passed to ``Paginator.get_elided_page_range``). Only read when
    ``paginate_by`` is set.

    Default: ``1``

.. attribute:: elided_ends
    :type: int

    Number of page numbers shown at each end of the elided page range (passed to
    ``Paginator.get_elided_page_range``). Only read when ``paginate_by`` is set.

    Default: ``1``

.. attribute:: enable_history
    :type: bool

    Whether the ``header_cell``/``pager`` Cotton components push sort, filter, and
    page changes onto the browser history via ``hx-push-url``. When enabled, add
    ``hx-history-elt`` to the element wrapping ``<c-tables.htmx_table />`` so
    Back/Forward navigation restores the table correctly — see
    :doc:`../guide/list_views`.

    Default: ``False``

Context Variables
~~~~~~~~~~~~~~~~~

The view provides the following context variables for templates:

.. attribute:: query_params
    :type: str

    URL-encoded query string (without the ``page`` parameter).

.. attribute:: page_range
    :type: List[int | str]

    Elided page range for pagination controls (shows first, last, and pages around current).

.. attribute:: order_by
    :type: str | None

    The currently active ordering field (with ``-`` prefix for descending).

.. attribute:: path
    :type: str

    The current request path.

.. attribute:: hx_target_id
    :type: str | None

    The HTMX target element ID (from view attribute).

.. attribute:: query
    :type: str

    Full query string including ``order_by`` but without ``page``.

.. attribute:: filter_query
    :type: str

    Query string containing only filter parameters (no ``order_by`` or ``page``).

.. attribute:: filters
    :type: Dict[str, str]

    Template-ready dict mapping plain field names to their filter values.

.. attribute:: fields
    :type: List[Dict[str, str | bool]]

    A list of ``{"name": str, "label": str, "visible": bool}`` dicts, one per field
    from ``get_fields()`` (always including ``"pk"``). ``visible`` is ``False`` for
    any field listed in ``hidden_fields``.

.. attribute:: enable_history
    :type: bool

    Whether sort/filter/page links should push browser history entries (from the
    view's ``enable_history`` attribute).

URL Query Parameters
~~~~~~~~~~~~~~~~~~~~

**Filtering**

Filters use the format ``field_name.filter_type=value``:

.. code-block:: text

    # Exact match
    /articles/?status.eq=published

    # Case-insensitive match
    /articles/?title.ieq=Django

    # Contains (case-sensitive)
    /articles/?title.like=htmx

    # Greater than or equal
    /articles/?views.gte=100

    # Multiple filters
    /articles/?status.eq=published&views.gte=100

See :doc:`../guide/filters_sorting` for complete filter reference.

**Sorting**

.. code-block:: text

    # Ascending sort
    /articles/?order_by=created_at

    # Descending sort
    /articles/?order_by=-created_at

**Pagination**

.. code-block:: text

    # Specific page
    /articles/?page=2

    # Override the page size (also settable from the table's "Show N entries" selector)
    /articles/?paginate_by=50

.. note::
   ``paginate_by`` from the query string is parsed with ``int()`` and applied
   without clamping to a min/max or to the selector's preset options
   (``10``/``25``/``50``/``100``) — a view that exposes this to untrusted users
   should validate the requested page size itself, e.g. in an overridden
   :meth:`get_context_data` or :meth:`setup`.

Example
~~~~~~~

.. code-block:: python

    from django_htmx_plus.views import HtmxListView
    from myapp.models import Article

    class ArticleListView(HtmxListView):
        model = Article
        template_name = "articles/list.html"
        paginate_by = 10
        hx_target_id = "#article-table"

        # Restrict to these fields
        fields = ("id", "title", "status", "created_at")

        # Custom labels
        labels = {
            "created_at": "Date Created",
            "status": "Publication Status",
        }

Integration with Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the provided context variables in templates:

.. code-block:: html

    {% extends "base.html" %}
    {% load cotton_extras %}

    {% block content %}
    <div id="article-table" hx-trigger="articleCreated from:body">
        <c-tables.htmx_table class="table table-striped" />
    </div>
    {% endblock %}

The ``HtmxListView`` automatically handles:

- Query parameter parsing and validation
- ORM filter generation
- Sorting
- Pagination with elided page ranges

Transforming Rows
~~~~~~~~~~~~~~~~~~

Override :meth:`get_transform_data` to post-process each page's rows before they reach the
template, without re-implementing filtering or pagination:

.. code-block:: python

    class ArticleListView(HtmxListView):
        model = Article
        fields = ("title", "status", "created_at")

        def get_transform_data(self, objects):
            rows = super().get_transform_data(objects)
            for row in rows:
                row["status"] = row["status"].title()
            return rows

``get_transform_data`` receives the current page's queryset (or values queryset) and must
return the list of rows to render.

Custom / Dynamic Querysets
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default ``get_queryset()`` resolves the view's base queryset (from ``self.queryset``
or ``self.model``), then applies URL-based filtering, ``order_by``, and the ``fields``
projection via :meth:`queryset_values`. To supply a fully custom or dynamic queryset —
a different manager, ``select_related``/``prefetch_related``, per-user logic — override
``get_queryset()`` without calling ``super()``, and pass your queryset through
:meth:`queryset_values` to opt back into the view's automatic filtering/sorting:

.. code-block:: python

    class ArticleListView(HtmxListView):
        model = Article
        fields = ("title", "status", "created_at")

        def get_queryset(self):
            queryset = Article.objects.select_related("author") if self.request.user.is_staff \
                else Article.published.select_related("author")
            return self.queryset_values(queryset)

.. method:: queryset_values(queryset)

    Applies ``self.filter`` (parsed from the URL's ``field.filter_type=value`` query
    parameters), orders the result by ``self.order_by``, and restricts the projection to
    :meth:`get_fields` (always including ``"pk"``). Call this from a fully overridden
    ``get_queryset()`` to get the same automatic filter/order_by/values behavior as the
    default implementation.

    If you skip ``queryset_values()`` and return a queryset directly, remember that
    without the final ``.values(*fields)`` step, full model instances are returned
    instead of the ``fields``-restricted dicts templates expect.
