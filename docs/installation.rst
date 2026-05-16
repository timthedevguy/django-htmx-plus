============
Installation
============

Requirements
============

- Python 3.11+
- Django (any version compatible with the above)
- `django-cotton <https://github.com/wrabit/django-cotton>`_ ≥ 2.6

Install the Package
===================

Using pip:

.. code-block:: bash

    pip install django-htmx-plus

Using poetry:

.. code-block:: bash

    poetry add django-htmx-plus

Configure Django
================

Add the package to your ``INSTALLED_APPS`` and configure the middleware in your ``settings.py``:

.. tip::
   The middleware ensures Django messages (success, info, warning, error) added in a view are automatically delivered to the client as HTMX events, allowing client-side JavaScript to display them without a full page reload, without this middleware Django messages would only show on the next full page load.

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        "django_cotton",
        "django_htmx_plus",
    ]

    MIDDLEWARE = [
        # ...
        "django.contrib.messages.middleware.MessageMiddleware"
        "django_htmx_plus.middleware.HtmxMessagesMiddleware",  # <-- Add this middleware after MessageMiddleware
    ]

HTMX
====
It is assumed you have HTMX already set up in your project. If not, you can include it via CDN in your base template or use `django-htmx <https://django-htmx.readthedocs.io/en/latest/>`_ to provide it.

Bootstrap Integration
=====================

django-htmx-plus is designed to work seamlessly with Bootstrap 5. A helper script will automagically wire up Bootstrap 5 Modals and Offcanvas elements.  Please see :doc:`api/javascript` for details on how to use the included JavaScript utilities to trigger modals and offcanvas components from your views.

Next Steps
==========

- Check out :doc:`quick_start` for basic usage examples
- See :doc:`features` for a complete feature overview
