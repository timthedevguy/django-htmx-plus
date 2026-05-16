======================
Working with Modals
======================

This guide covers setting up and using Bootstrap 5 modals with HTMX integration.

Setup
=====

The ``django-htmx-plus.js`` module automatically handles showing/hiding Bootstrap 5 modals when HTMX swaps content.

Base Template Setup
~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    {% extends "base.html" %}
    {% load django_htmx_plus %}

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{% block title %}My App{% endblock %}</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <!-- Import map for ES modules -->
        <script type="importmap">
        {
          "imports": {
            "@popperjs/core": "https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/esm/index.mjs",
            "bootstrap": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/esm/index.mjs"
          }
        }
        </script>
    </head>
    <body>
        <!-- Modal -->
        <div class="modal fade" data-htmx-plus-modal="form-dialog" tabindex="-1">
            <div class="modal-dialog">
                <div id="form-dialog" class="modal-content">
                    <!-- Form will be swapped here -->
                </div>
            </div>
        </div>

        <!-- Page content -->
        {% block content %}{% endblock %}

        <!-- Scripts -->
        <script src="https://unpkg.com/htmx.org"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <!-- Django HTMX Plus script -->
        {% htmx_plus_script %}
    </body>
    </html>

Creating Modal Forms
====================

Create a view that serves form content for modals:

.. code-block:: python

    from django.views.generic import TemplateView
    from django_htmx_plus.mixins import HtmxFormResponseMixin
    from myapp.models import Article
    from myapp.forms import ArticleForm

    class ArticleCreateModalView(TemplateView):
        """Serves the form for modal display"""
        template_name = "article/form_modal.html"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["form"] = ArticleForm()
            return context

    class ArticleCreateView(HtmxFormResponseMixin, CreateView):
        """Handles form submission"""
        model = Article
        form_class = ArticleForm
        template_name = "article/form_modal.html"

        valid_triggers = ["articleCreated"]
        success_message = "Article created successfully."

Form Template
~~~~~~~~~~~~~

.. code-block:: html

    <!-- article/form_modal.html -->
    <div class="modal-header">
        <h5 class="modal-title">New Article</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
    </div>
    <div class="modal-body">
        <form hx-post="{% url 'article-create' %}" hx-target="#form-dialog">
            {% csrf_token %}

            {% if form.non_field_errors %}
                <div class="alert alert-danger">
                    {{ form.non_field_errors }}
                </div>
            {% endif %}

            {% for field in form %}
                <div class="mb-3">
                    {{ field.label_tag }}
                    {{ field }}
                    {% if field.errors %}
                        <div class="invalid-feedback d-block">
                            {{ field.errors }}
                        </div>
                    {% endif %}
                </div>
            {% endfor %}

            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary">Save</button>
            </div>
        </form>
    </div>

Open Modal Button
~~~~~~~~~~~~~~~~~

.. code-block:: html

    {% extends "base.html" %}

    {% block content %}
    <div class="container mt-4">
        <button class="btn btn-primary" hx-get="{% url 'article-create-modal' %}" hx-target="#form-dialog">
            New Article
        </button>

        <!-- Table or list content here -->
    </div>
    {% endblock %}

How It Works
============

1. **User clicks button** – Button has ``hx-get="/article/create/"`` and ``hx-target="#form-dialog"``
2. **HTMX fetches form** – GET request to the form view
3. **Form renders in modal** – Content swaps into ``#form-dialog``
4. **django-htmx-plus.js shows modal** – Detects content swap and calls ``.show()`` on the Bootstrap modal
5. **User submits form** – POST request via HTMX
6. **Server saves or re-renders**:
   - **Success**: Returns empty ``HtmxResponse()``
   - **Validation error**: Re-renders form with errors
7. **Modal closes** – django-htmx-plus.js detects empty response and closes modal
8. **Table updates** – The ``articleCreated`` trigger refreshes the list

Multiple Modals
===============

Use different modal IDs for different forms:

.. code-block:: html

    <!-- Base template with multiple modals -->
    <div class="modal fade" data-htmx-plus-modal="create-dialog">
        <div class="modal-dialog">
            <div id="create-dialog" class="modal-content"></div>
        </div>
    </div>

    <div class="modal fade" data-htmx-plus-modal="edit-dialog">
        <div class="modal-dialog">
            <div id="edit-dialog" class="modal-content"></div>
        </div>
    </div>

    <div class="modal fade" data-htmx-plus-modal="delete-dialog">
        <div class="modal-dialog modal-sm">
            <div id="delete-dialog" class="modal-content"></div>
        </div>
    </div>

