=======
Filters
=======

The ``django_htmx_plus.utils`` module provides filter parsing utilities for URL-based filtering in ``HtmxListView``.

Overview
========

django-htmx-plus supports a comprehensive set of URL-based filters that map to Django ORM lookups. Filters are expressed as query parameters using the format:

.. code-block:: text

    field_name.filter_type=value

Filter Types
============

Exact Matching
~~~~~~~~~~~~~~

.. code-block:: text

    status.eq=published

- **Filter type:** ``eq``
- **Django lookup:** ``exact``
- **Example:** ``/articles/?status.eq=published``
- **Behavior:** Case-sensitive exact match

Case-Insensitive Matching
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    title.ieq=Django

- **Filter type:** ``ieq``
- **Django lookup:** ``iexact``
- **Example:** ``/articles/?title.ieq=django``
- **Behavior:** Case-insensitive exact match

Text Search (case-sensitive)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    body.like=htmx

- **Filter type:** ``like``
- **Django lookup:** ``contains``
- **Example:** ``/articles/?body.like=introduction``
- **Behavior:** Substring match, case-sensitive

Text Search (case-insensitive)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    title.ilike=django

- **Filter type:** ``ilike``
- **Django lookup:** ``icontains``
- **Example:** ``/articles/?title.ilike=django``
- **Behavior:** Substring match, case-insensitive

Starts With
~~~~~~~~~~~

.. code-block:: text

    title.sw=Django

- **Filter type:** ``sw``
- **Django lookup:** ``startswith``
- **Example:** ``/articles/?title.sw=Django``
- **Behavior:** Case-sensitive prefix match

Case-Insensitive Starts With
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    title.isw=django

- **Filter type:** ``isw``
- **Django lookup:** ``istartswith``
- **Example:** ``/articles/?title.isw=django``
- **Behavior:** Case-insensitive prefix match

Ends With
~~~~~~~~~

.. code-block:: text

    title.ew=plus

- **Filter type:** ``ew``
- **Django lookup:** ``endswith``
- **Example:** ``/articles/?title.ew=plus``
- **Behavior:** Case-sensitive suffix match

Case-Insensitive Ends With
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    title.iew=plus

- **Filter type:** ``iew``
- **Django lookup:** ``iendswith``
- **Example:** ``/articles/?title.iew=plus``
- **Behavior:** Case-insensitive suffix match

Numeric Comparisons
~~~~~~~~~~~~~~~~~~~~

Greater Than (``gt``)
    - **Filter type:** ``gt``
    - **Example:** ``/articles/?views.gt=100``

Greater Than or Equal (``gte``)
    - **Filter type:** ``gte``
    - **Example:** ``/articles/?views.gte=100``

Less Than (``lt``)
    - **Filter type:** ``lt``
    - **Example:** ``/articles/?views.lt=10``

Less Than or Equal (``lte``)
    - **Filter type:** ``lte``
    - **Example:** ``/articles/?views.lte=10``

In List
~~~~~~~

.. code-block:: text

    status.in=['draft','published']

- **Filter type:** ``in``
- **Django lookup:** ``in``
- **Example:** ``/articles/?status.in=['draft','published']``
- **Behavior:** Match if value is in the provided list

Null Check
~~~~~~~~~~

.. code-block:: text

    deleted_at.nl=True

- **Filter type:** ``nl``
- **Django lookup:** ``isnull``
- **Example:** ``/articles/?deleted_at.nl=True``
- **Behavior:** Check if field is null or not null

Date/Time Range
~~~~~~~~~~~~~~~

.. code-block:: text

    created_at.rng=['2024-01-01','2024-12-31']

- **Filter type:** ``rng``
- **Django lookup:** ``range``
- **Example:** ``/articles/?created_at.rng=['2024-01-01','2024-12-31']``
- **Behavior:** Match values between start and end (inclusive)

Full-Text Search
~~~~~~~~~~~~~~~~

.. code-block:: text

    body.sch=htmx

- **Filter type:** ``sch``
- **Django lookup:** ``search`` (PostgreSQL only)
- **Example:** ``/articles/?body.sch=htmx``
- **Behavior:** Full-text search using database search capabilities

Multiple Filters
================

Combine multiple filters using ``&`` in the query string:

.. code-block:: text

    /articles/?status.eq=published&views.gte=100&created_at.rng=['2024-01-01','2024-12-31']

All filters are applied together using an AND condition.

Field Restrictions
===================

The ``fields`` attribute on ``HtmxListView`` controls which fields can be filtered:

.. code-block:: python

    class ArticleListView(HtmxListView):
        fields = ("title", "status", "created_at")  # Only these fields can be filtered

Set to ``("__all__",)`` to allow filtering on all fields (use with caution):

.. code-block:: python

    class ArticleListView(HtmxListView):
        fields = ("__all__",)  # Allow any field

Invalid field names in filter parameters are silently ignored for security.
