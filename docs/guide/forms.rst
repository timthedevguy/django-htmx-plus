==========================
Working with Form Views
==========================

This guide covers using ``HtmxFormResponseMixin`` to build inline forms and modals with HTMX.

Basic Form View
===============

Create a form view that uses HTMX for inline submission:

.. code-block:: python

    from django.views.generic.edit import CreateView
    from django_htmx_plus.mixins import HtmxFormResponseMixin
    from myapp.models import Article
    from myapp.forms import ArticleForm

    class ArticleCreateView(HtmxFormResponseMixin, CreateView):
        model = Article
        form_class = ArticleForm
        template_name = "article/form.html"

        # Events to fire on successful submission
        valid_triggers = ["articleCreated"]

        # Optional success message
        success_message = "Article created successfully."

On successful submission:

1. Form is saved
2. Success message is queued (if set)
3. ``HtmxResponse`` with triggers is returned (204 No Content)
4. Original form element is removed/updated by HTMX

Template for Inline Forms
=========================

Create the form template to render the form for HTMX submission:

.. code-block:: html

    <!-- article/form.html -->
    <form hx-post="{% url 'article-create' %}" hx-target="this" hx-swap="outerHTML">
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

        <button type="submit" class="btn btn-primary">Save</button>
    </form>

Modal Form Example
==================

Create a modal form that closes automatically on success:

.. code-block:: html

    <!-- Base template with modal -->
    {% load django_htmx_plus %}

    <div class="modal fade" data-htmx-plus-modal="article-form">
        <div class="modal-dialog">
            <div id="article-form" class="modal-content">
                <!-- Form content swapped here -->
            </div>
        </div>
    </div>

    <!-- Trigger button -->
    <button class="btn btn-primary" hx-get="{% url 'article-form' %}" hx-target="#article-form">
        New Article
    </button>

The form template is the same, but when submitted successfully:

1. The form is saved
2. An empty ``HtmxResponse()`` is returned
3. HTMX swaps with an empty response
4. ``django-htmx-plus.js`` detects empty response and closes the modal

Multiple Triggers
=================

Fire multiple events on success to trigger updates in different parts of your page:

.. code-block:: python

    class ArticleCreateView(HtmxFormResponseMixin, CreateView):
        model = Article
        form_class = ArticleForm
        template_name = "article/form.html"

        valid_triggers = ["articleCreated", "listRefresh", "statsUpdated"]
        success_message = "Article created successfully."

Each trigger can be listened to independently:

.. code-block:: html

    <!-- List refreshes when article is created -->
    <div id="article-list" hx-trigger="articleCreated from:body">

    <!-- Stats update -->
    <div id="stats" hx-trigger="statsUpdated from:body" hx-get="/stats/">

    <!-- New articles appear -->
    <div id="recent" hx-trigger="listRefresh from:body" hx-get="/recent/">

Update View Example
===================

Use ``HtmxFormResponseMixin`` with ``UpdateView`` for in-place editing:

.. code-block:: python

    from django.views.generic.edit import UpdateView
    from django_htmx_plus.mixins import HtmxFormResponseMixin

    class ArticleUpdateView(HtmxFormResponseMixin, UpdateView):
        model = Article
        form_class = ArticleForm
        template_name = "article/form.html"

        valid_triggers = ["articleUpdated"]
        success_message = "Article updated."

        def get_object(self):
            return Article.objects.get(pk=self.kwargs["pk"])

Inline Editing Pattern
~~~~~~~~~~~~~~~~~~~~~~

Show edit form inline when a row is clicked:

.. code-block:: html

    <!-- article/list.html -->
    <table class="table">
        <tbody>
            {% for article in articles %}
                <tr id="article-{{ article.id }}" hx-trigger="articleUpdated from:body">
                    <td>
                        <a href="#" hx-get="{% url 'article-edit' article.id %}" hx-target="this" hx-swap="outerHTML">
                            Edit
                        </a>
                    </td>
                    <td>{{ article.title }}</td>
                    <td>{{ article.status }}</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>

Clicking "Edit" swaps the row for the form. On successful submission, the row updates automatically.

Validation Errors
=================

When the form has validation errors, the mixin re-renders the form with errors (not an HTMX response):

.. code-block:: html

    <!-- User submits with missing required field -->
    <!-- Form is re-rendered in place with error messages -->
    <form hx-post="...">
        ...
        <div class="invalid-feedback d-block">
            This field is required.
        </div>
    </form>

The user can correct and resubmit immediately without page reload.

Custom Success Handling
=======================

If you need custom logic on success, override ``form_valid()``:

.. code-block:: python

    class ArticleCreateView(HtmxFormResponseMixin, CreateView):
        model = Article
        form_class = ArticleForm
        template_name = "article/form.html"

        valid_triggers = ["articleCreated"]

        def form_valid(self, form):
            # Custom logic before save
            form.instance.author = self.request.user
            response = super().form_valid(form)

            # Custom logic after save
            notify_followers.delay(self.object.id)

            return response

The mixin handles the response creation, so just do your custom work and call ``super()``.

Best Practices
==============

1. **Use ``hx-target="this"`` for inline forms** – updates the form element itself
2. **Use ``hx-target="#modal-id"`` for modal forms** – targets the modal body
3. **Set appropriate triggers** – helps other parts of page know about changes
4. **Always include success messages** – users need feedback
5. **Test validation errors** – ensure form re-renders with errors correctly
6. **Use `django-cotton` forms** – for consistent styling with your Bootstrap theme
7. **Preserve CSRF token** – always include ``{% csrf_token %}`` in forms
