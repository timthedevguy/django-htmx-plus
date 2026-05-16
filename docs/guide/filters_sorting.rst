==========================
Filtering and Sorting Guide
==========================

This guide covers using URL-based filtering and sorting with ``HtmxListView``.

Basic Filtering
===============

Filters are expressed as query parameters using the format ``field_name.filter_type=value``:

.. code-block:: text

    /articles/?status.eq=published

Building a Filter Form
======================

Create a simple filter form to make filtering discoverable:

.. code-block:: html

    {% extends "base.html" %}

    {% block content %}
    <div class="container mt-4">
        <form method="get" class="mb-4">
            <div class="row">
                <div class="col-md-4">
                    <select name="status.eq" class="form-select">
                        <option value="">-- Select Status --</option>
                        <option value="draft" {% if 'draft' in filter_query %}selected{% endif %}>Draft</option>
                        <option value="published" {% if 'published' in filter_query %}selected{% endif %}>Published</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <input type="text" name="title.ilike" placeholder="Search title..." class="form-control"
                           value="{% if 'title.ilike' in filter_query %}{{ request.GET.title__ilike }}{% endif %}">
                </div>
                <div class="col-md-4">
                    <button type="submit" class="btn btn-primary w-100">Filter</button>
                </div>
            </div>
        </form>

        <!-- Table with results -->
        <div id="article-table" hx-trigger="articleCreated from:body">
            <c-tables.htmx_table class="table table-striped" />
        </div>
    </div>
    {% endblock %}

Common Filter Patterns
======================

Exact Match
~~~~~~~~~~~

Find articles with exactly "published" status:

.. code-block:: text

    /articles/?status.eq=published

Partial Text Match
~~~~~~~~~~~~~~~~~~~

Find articles containing "django" in title:

.. code-block:: text

    /articles/?title.ilike=django

Numeric Comparison
~~~~~~~~~~~~~~~~~~~

Find articles with at least 100 views:

.. code-block:: text

    /articles/?views.gte=100

Date Range
~~~~~~~~~~

Find articles from 2024:

.. code-block:: text

    /articles/?created_at.rng=['2024-01-01','2024-12-31']

Multiple Conditions
~~~~~~~~~~~~~~~~~~~

Combine filters with ``&``:

.. code-block:: text

    /articles/?status.eq=published&views.gte=100&author.eq=alice

All conditions are AND'ed together.

Filter Reference
================

Text Filters
~~~~~~~~~~~~

===================== =================================================== ==========================
Parameter             Operator                                              Example
===================== =================================================== ==========================
``field.eq``          Exact match (case-sensitive)                          ``status.eq=published``
``field.ieq``         Exact match (case-insensitive)                        ``title.ieq=django``
``field.like``        Contains (case-sensitive)                             ``body.like=htmx``
``field.ilike``       Contains (case-insensitive)                           ``title.ilike=django``
``field.sw``          Starts with (case-sensitive)                          ``title.sw=Django``
``field.isw``         Starts with (case-insensitive)                        ``title.isw=django``
``field.ew``          Ends with (case-sensitive)                            ``title.ew=plus``
``field.iew``         Ends with (case-insensitive)                          ``title.iew=plus``
===================== =================================================== ==========================

Numeric and Date Filters
~~~~~~~~~~~~~~~~~~~~~~~~

==================== ================================ ============================================
Parameter            Operator                         Example
==================== ================================ ============================================
``field.gt``         Greater than                     ``views.gt=100``
``field.gte``        Greater than or equal            ``views.gte=100``
``field.lt``         Less than                        ``views.lt=10``
``field.lte``        Less than or equal               ``views.lte=10``
``field.rng``        Range (start, end)               ``created_at.rng=['2024-01-01','2024-12-31']``
==================== ================================ ============================================

Special Filters
~~~~~~~~~~~~~~~

==================== =================== =========================================
Parameter            Operator            Example
==================== =================== =========================================
``field.in``         In list             ``status.in=['draft','published']``
``field.nl``         Is null             ``deleted_at.nl=True``
``field.sch``        Full-text search    ``body.sch=htmx``
==================== =================== =========================================

Sorting
=======

Sort with the ``order_by`` parameter. Use ``-`` prefix for descending:

.. code-block:: text

    # Ascending sort
    /articles/?order_by=created_at

    # Descending sort
    /articles/?order_by=-created_at

    # Combined with filters
    /articles/?status.eq=published&order_by=-views

Combining Filters and Sorting
==============================

Use both together for flexible querying:

.. code-block:: text

    /articles/?status.eq=published&author.eq=alice&views.gte=100&order_by=-created_at&page=2

This query:

1. Filters to published articles
2. By author "alice"
3. With at least 100 views
4. Sorted newest first
5. Shows page 2

Advanced: Building Dynamic Filter URLs
=======================================

In templates, use the context variables to build filter URLs:

.. code-block:: html

    <!-- Add filter while preserving existing filters -->
    <a href="?{{ query_params }}&status.eq=published">Published Only</a>

    <!-- Sort by title -->
    <a href="?{{ filter_query }}&order_by=title">Sort by Title</a>

    <!-- Toggle sort direction -->
    {% if order_by == 'created_at' %}
        <a href="?{{ filter_query }}&order_by=-created_at">Oldest First</a>
    {% else %}
        <a href="?{{ filter_query }}&order_by=created_at">Newest First</a>
    {% endif %}

The context variables help build URLs that preserve or modify filters correctly.

Advanced: Custom Filter Widgets
===============================

Create reusable filter components:

.. code-block:: html

    {# Filter widget #}
    {% with param_name=param_name value=value options=options %}
    <div class="filter-widget">
        <label>{{ label }}</label>
        <select name="{{ param_name }}" class="form-select" hx-get="." hx-target="#results">
            <option value="">-- Any --</option>
            {% for opt_value, opt_label in options %}
                <option value="{{ opt_value }}" {% if opt_value == value %}selected{% endif %}>
                    {{ opt_label }}
                </option>
            {% endfor %}
        </select>
    </div>
    {% endwith %}

Use in your filter form:

.. code-block:: html

    {% include "filters/select.html" with param_name="status.eq" value=status label="Status" options=status_choices %}

Advanced: Range Picker
======================

For date ranges, use a JavaScript date picker:

.. code-block:: html

    <div class="mb-3">
        <label>Created Date Range</label>
        <input type="date" name="created_at_start" class="form-control" id="start-date">
        <input type="date" name="created_at_end" class="form-control" id="end-date">
    </div>

    <script>
    document.querySelector('form').addEventListener('submit', function(e) {
        const start = document.querySelector('#start-date').value;
        const end = document.querySelector('#end-date').value;
        if (start && end) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'created_at.rng';
            input.value = `['${start}','${end}']`;
            this.appendChild(input);
        }
    });
    </script>

Best Practices
==============

1. **Only expose necessary fields** – Use the ``fields`` attribute to whitelist filterable columns
2. **Provide default filters** – Show relevant data without manual filtering
3. **Test edge cases** – Empty results, invalid dates, etc.
4. **Make filters discoverable** – Use forms instead of requiring users to know URL syntax
5. **Use meaningful parameter names** – Match field names when possible
6. **Preserve filters in pagination** – Use context variables to build URLs
7. **Consider performance** – Complex filters on large datasets may be slow
