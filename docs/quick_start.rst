===========
Quick Start
===========

This guide will get you up and running with django-htmx-plus in minutes.

Basic Response with Triggers
=============================

Send a 204 No Content response that fires HTMX events on the client:

.. code-block:: python

    from django_htmx_plus.http import HtmxResponse

    def my_view(request):
        # ... do some work ...
        return HtmxResponse(triggers=["itemUpdated", "refreshStats"])

The response sets ``HX-Trigger: itemUpdated,refreshStats``, which HTMX picks up to re-fetch any elements listening for those events.

See :doc:`guide/responses` for more details.

Form Views with HTMX Support
=============================

Use ``HtmxFormResponseMixin`` to automatically handle form submissions with HTMX:

.. code-block:: python

    from django.views.generic.edit import CreateView
    from django_htmx_plus.mixins import HtmxFormResponseMixin
    from myapp.models import Article
    from myapp.forms import ArticleForm

    class ArticleCreateView(HtmxFormResponseMixin, CreateView):
        model = Article
        form_class = ArticleForm
        template_name = "articles/form.html"

        valid_triggers = ["articleCreated"]
        success_message = "Article created successfully."

After a valid submission, the form is saved, an optional Django success message is queued, and an HTMX response with the ``articleCreated`` trigger is returned.

See :doc:`guide/forms` for more details.

Filterable List Views
=====================

Create interactive list views with URL-based filtering, sorting, and pagination:

.. code-block:: python

    from django_htmx_plus.views import HtmxListView
    from myapp.models import Article

    class ArticleListView(HtmxListView):
        model = Article
        template_name = "articles/list.html"
        paginate_by = 20
        target_id = "#article-table"

        # Restrict filtering and sorting to these fields
        fields = ("id", "title", "status", "created_at")

        # Optional custom column labels
        labels = {
            "created_at": "Date Created",
        }

Users can now filter and sort by URL parameters:

.. code-block:: text

    # Filter by status
    /articles/?status.eq=published

    # Filter by title containing "django"
    /articles/?title.ilike=django

    # Sort by created_at descending
    /articles/?order_by=-created_at

    # Multiple filters
    /articles/?status.eq=published&views.gte=100

See :doc:`guide/list_views` for more details.

Cotton Table Components
=======================

Render sortable, paginated tables with Bootstrap 5 styling:

.. code-block:: html

    {% load cotton_extras %}

    <c-tables.htmx_table class="table table-striped" />

The component automatically integrates with your ``HtmxListView`` to provide sortable headers, pagination, and row rendering.

See :doc:`guide/components` for more details.

Messages Middleware
===================

Django messages are automatically forwarded to HTMX clients:

.. code-block:: python

    from django.contrib import messages

    def my_view(request):
        messages.success(request, "Record saved.")
        return HtmxResponse(triggers=["recordUpdated"])

The message is automatically added to the HTMX response as an ``HX-Trigger`` event that your JavaScript can listen to:

.. code-block:: javascript

    document.body.addEventListener("messages", (event) => {
        event.detail.value.forEach(({message, tags}) => {
            showToast(message, tags); // your toast implementation
        });
    });

See :doc:`guide/modals` for complete setup with Bootstrap.

Next Steps
==========

- Read about :doc:`guide/responses` for more response types
- Explore :doc:`guide/list_views` for advanced filtering and sorting
- Check :doc:`guide/components` for Cotton component usage
- Browse the :doc:`api/index` reference
