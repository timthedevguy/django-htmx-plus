======
Mixins
======

The ``django_htmx_plus.mixins`` module provides reusable mixins for HTMX-enhanced views.

HtmxFormResponseMixin
=====================

.. code-block:: python

    from django_htmx_plus.mixins import HtmxFormResponseMixin

A mixin for ``FormView`` and ``CreateView`` that replaces the default success redirect with an HTMX trigger response.

Attributes
~~~~~~~~~~

.. attribute:: valid_triggers
    :type: List[str]

    List of HTMX event names to include in the ``HX-Trigger`` header on successful form submission.

    Default: ``[]``

.. attribute:: success_message
    :type: str | None

    Optional Django success message to queue after form submission. The message is automatically added to the ``HX-Trigger`` header by ``HtmxMessagesMiddleware``.

    Default: ``None``

Example
~~~~~~~

.. code-block:: python

    from django.views.generic.edit import CreateView
    from django_htmx_plus.mixins import HtmxFormResponseMixin
    from myapp.models import Article
    from myapp.forms import ArticleForm

    class ArticleCreateView(HtmxFormResponseMixin, CreateView):
        model = Article
        form_class = ArticleForm
        template_name = "articles/form.html"

        valid_triggers = ["articleCreated", "refreshList"]
        success_message = "Article created successfully."

Behavior
~~~~~~~~

On successful form submission:

1. The form is saved (by calling ``form.save()``)
2. The optional success message is queued
3. An ``HtmxResponse`` with the specified triggers is returned (204 No Content)

On form validation errors:

1. The form is re-rendered with errors as usual
2. No HTMX response is sent

This allows you to build inline forms and modals that close/update automatically on success and display validation errors in place.
