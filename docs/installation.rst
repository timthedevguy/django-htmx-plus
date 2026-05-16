============
Installation
============

Requirements
============

- Python 3.11+
- Django (any version compatible with the above)
- `django-htmx <https://github.com/adamchainz/django-htmx>`_ ≥ 1.27
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

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        "django_htmx",
        "django_cotton",
        "django_htmx_plus",
    ]

    MIDDLEWARE = [
        # ...
        "django_htmx.middleware.HtmxMiddleware",        # required by django-htmx
        "django_htmx_plus.middleware.HtmxMessagesMiddleware",
    ]

Next Steps
==========

- Check out :doc:`quick_start` for basic usage examples
- See :doc:`features` for a complete feature overview
