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
        paginate_by = 20
        target_id = "#article-table"

        # Restrict to these fields only
        fields = ("id", "title", "status", "created_at")

The view automatically handles:

- URL-based filtering (``status.eq=published``)
- Sorting (``order_by=created_at`` or ``order_by=-created_at``)
- Pagination
- Query string preservation for updates

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
        paginate_by = 20

        fields = ("id", "title", "status", "created_at", "author")

        labels = {
            "created_at": "Date Created",
            "status": "Publication Status",
            "author": "Written by",
        }

The labels are used by Cotton components and available in ``context['fields']['labels']``.

Advanced: Allowing All Fields
=============================

By default, ``HtmxListView`` requires you to explicitly list allowed fields (for security). To allow any field:

.. code-block:: python

    class ArticleListView(HtmxListView):
        model = Article
        fields = ("__all__",)  # Allow filtering/sorting on any field

Use this with caution in production apps, as it exposes all model fields to filtering.

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

Best Practices
==============

1. **Set ``target_id`` for HTMX updates** – helps routing of swap requests
2. **Use specific field restrictions** – only allow filtering on intended fields
3. **Provide custom labels** – makes the table headers more user-friendly
4. **Test edge cases** – empty results, invalid filters, etc.
5. **Combine with filters form** – makes filtering discoverable to users
6. **Use triggers for modal integration** – automatic table updates
7. **Consider query performance** – optimize queryset if filtering many rows
