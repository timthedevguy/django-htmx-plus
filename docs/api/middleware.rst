==========
Middleware
==========

The ``django_htmx_plus.middleware`` module provides middleware for HTMX-specific handling.

HtmxMessagesMiddleware
======================

.. code-block:: python

    from django_htmx_plus.middleware import HtmxMessagesMiddleware

The middleware automatically forwards Django messages to HTMX clients via the ``HX-Trigger`` header.

Installation
~~~~~~~~~~~~

Add to your ``MIDDLEWARE`` setting:

.. code-block:: python

    MIDDLEWARE = [
        # ...
        "django.contrib.messages.middleware.MessageMiddleware"
        "django_htmx_plus.middleware.HtmxMessagesMiddleware", # <-- Add this middleware after MessageMiddleware
    ]

Behavior
~~~~~~~~

When a view adds a Django message during an HTMX request, the middleware automatically:

1. Serializes the messages into JSON format
2. Merges them into the ``HX-Trigger`` response header
3. Preserves any existing triggers set by the view

Example message format in ``HX-Trigger``:

.. code-block:: json

    {
        "messages": [
            {"message": "Record saved.", "tags": "success"},
            {"message": "Warning: Low stock.", "tags": "warning"}
        ],
        "myCustomEvent": true
    }

Usage in Views
~~~~~~~~~~~~~~

Add messages as usual in Django views:

.. code-block:: python

    from django.contrib import messages
    from django_htmx_plus.http import HtmxResponse

    def save_item(request):
        item = Item.objects.create(name=request.POST.get("name"))
        messages.success(request, f"Item '{item.name}' created successfully.")
        return HtmxResponse(triggers=["itemCreated"])

Client-Side Handling
~~~~~~~~~~~~~~~~~~~~

Listen for the ``messages`` event in your JavaScript:

.. code-block:: javascript

    document.body.addEventListener("messages", (event) => {
        event.detail.value.forEach(({message, tags}) => {
            showToast(message, tags);
        });
    });

The middleware works with both string and JSON object ``HX-Trigger`` formats, automatically detecting and merging appropriately.
