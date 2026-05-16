========
Features
========

django-htmx-plus provides a comprehensive set of tools for building modern HTMX-powered Django applications.

HTTP Responses
==============

**HtmxResponse**
    A 204 No Content response that fires HTMX events on the client. Useful for background operations that don't need to update the DOM.

**HtmxRedirectResponse**
    Sends an ``HX-Redirect`` header to navigate the browser to a new URL without a traditional HTTP redirect.

See :doc:`guide/responses` for detailed usage.

Middleware
==========

**HtmxMessagesMiddleware**
    Automatically forwards Django messages to HTMX clients via the ``HX-Trigger`` header. Messages from any view are seamlessly converted to HTMX events that your JavaScript can listen to.

Mixins
======

**HtmxFormResponseMixin**
    A mixin for ``FormView`` and ``CreateView`` that replaces the default success redirect with an HTMX trigger response. Perfect for inline form submissions and modals.

Views
=====

**HtmxListView**
    A drop-in replacement for Django's ``ListView`` with built-in:

    - URL-based filtering with multiple operators (exact, contains, range, etc.)
    - Column sorting (ascending/descending)
    - Elided pagination
    - Context variables for template rendering

Cotton Components
=================

A set of `django-cotton <https://github.com/wrabit/django-cotton>`_ components for rendering:

- **Sortable table headers** – Click to toggle sort direction
- **Paginated tables** – Bootstrap 5 pagination controls
- **Icon components** – Chevrons for sort indicators and pagination
- **Full table component** – Auto-generated from your list view context

Template Filters
================

- **get_attr** – Access object attributes in templates
- **get_key_value** – Access dictionary values in templates

JavaScript Integration
======================

**django-htmx-plus.js**
    An ES module that automatically integrates Bootstrap 5 Modals and Offcanvases with HTMX:

    - Opens modals/offcanvases when HTMX swaps content
    - Closes them when receiving empty responses
    - Resets modal body on close

Filtering and Sorting
=====================

Advanced URL-based filtering with support for:

- Exact matching
- Case-insensitive matching
- Greater than / less than comparisons
- Range queries
- Text searching
- Null checks
- In/Not In lists

See :doc:`guide/filters_sorting` for complete filter reference.

Integration
===========

All components are designed to work seamlessly together:

1. Use ``HtmxListView`` to provide filtered/sorted data
2. Render with ``HtmxListView`` context variables
3. Use Cotton components for sortable tables and pagination
4. Handle form submissions with ``HtmxFormResponseMixin``
5. Display modal responses with ``django-htmx-plus.js``
6. Forward messages with ``HtmxMessagesMiddleware``
