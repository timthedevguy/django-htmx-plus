=======================
Working with List Views
=======================

This guide covers using ``HtmxListView`` to build interactive, filterable list views.

Basic List View
===============

Create a filterable list view with sorting and pagination:

.. code-block:: python

    from django_htmx_plus.views import HtmxListView
    from myapp.models import Article

    class ArticleListView(HtmxListView):
        model = Article
        template_name = "article/list.html"
        paginate_by = 10
        hx_target_id = "#article-table"

        # Restrict to these fields only
        fields = ("id", "title", "status", "created_at")

The view automatically handles:

- URL-based filtering (``status.eq=published``)
- Sorting (``order_by=created_at`` or ``order_by=-created_at``)
- Pagination
- Query string preservation for updates

.. note::
   ``"pk"`` is always added to ``fields`` automatically, even if you don't list it, so rows
   stay uniquely identifiable. The ``<c-tables.htmx_table />`` component hides the ``pk``
   column by default — pass ``show_pk=True`` in the context if you want it rendered.

Automatic PK Injection
======================
Since ``"pk"`` is always added to ``fields`` at the beginning of the fields list there may be a time that you would like to show the column in a certain position.  Simply add the ``"pk"`` to your field list in the HtmxListView and it will be shown regardless of the ``show_pk=True`` setting and will be shown in the position you specified.

.. code-block:: python

    from django_htmx_plus.views import HtmxListView
    from myapp.models import Article

    class ArticleListView(HtmxListView):
        model = Article
        template_name = "article/list.html"
        paginate_by = 10
        hx_target_id = "#article-table"

        # Restrict to these fields only
        fields = ("id", "title", "status", "pk", "created_at")

In the sample code above the PK column will be rendered second to last.

Filtering
=========

Users can filter by adding query parameters:

.. code-block:: text

    # Filter by exact status
    /articles/?status.eq=published

    # Filter by title containing "django" (case-insensitive)
    /articles/?title.ilike=django

    # Filter by views greater than or equal to 100
    /articles/?views.gte=100

    # Filter by creation date range
    /articles/?created_at.rng=['2024-01-01','2024-12-31']

    # Multiple filters
    /articles/?status.eq=published&views.gte=100&title.ilike=django

.. attention::
   I have not implemented a cotton component to provide filtering UI elements.  You can build your own filter form that submits with HTMX to make it more user-friendly until I add this feature.

See :doc:`../api/filters` for the complete filter reference.

Sorting
=======

Add sorting with the ``order_by`` parameter:

.. code-block:: text

    # Sort by title ascending
    /articles/?order_by=title

    # Sort by created_at descending
    /articles/?order_by=-created_at

    # Combine filters and sorting
    /articles/?status.eq=published&order_by=-created_at

With ``HtmxListView``, the current sort order is tracked in the context as ``order_by``.

Pagination
==========

Pagination is automatic with ``paginate_by``:

.. code-block:: text

    # Page 2
    /articles/?page=2

    # With filters and sorting
    /articles/?status.eq=published&order_by=-created_at&page=2

The view provides:

- ``page_obj`` – Current page object
- ``paginator`` – Paginator instance
- ``page_range`` – Elided page numbers (shows first, last, and pages around current)

Changing the Page Size
=======================

Whenever ``paginate_by`` is set (so the view is paginated), ``<c-tables.htmx_table />``
renders a "Show N entries" ``<select>`` above the table with options for ``10``,
``25``, ``50``, and ``100`` rows per page. Choosing an option issues an
``hx-get`` with a ``paginate_by`` query parameter, which the view applies for
that request:

.. code-block:: text

    /articles/?paginate_by=50

Once a non-default page size is active, subsequent sort/page links (rendered by
``header_cell`` and ``pager``) carry the same ``paginate_by`` forward so the
chosen page size persists across sorting and paging.

.. attention::
   The view applies ``paginate_by`` from the query string via a plain ``int()``
   conversion — there's no clamping to the selector's preset options or to any
   min/max. If this view is reachable by untrusted users, override
   :meth:`get_context_data` (or :meth:`setup`) to validate/clamp the requested
   value before it reaches ``Paginator``.

Browser History (Back/Forward Navigation)
==========================================

Sorting, pagination, and filtering can update the URL query string and push a
new browser history entry for each change (via ``hx-push-url`` on the
``header_cell``/``pager`` components), so the address bar reflects the
current table state and can be bookmarked or shared.

The "Show N entries" selector pushes history a little differently: its
selected value isn't known server-side until after the request fires, so
rather than a static ``hx-push-url`` it carries a ``data-htmx-plus-push-url``
attribute (the page/query string, without the page size), and
:doc:`../api/javascript`'s shared script appends the selector's live value
and calls ``history.pushState`` once the request succeeds. This avoids
pushing the element's ``hx-get`` fetch path itself (which may point at a
different partial-fetch endpoint than the page's own URL).

This is opt-in — set ``enable_history = True`` on the view to turn it on:

.. code-block:: python

    class ArticleListView(HtmxListView):
        model = Article
        template_name = "article/list.html"
        enable_history = True

