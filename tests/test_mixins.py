"""Tests for django_htmx_plus.mixins"""
from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.cookie import CookieStorage
from unittest.mock import MagicMock, patch
from django_htmx_plus.mixins import HtmxFormResponseMixin
from django_htmx_plus.http import HtmxResponse


class _MockForm:
    def save(self):
        pass


class _MockView(HtmxFormResponseMixin):
    valid_triggers = ["personAdded"]
    success_message = ""

    def __init__(self, request):
        self.request = request


class TestHtmxFormResponseMixin(TestCase):
    def setUp(self):
        factory = RequestFactory()
        request = factory.post("/")
        request._messages = CookieStorage(request)
        self.view = _MockView(request)

    def test_form_valid_returns_htmx_response(self):
        response = self.view.form_valid(_MockForm())
        self.assertIsInstance(response, HtmxResponse)

    def test_form_valid_response_is_204(self):
        response = self.view.form_valid(_MockForm())
        self.assertEqual(response.status_code, 204)

    def test_form_valid_hx_trigger_header(self):
        response = self.view.form_valid(_MockForm())
        self.assertEqual(response.headers["HX-Trigger"], "personAdded")

    def test_form_valid_multiple_triggers(self):
        self.view.valid_triggers = ["personAdded", "refreshStats"]
        response = self.view.form_valid(_MockForm())
        self.assertEqual(response.headers["HX-Trigger"], "personAdded,refreshStats")

    def test_form_valid_calls_form_save(self):
        form = MagicMock()
        self.view.form_valid(form)
        form.save.assert_called_once()

    def test_success_message_added_when_set(self):
        self.view.success_message = "Saved successfully!"
        with patch("django_htmx_plus.mixins.messages") as mock_messages:
            self.view.form_valid(_MockForm())
            mock_messages.success.assert_called_once_with(self.view.request, "Saved successfully!")

    def test_no_message_when_success_message_empty(self):
        self.view.success_message = ""
        with patch("django_htmx_plus.mixins.messages") as mock_messages:
            self.view.form_valid(_MockForm())
            mock_messages.success.assert_not_called()