Trigger buttons:

.. code-block:: html

    <button hx-get="/article/create/" hx-target="#create-dialog">New</button>
    <button hx-get="/article/edit/{{ article.id }}/" hx-target="#edit-dialog">Edit</button>
    <button hx-get="/article/delete/{{ article.id }}/" hx-target="#delete-dialog">Delete</button>

Each modal opens independently.

Nested Forms (Multi-Step)
=========================

Create multi-step forms by replacing the form content:

.. code-block:: html

    <!-- Step 1: Basic info -->
    <form hx-post="/article/step-1/" hx-target="#form-dialog">
        <!-- Step 1 form fields -->
        <button type="submit" class="btn btn-primary">Next</button>
    </form>

    <!-- After submission, server returns Step 2 form -->
    <form hx-post="/article/step-2/" hx-target="#form-dialog">
        <!-- Step 2 form fields -->
        <button type="submit" class="btn btn-primary">Next</button>
    </form>

The modal stays open while the form content changes. Return an empty response to close.

Offcanvas (Side Panels)
=======================

The same integration works with Bootstrap Offcanvas:

.. code-block:: html

    <!-- Offcanvas instead of modal -->
    <div class="offcanvas offcanvas-end" data-htmx-plus-offcanvas="sidebar">
        <div class="offcanvas-header">
            <h5>Menu</h5>
            <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
        </div>
        <div id="sidebar" class="offcanvas-body">
            <!-- Content swapped here -->
        </div>
    </div>

    <button hx-get="/menu/" hx-target="#sidebar">Open Menu</button>

The ``data-htmx-plus-offcanvas`` attribute works the same as ``data-htmx-plus-modal``.

Complete Example App
====================

Here's a complete article management app with modals:

Django Views:

.. code-block:: python

    from django.views.generic import CreateView, UpdateView, TemplateView
    from django_htmx_plus.mixins import HtmxFormResponseMixin
    from myapp.models import Article
    from myapp.forms import ArticleForm

    class ArticleCreateView(HtmxFormResponseMixin, CreateView):
        model = Article
        form_class = ArticleForm
        template_name = "article/form_modal.html"
        valid_triggers = ["articleCreated"]
        success_message = "Article created."

    class ArticleUpdateView(HtmxFormResponseMixin, UpdateView):
        model = Article
        form_class = ArticleForm
        template_name = "article/form_modal.html"
        valid_triggers = ["articleUpdated"]
        success_message = "Article updated."

        def get_object(self):
            return Article.objects.get(pk=self.kwargs["pk"])

    class ArticleListView(TemplateView):
        template_name = "article/list.html"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["articles"] = Article.objects.all()
            return context

Template:

.. code-block:: html

    {% extends "base.html" %}
    {% load cotton_extras %}

    {% block modal %}
    <div class="modal fade" data-htmx-plus-modal="form-dialog">
        <div class="modal-dialog">
            <div id="form-dialog" class="modal-content"></div>
        </div>
    </div>
    {% endblock %}

    {% block content %}
    <div class="container mt-4">
        <h1>Articles</h1>
        <button hx-get="/article/create/" hx-target="#form-dialog" class="btn btn-primary mb-3">
            New Article
        </button>

        <div id="article-table" hx-trigger="articleCreated,articleUpdated from:body">
            <table class="table">
                <tbody>
                {% for article in articles %}
                    <tr>
                        <td>{{ article.title }}</td>
                        <td>{{ article.status }}</td>
                        <td>
                            <button hx-get="/article/edit/{{ article.id }}/" hx-target="#form-dialog" 
                                    class="btn btn-sm btn-primary">Edit</button>
                        </td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}

Best Practices
==============

1. **Always include title and close button** – Makes modals user-friendly
2. **Return empty HtmxResponse on success** – Triggers automatic close
3. **Re-render form on validation error** – Users see errors in context
4. **Use consistent modal IDs** – Makes debugging easier
5. **Include success messages** – Users need feedback
6. **Test modal close behavior** – Ensure proper cleanup
7. **Use target_id matching** – Keep ``hx-target`` and ``data-htmx-plus-modal`` IDs in sync
