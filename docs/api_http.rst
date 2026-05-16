====
HTTP
====

The ``django_htmx_plus.http`` module provides custom HTTP response classes for HTMX applications.

HtmxResponse
============

.. code-block:: python

    from django_htmx_plus.http import HtmxResponse

    class HtmxResponse(HttpResponse):
        """A 204 No Content response with HX-Trigger headers."""
        
        def __init__(self, triggers: List[str] | str | None = None, **kwargs):
            """
            Initialize an HtmxResponse.
            
            Args:
                triggers: A string or list of HTMX event names to trigger on the client
                **kwargs: Additional arguments passed to HttpResponse
            """

Returns a 204 No Content response with ``HX-Trigger`` header set to the provided event names. Useful for background operations that don't need to update the DOM.

Example:

.. code-block:: python

    def my_view(request):
        # Do some background work
        process_data.delay(request.user.id)
        return HtmxResponse(triggers=["dataProcessed", "statsRefreshed"])

HtmxRedirectResponse
====================

.. code-block:: python

    from django_htmx_plus.http import HtmxRedirectResponse

    class HtmxRedirectResponse(HttpResponse):
        """A response that sends an HX-Redirect header."""
        
        def __init__(self, destination: str, **kwargs):
            """
            Initialize an HtmxRedirectResponse.
            
            Args:
                destination: The URL to redirect to
                **kwargs: Additional arguments passed to HttpResponse
            """

Instructs HTMX to navigate the browser to a new URL without a traditional HTTP redirect.

Example:

.. code-block:: python

    def my_view(request):
        obj = MyModel.objects.create(name=request.POST.get("name"))
        return HtmxRedirectResponse(destination=obj.get_absolute_url())

Both responses automatically handle HTMX request detection and work seamlessly with the rest of django-htmx-plus.
