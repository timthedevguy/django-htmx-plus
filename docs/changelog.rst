=========
Changelog
=========

This page documents all releases of django-htmx-plus.

[0.2.0] - 2024-05-16
====================
Fixes
-----
- Removed dependency on ``django-htmx`` to simplify installation
- Updated documentation

[0.1.0] - 2024-05-16
====================

Initial Release

Features
--------

- **HtmxResponse** – 204 No Content response with HX-Trigger header support
- **HtmxRedirectResponse** – Browser navigation via HX-Redirect header
- **HtmxMessagesMiddleware** – Django messages forwarding to HTMX clients
- **HtmxFormResponseMixin** – Automatic HTMX responses for form views
- **HtmxListView** – Enhanced ListView with URL-based filtering, sorting, and pagination
- **Filter Helpers** – URL parameter parsing for safe Django ORM filtering
- **Cotton Components** – Bootstrap 5 compatible table, header, and pagination components
- **Template Filters** – ``get_attr`` and ``get_key_value`` for template rendering
- **JavaScript Integration** – ``django-htmx-plus.js`` for Bootstrap modal/offcanvas automation

Core Features
~~~~~~~~~~~~~

- Full HTMX integration for Django views
- URL-based filtering with 14+ filter operators
- Automatic column sorting and pagination
- Bootstrap 5 component library
- Django messages integration
- Content Security Policy (CSP) nonce support
- Python 3.11+ support
