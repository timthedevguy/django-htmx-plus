from typing import List

from django.http import HttpResponse


class HtmxResponse(HttpResponse):
    """An HTTP 204 response that carries HTMX trigger events.

    Returns a ``204 No Content`` status and populates the ``HX-Trigger``
    response header with one or more comma-separated event names, causing
    HTMX to fire those events on the client and trigger any listening elements
    to refresh without a full page reload.
    """

    def __init__(self, triggers: List[str], *args, **kwargs):
        """Initialise the response with the given trigger event names.

        Args:
            triggers (List[str]): Event names to include in the ``HX-Trigger``
                response header.
            *args: Additional positional arguments forwarded to ``HttpResponse``.
            **kwargs: Additional keyword arguments forwarded to ``HttpResponse``.
        """
        super(HtmxResponse, self).__init__(*args, **kwargs)
        self.status_code = 204
        self.headers["HX-Trigger"] = ",".join(triggers)


class HtmxRedirectResponse(HttpResponse):
    """An HTTP response that instructs HTMX to perform a client-side redirect.

    Populates the ``HX-Redirect`` response header with the supplied destination
    URL, causing HTMX to navigate the browser to that URL without a traditional
    HTTP redirect status code.
    """

    def __init__(self, destination: str, *args, **kwargs):
        """Initialise the response with the redirect destination URL.

        Args:
            destination (str): The URL to redirect the client to via the
                ``HX-Redirect`` response header.
            *args: Additional positional arguments forwarded to ``HttpResponse``.
            **kwargs: Additional keyword arguments forwarded to ``HttpResponse``.
        """
        super(HtmxRedirectResponse, self).__init__(*args, **kwargs)
        self.headers["HX-Redirect"] = destination
