from django_htmx_plus.http import HtmxResponse
from django.contrib import messages
from typing import List


class HtmxFormResponseMixin:
    """A mixin that provides a trigger-aware HTMX response for successful form submissions.

    Mix this class into any ``FormView`` or ``CreateView`` subclass to replace the
    default redirect response with an :class:`~django_htmx_plus.http.HtmxResponse`
    that carries one or more ``HX-Trigger`` events, allowing the page to react
    without a full navigation.

    Attributes:
        valid_triggers (List[str]): Event names included in the ``HX-Trigger`` header
            of the response returned after a successful form submission.
    """

    valid_triggers: List[str] = []
    success_message: str = ''

    def form_valid(self, form):
        """Save the form and return a trigger-aware HTMX response.

        Calls ``form.save()`` and then returns an :class:`~django_htmx_plus.http.HtmxResponse`
        that sends all events listed in :attr:`valid_triggers` via the ``HX-Trigger``
        response header, prompting any listening HTMX elements to refresh.

        Args:
            form (forms.ModelForm): A bound and validated Django form instance.

        Returns:
            HtmxResponse: A 204 response containing the ``HX-Trigger`` header populated
            with the events defined in :attr:`valid_triggers`.
        """
        form.save()

        if self.success_message:
            messages.success(self.request, self.success_message)

        return HtmxResponse(self.valid_triggers)