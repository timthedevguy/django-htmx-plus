=================
Working with Responses
=================

This guide covers using the HTMX response classes for different scenarios.

HtmxResponse for Background Tasks
==================================

Use ``HtmxResponse`` when you need to signal that an operation is complete without updating the DOM:

.. code-block:: python

    from django_htmx_plus.http import HtmxResponse
    from myapp.tasks import process_data

    def start_processing(request):
        # Start a background task
        task = process_data.delay(request.user.id)

        # Signal completion to client without updating DOM
        return HtmxResponse(triggers=["processingStarted"])

Your HTMX element can listen for the event:

.. code-block:: html

    <button hx-post="/start-processing/" hx-trigger="click" hx-on::processingStarted="alert('Processing started!')">
        Start Processing
    </button>

Multiple Triggers
=================

Trigger multiple HTMX events in a single response:

.. code-block:: python

    def save_and_refresh(request):
        article = Article.objects.get(pk=request.POST.get("id"))
        article.title = request.POST.get("title")
        article.save()

        return HtmxResponse(triggers=["articleUpdated", "statsRefreshed", "cacheCleared"])

All three events are fired on the client side, allowing different elements to react independently:

.. code-block:: html

    <!-- Table row re-fetches itself -->
    <tr hx-trigger="articleUpdated from:body">

    <!-- Stats panel refreshes -->
    <div hx-trigger="statsRefreshed from:body" hx-get="/stats/">
        <!-- Updated stats -->
    </div>

    <!-- Cache is invalidated -->
    <div hx-trigger="cacheCleared from:body">
        Cache cleared
    </div>

Single Trigger as String
========================

Pass a single trigger as a string instead of a list:

.. code-block:: python

    return HtmxResponse(triggers="articleDeleted")

Both formats work identically – use whichever is more convenient for your code.

HtmxRedirectResponse for Navigation
===================================

Use ``HtmxRedirectResponse`` to navigate to a new URL after an operation:

.. code-block:: python

    from django_htmx_plus.http import HtmxRedirectResponse

    def create_article(request):
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            return HtmxRedirectResponse(destination=article.get_absolute_url())
        # Re-render form with errors if invalid
        return render(request, "article/form.html", {"form": form})

After the response, HTMX will navigate the browser to ``/articles/1/`` without a full page reload.

Combining with Messages
=======================

Use ``HtmxResponse`` with Django messages through ``HtmxMessagesMiddleware``:

.. code-block:: python

    from django.contrib import messages
    from django_htmx_plus.http import HtmxResponse

    def delete_article(request, pk):
        article = Article.objects.get(pk=pk)
        article.delete()

        messages.success(request, f"Article '{article.title}' deleted.")
        return HtmxResponse(triggers=["articleDeleted"])

The middleware automatically merges the message into the ``HX-Trigger`` header, and your JavaScript listens for both:

.. code-block:: javascript

    document.body.addEventListener("articleDeleted", (event) => {
        // Custom deletion handling
        console.log("Article deleted");
    });

    document.body.addEventListener("messages", (event) => {
        // Display message toast
        event.detail.value.forEach(({message, tags}) => {
            showToast(message, tags);
        });
    });

Best Practices
==============

1. **Use trigger names that describe what happened** – e.g., ``articleCreated`` instead of ``refreshUI``
2. **Combine HtmxResponse with form rendering for validation errors** – only return HtmxResponse on success
3. **Use specific triggers to allow fine-grained DOM updates** – multiple specific triggers instead of one generic refresh
4. **Document your triggers** – keep a list of events your application fires
5. **Consider event naming conventions** – use past tense for actions (``articleCreated``, ``dataSaved``)
