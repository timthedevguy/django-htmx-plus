==========
JavaScript
==========

The ``django-htmx-plus.js`` ES module provides client-side integration between HTMX and Bootstrap 5 modals/offcanvases.

Overview
========

The JavaScript module automatically handles opening and closing Bootstrap 5 modals and offcanvases when HTMX swaps content. This eliminates the need for manual JavaScript coordination between HTMX and Bootstrap components.

Features
~~~~~~~~

- Auto-show modals when HTMX swaps content
- Auto-hide modals on empty responses
- Auto-reset modal body when closed
- Full support for Bootstrap 5 Modals and Offcanvases
- Content Security Policy (CSP) nonce support

Installation
============

Add the template tag to your base template, after Bootstrap JS:

.. code-block:: html

    {% load django_htmx_plus %}

    <!-- After Bootstrap JS -->
    {% htmx_plus_script %}

This renders:

.. code-block:: html

    <script src="/static/django_htmx_plus/django-htmx-plus.js" type="module"></script>

With optional CSP nonce if present in template context:

.. code-block:: html

    <script src="/static/django_htmx_plus/django-htmx-plus.js" type="module" nonce="..."></script>

Requirements
~~~~~~~~~~~~

- Bootstrap 5 available as an ES module
- HTMX library loaded before the script
- Either an import map or bundler that provides Bootstrap as an ES module

Setup with Import Map
~~~~~~~~~~~~~~~~~~~~~~~

If loading Bootstrap as a global script, use an import map to make it available as an ES module:

.. code-block:: html

    <script type="importmap">
    {
      "imports": {
        "@popperjs/core": "{% static '@popperjs/core/dist/esm/index.js' %}",
        "bootstrap": "{% static 'bootstrap/js/index.esm.js' %}",
      }
    }
    </script>

    {% htmx_plus_script %}

Setup with Bundler
~~~~~~~~~~~~~~~~~~~

If using a bundler (Webpack, Vite, etc.), ensure Bootstrap is installed as an npm package and the bundler resolves the import correctly.

Modal Configuration
===================

Mark Modal Elements
~~~~~~~~~~~~~~~~~~~

Add ``data-htmx-plus-modal="<target_id>"`` to the modal root element, where ``target_id`` is the ID of the element that will be swapped:

.. code-block:: html

    <!-- Bootstrap Modal -->
    <div class="modal modal-blur fade" id="modal" data-htmx-plus-modal="dialog" tabindex="-1" style="display: none;" aria-hidden="true">
		<div id="dialog" class="modal-dialog modal-dialog-scrollable htmx-plus-modal" role="document" hx-target="this"></div>
	</div>

Create HTMX Triggers
~~~~~~~~~~~~~~~~~~~~

Point HTMX elements at the matching target ID:

.. code-block:: html

    <button class="btn btn-primary" hx-get="/person/add/" hx-target="#dialog">
        Add Person
    </button>

Behavior
~~~~~~~~

========================================================================== =====================================
Event                                                                      Behavior
========================================================================== =====================================
HTMX swaps non-empty content into ``#dialog``                             Modal is automatically shown
Server returns empty 200 or ``HtmxResponse()``                            Modal is automatically hidden
User clicks modal close button                                            Modal body is cleared
========================================================================== =====================================

Example Modal Template
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    <!-- form.html - rendered by hx-get="/person/add/" -->
    <form hx-post="{{ request.path }}" class="modal-content">
        <div class="modal-header">
            <h5 class="modal-title">Add Person</h5>
        </div>
        <div class="modal-body">
            {% csrf_token %}
            <div class="alert alert-info">Form validation works as well, try adding an invalid Date of Birth.</div>
            {% form %}
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="submit" class="btn btn-primary">Save</button>
        </div>
    </form>

After submission, the server returns an empty ``HtmxResponse()`` to close the modal.

Offcanvas Configuration
======================

Mark Offcanvas Elements
~~~~~~~~~~~~~~~~~~~~~~~

Add ``data-htmx-plus-offcanvas="<target_id>"`` to the offcanvas root element:

.. code-block:: html

    <!-- Bootstrap Offcanvas -->
    <div class="offcanvas offcanvas-end" tabindex="-1" id="flyout-end" data-htmx-plus-offcanvas="flyout-end" aria-labelledby="flyout-label" aria-modal="true" role="dialog">
	</div>

Create HTMX Triggers
~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    <button class="btn btn-secondary" hx-get="/menu/" hx-target="#flyout">
        Open Menu
    </button>

Behavior is the same as modals – content triggers show, empty response triggers close.

Complete Example
================

.. code-block:: html
   :caption: Test.py

    {% extends "base.html" %}
    {% load django_htmx_plus %}

    {% block modal %}
    <div class="modal fade" data-htmx-plus-modal="form-dialog">
        <div class="modal-dialog">
            <div id="form-dialog" class="modal-content">
                <!-- Form content swapped here -->
            </div>
        </div>
    </div>
    {% endblock %}

    {% block content %}
    <div class="container mt-4">
        <button hx-get="{% url 'person-form' %}" hx-target="#form-dialog" class="btn btn-primary">
            Add Person
        </button>
    </div>
    {% endblock %}

    {% block script %}
    {% htmx_plus_script %}
    {% endblock %}

Django View
~~~~~~~~~~~

.. code-block:: python

    from django.views.generic import TemplateView
    from django_htmx_plus.mixins import HtmxFormResponseMixin
    from django_htmx_plus.http import HtmxResponse

    class PersonFormView(HtmxFormResponseMixin, CreateView):
        model = Person
        form_class = PersonForm
        template_name = "person/form.html"
        valid_triggers = ["personCreated"]
        success_message = "Person added successfully."

After form submission, the view returns ``HtmxResponse(triggers=["personCreated"])`` which:

1. The modal is automatically closed
2. The ``personCreated`` event is fired
3. Any listeners on ``personCreated`` are triggered

CSP Nonce Support
=================

If using Content Security Policy, pass a ``nonce`` variable in your template context:

.. code-block:: python

    context = {
        "nonce": generate_nonce(),  # Your nonce generation function
    }

The template tag automatically includes the nonce in the script tag:

.. code-block:: html

    <script src="..." type="module" nonce="your-nonce-value"></script>