By default (``enable_history = False``), sort/page/filter links don't touch
``hx-push-url`` or browser history at all — the table updates in place with
no address bar changes. This is the safer default for tables embedded in
modals or alongside other independently-updating widgets on a page.

For the Back/Forward buttons to actually restore the table once history is
enabled, add ``hx-history-elt`` to the element wrapping
``<c-tables.htmx_table />`` — the same element that carries your
``hx_target_id``:

.. code-block:: html

    <div id="article-table" hx-history-elt>
        <c-tables.htmx_table class="table table-striped" />
    </div>

Without this, htmx falls back to snapshotting/restoring the entire ``<body>``
on history navigation, which doesn't line up with the smaller region your
sort/page/filter clicks actually swap — Back/Forward can then appear to do
nothing. ``hx-history-elt`` needs to be present on every page rendered by this
view for restoration to work reliably. If a page has multiple independent
tables, only enable history (and designate ``hx-history-elt``) on one of
them — htmx tracks a single history snapshot per page.

If this same wrapping element also refreshes on a custom trigger (e.g.
``hx-trigger="articleCreated from:body"`` after a modal form save), its
``hx-get`` needs the current URL's query string appended —
``?{{ request.GET.urlencode }}`` — so the refresh re-reads the browser's
current sort/filter/page state instead of resetting to the view's defaults:

.. code-block:: html

    <div id="article-table"
         hx-trigger="articleCreated from:body"
         hx-get="{{ path }}?{{ request.GET.urlencode }}"
         hx-history-elt>
        <c-tables.htmx_table class="table table-striped" />
    </div>

This is only necessary when ``enable_history`` is ``True`` — that's the only
case where the browser's address bar (and therefore ``request.GET`` on the
next render) can hold table state that differs from what the page was
originally rendered with. With history disabled, the trigger's plain
``hx-get`` (no appended query string) is fine.

Using Cotton Components
=======================

The Cotton table component automatically integrates:

.. code-block:: html

    <c-tables.htmx_table class="table table-striped" />

This renders:

- Sortable column headers (click to change sort)
- Table rows from the queryset
- Pagination controls with next/previous

Advanced: Custom Field Labels
=============================

Provide custom display labels for fields:

.. code-block:: python

    class ArticleListView(HtmxListView):
        model = Article
        template_name = "article/list.html"
        paginate_by = 10

        fields = ("id", "title", "status", "created_at", "author")

        labels = {
            "created_at": "Date Created",
            "status": "Publication Status",
            "author": "Written by",
        }

The labels are used by Cotton components via ``context['fields']``, a list of
``{"name", "label", "visible"}`` dicts — one per field in ``fields``. ``label`` is the
entry from ``labels`` if present and truthy, otherwise the field name run through
Django's ``capfirst`` filter.

``HtmxListView`` always requires you to explicitly list allowed fields (for security) —
there is no wildcard or bypass value. Any field a view needs to filter, sort, or display
must appear in ``fields``.

Advanced: Hiding Fields
=======================

Include a field in the queryset and context (e.g. so :meth:`get_transform_data` can use
it) without rendering a column for it:

.. code-block:: python

    class ArticleListView(HtmxListView):
        model = Article
        fields = ("id", "title", "status", "author_id")
        hidden_fields = ("author_id",)

``hidden_fields`` doesn't remove the field from filtering, sorting, or the queryset
projection — it only sets ``visible: False`` on that field's entry in ``context['fields']``,
which ``<c-tables.htmx_table />`` uses to skip rendering its header and cells.

Advanced: Custom Filtering Logic
=================================

For complex filtering, override ``get_queryset()``:

.. code-block:: python

    from django_htmx_plus.views import HtmxListView
    from django.db.models import Q

    class ArticleListView(HtmxListView):
        model = Article
        template_name = "article/list.html"

        fields = ("title", "status", "created_at")

        def get_queryset(self):
            # Start with view's automatic filtering
            queryset = super().get_queryset()

            # Add custom logic
            if self.request.user.is_staff:
                # Staff sees all articles
                pass
            else:
                # Others see only published articles
                queryset = queryset.filter(status="published")

            return queryset

The base implementation handles URL-based filters; your custom logic runs after.

Advanced: Transforming Rows
============================

To post-process rows (e.g. reformat a value) without overriding ``get_queryset()`` or
``get_context_data()``, override ``get_transform_data()``:

.. code-block:: python

    class ArticleListView(HtmxListView):
        model = Article
        fields = ("title", "status", "created_at")

        def get_transform_data(self, objects):
            rows = super().get_transform_data(objects)
            for row in rows:
                row["status"] = row["status"].title()
            return rows

It receives the current page's queryset (or values queryset, if ``fields`` is restricted)
and must return the list of rows for the template.

Best Practices
==============

1. **Set ``hx_target_id`` for HTMX updates** – helps routing of swap requests
2. **Use specific field restrictions** – only allow filtering on intended fields
3. **Provide custom labels** – makes the table headers more user-friendly
4. **Test edge cases** – empty results, invalid filters, etc.
5. **Combine with filters form** – makes filtering discoverable to users
6. **Use triggers for modal integration** – automatic table updates
7. **Consider query performance** – optimize queryset if filtering many rows
