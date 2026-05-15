"""Tests for django_htmx_plus.middleware"""
import json
from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.cookie import CookieStorage
from django.contrib.messages import constants as msg_constants
from django.http import HttpResponse
from django_htmx_plus.middleware import HtmxMessagesMiddleware


def _make_response(status=200, hx_trigger=None):
    resp = HttpResponse(status=status)
    if hx_trigger is not None:
        resp.headers["HX-Trigger"] = hx_trigger
    return resp


def _add_message(request, message, level=msg_constants.SUCCESS, tags="success"):
    storage = request._messages
    storage.add(level, message, tags)


class TestHtmxMessagesMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = HtmxMessagesMiddleware(get_response=lambda r: _make_response())

    def _make_htmx_request(self, path="/"):
        request = self.factory.get(path, HTTP_HX_REQUEST="true")
        request._messages = CookieStorage(request)
        return request

    def _make_plain_request(self, path="/"):
        request = self.factory.get(path)
        request._messages = CookieStorage(request)
        return request

    # --- Non-HTMX requests ---

    def test_non_htmx_request_passes_through_unchanged(self):
        request = self._make_plain_request()
        _add_message(request, "Hello")
        response = _make_response()
        middleware = HtmxMessagesMiddleware(get_response=lambda r: response)
        result = middleware(request)
        self.assertNotIn("HX-Trigger", result.headers)

    # --- Redirect responses ---

    def test_redirect_response_passes_through_unchanged(self):
        request = self._make_htmx_request()
        _add_message(request, "Redirected")
        response = _make_response(status=302)
        middleware = HtmxMessagesMiddleware(get_response=lambda r: response)
        result = middleware(request)
        self.assertNotIn("HX-Trigger", result.headers)

    # --- No messages ---

    def test_htmx_request_with_no_messages_leaves_hx_trigger_alone(self):
        request = self._make_htmx_request()
        response = _make_response(hx_trigger="refresh")
        middleware = HtmxMessagesMiddleware(get_response=lambda r: response)
        result = middleware(request)
        self.assertEqual(result.headers["HX-Trigger"], "refresh")

    # --- Messages are embedded ---

    def test_messages_added_to_hx_trigger_when_no_existing_trigger(self):
        request = self._make_htmx_request()
        _add_message(request, "Saved!", level=msg_constants.SUCCESS, tags="success")
        response = _make_response()
        middleware = HtmxMessagesMiddleware(get_response=lambda r: response)
        result = middleware(request)
        data = json.loads(result.headers["HX-Trigger"])
        self.assertIn("messages", data)
        self.assertEqual(data["messages"][0]["message"], "Saved!")
        self.assertIn("success", data["messages"][0]["tags"])

    def test_messages_merged_with_existing_object_trigger(self):
        request = self._make_htmx_request()
        _add_message(request, "Done")
        response = _make_response(hx_trigger=json.dumps({"refresh": True}))
        middleware = HtmxMessagesMiddleware(get_response=lambda r: response)
        result = middleware(request)
        data = json.loads(result.headers["HX-Trigger"])
        self.assertIn("refresh", data)
        self.assertIn("messages", data)

    def test_messages_merged_with_existing_string_trigger(self):
        request = self._make_htmx_request()
        _add_message(request, "Done")
        response = _make_response(hx_trigger="refresh,closeModal")
        middleware = HtmxMessagesMiddleware(get_response=lambda r: response)
        result = middleware(request)
        data = json.loads(result.headers["HX-Trigger"])
        self.assertIn("refresh", data)
        self.assertIn("closeModal", data)
        self.assertIn("messages", data)

    def test_multiple_messages_all_included(self):
        request = self._make_htmx_request()
        _add_message(request, "First", level=msg_constants.SUCCESS, tags="success")
        _add_message(request, "Second", level=msg_constants.ERROR, tags="error")
        response = _make_response()
        middleware = HtmxMessagesMiddleware(get_response=lambda r: response)
        result = middleware(request)
        data = json.loads(result.headers["HX-Trigger"])
        self.assertEqual(len(data["messages"]), 2)


