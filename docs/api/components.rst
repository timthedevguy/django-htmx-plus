==========
Components
==========

The ``django_htmx_plus.components`` package includes Cotton components for building HTMX-powered tables.

Overview
========

django-htmx-plus provides a set of `django-cotton <https://github.com/wrabit/django-cotton>`_ components that integrate seamlessly with ``HtmxListView`` to render sortable, paginated tables with Bootstrap 5 styling.

Loading Components
~~~~~~~~~~~~~~~~~~

In your template, load the Cotton tag library:

.. code-block:: html

    {% load cotton_extras %}

Main Table Component
====================

c-tables.htmx_table
~~~~~~~~~~~~~~~~~~~

Renders a complete table with auto-generated headers, rows, and pagination controls.

.. code-block:: html

    <c-tables.htmx_table class="table table-striped" />

Uses the following context variables from ``HtmxListView``:

- ``fields`` – Column definitions and labels
- ``objects`` – List of items to display
- ``order_by`` – Current sort field
- ``path`` – Request path
- ``filter_query`` – Query string with filters only
- ``target_id`` – HTMX target element ID
- ``page_obj`` – Current page object
- ``paginator`` – Paginator instance

Header Components
=================

c-tables.head
~~~~~~~~~~~~~

Wraps header cells in a ``<thead>`` section:

.. code-block:: html

    <c-tables.head>
        <c-tables.header_cell name="title">Title</c-tables.header_cell>
        <c-tables.header_cell name="created_at">Date Created</c-tables.header_cell>
    </c-tables.head>

c-tables.header_cell
~~~~~~~~~~~~~~~~~~~~

Renders a sortable table header cell with a chevron indicator:

.. code-block:: html

    <c-tables.header_cell name="title">Title</c-tables.header_cell>

Attributes:

- ``name`` – Field name (must be in ``fields``)
- Content – Display label for the header

Behavior:

- Clicking toggles between ascending/descending sort
- Shows a chevron icon indicating current sort direction
- Generates an ``hx-get`` request with the new sort order

Pagination Component
====================

c-tables.pager
~~~~~~~~~~~~~~

Renders Bootstrap 5 pagination controls with elided page numbers:

.. code-block:: html

    <c-tables.pager />

Features:

- Previous/Next buttons
- Elided page range (shows first, last, and pages around current)
- All controls are wired with ``hx-get`` requests
- Bootstrap pagination styling

Icon Components
===============

Chevron Icons
~~~~~~~~~~~~~

Used internally by header cells and pagination, but available for custom use:

.. code-block:: html

    <c-icons.chevron_up add_class="ms-1" />
    <c-icons.chevron_down add_class="ms-1" />
    <c-icons.chevron_left />
    <c-icons.chevron_right />

Attributes:

- ``add_class`` – Additional CSS classes to append

Complete Example
================

.. code-block:: html

    {% extends "base.html" %}
    {% load cotton_extras %}

    {% block content %}
    <div class="container mt-4">
        <h1>Articles</h1>

        <!-- HTMX Container for table updates -->
        <div id="article-table" hx-trigger="articleCreated from:body">
            <c-tables.htmx_table class="table table-striped table-hover" />
        </div>
    </div>
    {% endblock %}

The view automatically provides all necessary context for the components to work.
