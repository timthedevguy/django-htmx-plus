=======================
Working with Components
=======================

This guide covers using the Cotton components provided by django-htmx-plus.

Overview
========

django-htmx-plus provides Cotton components for:

- Rendering sortable table headers
- Displaying paginated tables with Bootstrap 5 styling
- Building complete interactive tables with minimal template code

All components work with the context variables provided by ``HtmxListView``.

Complete Table Component
========================

The simplest way to build a table is using the complete component:

.. code-block:: html

    {% extends "base.html" %}
    {% load cotton_extras %}

    {% block content %}
    <div id="article-table" hx-trigger="articleCreated from:body">
        <c-tables.htmx_table class="table table-striped table-hover" />
    </div>
    {% endblock %}

This single component renders:

- Table headers with sorting
- Table rows
- Pagination controls

All automatic from your ``HtmxListView`` context.

Custom Table Structure
======================

For more control, build your table manually with individual components:

.. code-block:: html

    {% load cotton_extras %}

    <table class="table table-striped">
        <c-tables.head>
            <c-tables.header_cell name="title">Title</c-tables.header_cell>
            <c-tables.header_cell name="status">Status</c-tables.header_cell>
            <c-tables.header_cell name="created_at">Date</c-tables.header_cell>
            <th>Actions</th>
        </c-tables.head>
        <tbody>
            {% for article in objects %}
            <tr>
                <td>{{ article.title }}</td>
                <td>{{ article.status }}</td>
                <td>{{ article.created_at|date:"Y-m-d" }}</td>
                <td>
                    <a href="{% url 'article-edit' article.id %}" class="btn btn-sm btn-primary">Edit</a>
                    <a href="{% url 'article-delete' article.id %}" class="btn btn-sm btn-danger">Delete</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <c-tables.pager />

Sortable Headers
================

Make column headers sortable:

.. code-block:: html

    <c-tables.head>
        <c-tables.header_cell name="title">Title</c-tables.header_cell>
        <c-tables.header_cell name="author">Author</c-tables.header_cell>
        <c-tables.header_cell name="created_at">Date</c-tables.header_cell>
    </c-tables.head>

Each header:

- Shows a chevron icon indicating sort direction when active
- Links to toggle sort direction (ascending → descending → no sort)
- Uses HTMX to update the table without page reload

The ``order_by`` context variable shows the current sort field.

Pagination
==========

Add pagination controls with a single component:

.. code-block:: html

    <c-tables.pager />

Features:

- Previous/Next buttons (disabled at boundaries)
- Elided page numbers (shows first, last, and pages around current)
- All links use HTMX for smooth updates
- Bootstrap 5 pagination styling

Example with page range display:

.. code-block:: html

    <nav aria-label="Page navigation">
        <c-tables.pager />
    </nav>

Icon Components
===============

Use icon components directly for custom layouts:

.. code-block:: html

    {% load cotton_extras %}

    <!-- Chevron up (ascending sort) -->
    <c-icons.chevron_up />

    <!-- Chevron down (descending sort) -->
    <c-icons.chevron_down />

    <!-- Chevron left (previous page) -->
    <c-icons.chevron_left />

    <!-- Chevron right (next page) -->
    <c-icons.chevron_right />

All icons accept an optional ``add_class`` attribute:

.. code-block:: html

    <c-icons.chevron_up add_class="ms-1" />

Advanced: Custom Styling
=========================

Apply custom CSS classes to the table:

.. code-block:: html

    <c-tables.htmx_table class="table table-striped table-hover table-sm" />

Use Bootstrap table utilities:

- ``table-striped`` – Alternating row colors
- ``table-hover`` – Highlight row on hover
- ``table-sm`` – Smaller table
- ``table-bordered`` – Borders on all cells
- ``table-dark`` – Dark theme

Advanced: Multiple Tables on Same Page
=======================================

Each table needs a unique ``target_id``:

.. code-block:: python

    class DraftArticleListView(HtmxListView):
        model = Article
        template_name = "article/drafts.html"
        target_id = "#draft-table"

        def get_queryset(self):
            return super().get_queryset().filter(status="draft")

.. code-block:: python

    class PublishedArticleListView(HtmxListView):
        model = Article
        template_name = "article/published.html"
        target_id = "#published-table"

        def get_queryset(self):
            return super().get_queryset().filter(status="published")

Template with both tables:

.. code-block:: html

    {% extends "base.html" %}
    {% load cotton_extras %}

    {% block content %}
    <div class="container mt-4">
        <h2>Draft Articles</h2>
        <div id="draft-table" hx-trigger="articleCreated,articleUpdated from:body">
            <c-tables.htmx_table class="table table-striped" />
        </div>

        <h2>Published Articles</h2>
        <div id="published-table" hx-trigger="articleCreated,articleUpdated from:body">
            <c-tables.htmx_table class="table table-striped" />
        </div>
    </div>
    {% endblock %}

Each table updates independently based on filters and sorting.

Integration with Modals
=======================

Refresh a table when items are created in a modal:

.. code-block:: html

    {% extends "base.html" %}
    {% load django_htmx_plus %}
    {% load cotton_extras %}

    {% block modal %}
    <div class="modal fade" data-htmx-plus-modal="article-form">
        <div class="modal-dialog">
            <div id="article-form" class="modal-content"></div>
        </div>
    </div>
    {% endblock %}

    {% block content %}
    <button hx-get="{% url 'article-create' %}" hx-target="#article-form" class="btn btn-primary">
        New Article
    </button>

    <div id="article-table" hx-trigger="articleCreated from:body">
        <c-tables.htmx_table class="table table-striped" />
    </div>
    {% endblock %}

When the form fires the ``articleCreated`` trigger, the table automatically refreshes.

Best Practices
==============

1. **Use complete table component for simple cases** – Saves boilerplate
2. **Build custom tables for complex layouts** – Maximum flexibility
3. **Set unique target_id per table** – Ensures correct HTMX targeting
4. **Use meaningful sort fields** – Not all fields need sorting
5. **Add HTMX triggers for automatic updates** – Keeps UI in sync
6. **Test sorting and pagination** – Ensure query string handling works
7. **Consider performance** – Pagination helps with large datasets
