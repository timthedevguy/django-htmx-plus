"""Tests for django_htmx_plus.http"""
from django.test import TestCase
from django_htmx_plus.http import HtmxResponse, HtmxRedirectResponse


class TestHtmxResponse(TestCase):
    def test_status_code_is_204(self):
        response = HtmxResponse(["refresh"])
        self.assertEqual(response.status_code, 204)

    def test_single_trigger_in_header(self):
        response = HtmxResponse(["refresh"])
        self.assertEqual(response.headers["HX-Trigger"], "refresh")

    def test_multiple_triggers_comma_joined(self):
        response = HtmxResponse(["refresh", "closeModal", "showAlert"])
        self.assertEqual(response.headers["HX-Trigger"], "refresh,closeModal,showAlert")

    def test_empty_triggers_list(self):
        response = HtmxResponse([])
        self.assertEqual(response.headers["HX-Trigger"], "")


class TestHtmxRedirectResponse(TestCase):
    def test_hx_redirect_header_set(self):
        response = HtmxRedirectResponse("/dashboard/")
        self.assertEqual(response.headers["HX-Redirect"], "/dashboard/")

    def test_default_status_code_is_200(self):
        response = HtmxRedirectResponse("/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_absolute_url(self):
        response = HtmxRedirectResponse("https://example.com/page/")
        self.assertEqual(response.headers["HX-Redirect"], "https://example.com/page/")


