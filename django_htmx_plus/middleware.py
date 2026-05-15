import json
from django.contrib.messages import get_messages


class HtmxMessagesMiddleware:
    """Middleware that forwards Django messages to HTMX via the HX-Trigger header.

    Intercepts HTMX requests and appends any pending Django messages to the
    ``HX-Trigger`` response header as a ``messages`` key, allowing the
    client-side HTMX event system to display them without a full page reload.
    """

    def __init__(self, get_response):
        """Initialize the middleware.

        Args:
            get_response: The next middleware or view in the chain.
        """
        self.get_response = get_response

    def __call__(self, request):
        """Process the request and attach messages to the HX-Trigger header.

        Args:
            request: The incoming HTTP request.

        Returns:
            HttpResponse: The response with the ``HX-Trigger`` header updated
            to include any pending Django messages when the request was made
            by HTMX and the response is not a redirect.
        """
        response = self.get_response(request)

        # The HX-Request header indicates that the request was made with HTMX
        if "HX-Request" not in request.headers:
            return response

        # Ignore redirections because HTMX cannot read the headers
        if 300 <= response.status_code < 400:
            return response

        # Extract the messages
        messages = [{"message": message.message, "tags": message.tags} for message in get_messages(request)]
        if not messages:
            return response

        # Get the existing HX-Trigger that could have been defined by the view
        hx_trigger = response.headers.get("HX-Trigger")

        if hx_trigger is None:
            # If the HX-Trigger is not set, start with an empty object
            hx_trigger = {}
        elif hx_trigger.startswith("{"):
            # If the HX-Trigger uses the object syntax, parse the object
            hx_trigger = json.loads(hx_trigger)
        else:
            # If the HX-Trigger uses the string syntax, convert to the object syntax
            triggers = hx_trigger.split(",")
            hx_trigger = {}
            for trigger in triggers:
                hx_trigger[trigger] = True

        # Add the messages array in the HX-Trigger object
        hx_trigger["messages"] = messages

        # Add or update the HX-Trigger
        response.headers["HX-Trigger"] = json.dumps(hx_trigger)

        return response

