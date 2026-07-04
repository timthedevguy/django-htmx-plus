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
        paginate_by = 20

A drop-in replacement for Django's ``ListView`` with built-in URL-based filtering, column sorting, and elided pagination.

Attributes
~~~~~~~~~~

.. attribute:: fields
    :type: Tuple[str, ...] | List[str]

    The fields that are allowed for filtering and sorting. Set to ``("__all__",)`` to allow all fields.

    ``"pk"`` is always added automatically if it isn't already present (unless ``fields`` is
    ``"__all__"``), so rows remain uniquely identifiable even if you don't list it explicitly.
    The ``<c-tables.htmx_table />`` component hides the ``pk`` column by default — pass
    ``show_pk=True`` in the context to render it.

    Default: ``("__all__",)``

.. attribute:: labels
    :type: Dict[str, str] | None

    Custom display labels for fields in table headers and filter UI.

    Default: ``None``

.. attribute:: target_id
    :type: str | None

    The HTMX target element ID for list updates. Used by Cotton components.

    Default: ``None``

.. attribute:: paginate_by
    :type: int

    Number of items per page for pagination.

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

.. attribute:: target_id
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
    :type: Dict[str, List[str]]

    Dict with ``keys`` (list of field names, always including ``"pk"``) and ``labels``
    (list of display names).

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

Example
~~~~~~~

.. code-block:: python

    from django_htmx_plus.views import HtmxListView
    from myapp.models import Article

    class ArticleListView(HtmxListView):
        model = Article
        template_name = "articles/list.html"
        paginate_by = 20
        target_id = "#article-table"

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
