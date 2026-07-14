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

- Bootstrap 5 JS loaded before the script, exposing a global ``window.bootstrap``
- HTMX library loaded before the script

Setup
~~~~~

Load Bootstrap's regular (non-module) bundle, which attaches ``bootstrap`` to
``window`` automatically, then include the script tag:

.. code-block:: html

    <script src="{% static 'bootstrap/js/bootstrap.bundle.min.js' %}"></script>
    {% htmx_plus_script %}

No import map or bundler is required — the script reads ``window.bootstrap.Modal``
and ``window.bootstrap.Offcanvas`` directly.

Modal Configuration
===================

Mark Modal Elements
~~~~~~~~~~~~~~~~~~~

Add ``data-htmx-plus-modal="<target_id>"`` to the modal root element, where ``target_id`` is the ID of the element that will be swapped, this is also the ID that you will use in ``hx-target`` to show content in the dialog.

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

.. note::
   Please note that the ``hx-target`` should point to the element with the ID specified in ``data-htmx-plus-modal``, and should include the '#' (required by HTMX)

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

    <button class="btn btn-secondary" hx-get="/menu/" hx-target="#flyout-end">
        Open Menu
    </button>

Behavior is the same as modals – content triggers show, empty response triggers close.

Page-Size Selector History
===========================

``<c-tables.htmx_table />``'s "Show N entries" selector (see :doc:`../guide/list_views`)
carries a ``data-htmx-plus-push-url`` attribute instead of a static ``hx-push-url``,
since the chosen page size isn't known until the user picks it client-side. On a
successful request from an element with this attribute, the script appends the
element's current ``value`` and calls ``history.pushState`` directly:

.. code-block:: html

    <select name="paginate_by" data-htmx-plus-push-url="?page=1&amp;paginate_by=">

This only fires for elements you mark with ``data-htmx-plus-push-url`` — it has no
effect on ``header_cell``/``pager``, which push a complete URL themselves via a
normal ``hx-push-url`` attribute.

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
