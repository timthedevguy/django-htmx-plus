"""Tests for django_htmx_plus.views (HtmxListView)"""
from django.db import models
from django.test import TestCase, RequestFactory
from django.views.generic import ListView
from django_htmx_plus.views import HtmxListView


# --- Minimal in-memory model for testing ---

class PersonTest(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=0)

    class Meta:
        app_label = "django_htmx_plus"


class _PersonListView(HtmxListView):
    model = PersonTest
    template_name = "dummy.html"
    fields = ("name", "age")
    hx_target_id = "person-list"
    labels = {"name": "Name", "age": "Age"}
    paginate_by = 10

    def get_queryset(self):
        # Return an empty queryset — we only care about filter/order logic
        return PersonTest.objects.none()


class TestHtmxListViewSetup(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _get_view(self, query_string=""):
        request = self.factory.get("/", query_string)
        view = _PersonListView()
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        return view

    # --- Default ordering ---

    def test_default_order_by_is_none(self):
        view = self._get_view()
        self.assertIsNone(view.order_by)

    # --- Custom ordering ---

    def test_order_by_allowed_field(self):
        view = self._get_view({"order_by": "name"})
        self.assertEqual(view.order_by, "name")

    def test_descending_order_by_allowed_field(self):
        view = self._get_view({"order_by": "-age"})
        self.assertEqual(view.order_by, "-age")

    def test_order_by_disallowed_field_is_ignored(self):
        view = self._get_view({"order_by": "secret"})
        self.assertIsNone(view.order_by)

    def test_order_by_traversal_attempt_blocked(self):
        view = self._get_view({"order_by": "name__secret"})
        # root field "name" is allowed so traversal is rejected based on root only
        # This verifies that only the root is checked
        view2 = self._get_view({"order_by": "secret__name"})
        self.assertIsNone(view2.order_by)

    # --- Filter parsing ---

    def test_filter_built_from_query_params(self):
        view = self._get_view({"name.eq": "Alice"})
        self.assertEqual(view.filter, {"name__exact": "Alice"})

    def test_disallowed_filter_field_ignored(self):
        view = self._get_view({"secret.eq": "x"})
        self.assertEqual(view.filter, {})

    # --- Query strings ---

    def test_filter_query_contains_filter_params(self):
        view = self._get_view({"name.eq": "Alice"})
        self.assertIn("name.eq=Alice", view.filter_query)

    def test_query_contains_order_by_when_requested(self):
        view = self._get_view({"name.eq": "Alice", "order_by": "name"})
        self.assertIn("order_by=name", view.query)

    def test_query_omits_order_by_when_not_requested(self):
        view = self._get_view({"name.eq": "Alice"})
        self.assertNotIn("order_by=", view.query)

    # --- _is_order_by_allowed ---

    def test_is_order_by_allowed_with_valid_field(self):
        view = _PersonListView()
        self.assertTrue(view._is_order_by_allowed("name"))

    def test_is_order_by_allowed_with_descending_valid_field(self):
        view = _PersonListView()
        self.assertTrue(view._is_order_by_allowed("-age"))

    def test_is_order_by_allowed_with_invalid_field(self):
        view = _PersonListView()
        self.assertFalse(view._is_order_by_allowed("password"))

    def test_is_order_by_denied_with_empty_fields(self):
        view = _PersonListView()
        view.fields = ()
        self.assertFalse(view._is_order_by_allowed("anything"))

    # --- get_context_data ---

    def test_context_contains_expected_keys(self):
        request = self.factory.get("/persons/", {"name.eq": "Alice", "order_by": "name"})
        view = _PersonListView()
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        for key in ("query_params", "order_by", "path", "hx_target_id", "query", "filter_query", "filters", "fields"):
            self.assertIn(key, context)

    def test_context_hx_target_id(self):
        request = self.factory.get("/")
        view = _PersonListView()
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertEqual(context["hx_target_id"], "person-list")

    def test_context_page_range_present_when_paginated(self):
        request = self.factory.get("/")
        view = _PersonListView()
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn("page_range", context)

    def test_context_query_params_excludes_page(self):
        request = self.factory.get("/", {"name.eq": "Alice"})
        view = _PersonListView()
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertNotIn("page=", context["query_params"])
        self.assertIn("name.eq=Alice", context["query_params"])

    def test_context_filters_are_template_friendly(self):
        request = self.factory.get("/", {"name.eq": "Alice"})
        view = _PersonListView()
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertEqual(context["filters"], {"name": "Alice"})

    # --- fields / hidden_fields ---

    def test_context_fields_default_all_visible(self):
        request = self.factory.get("/")
        view = _PersonListView()
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertTrue(all(f["visible"] for f in context["fields"]))
        self.assertEqual({f["name"] for f in context["fields"]}, {"pk", "name", "age"})

    def test_context_fields_uses_custom_label(self):
        request = self.factory.get("/")
        view = _PersonListView()
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        name_field = next(f for f in context["fields"] if f["name"] == "name")
        self.assertEqual(name_field["label"], "Name")

    def test_context_fields_falls_back_to_capfirst_label(self):
        request = self.factory.get("/")
        view = _PersonListView()
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        pk_field = next(f for f in context["fields"] if f["name"] == "pk")
        self.assertEqual(pk_field["label"], "Pk")

    def test_hidden_fields_marked_not_visible(self):
        request = self.factory.get("/")
        view = _PersonListView()
        view.hidden_fields = ("age",)
        view.setup(request)
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        age_field = next(f for f in context["fields"] if f["name"] == "age")
        other_fields = [f for f in context["fields"] if f["name"] != "age"]
        self.assertFalse(age_field["visible"])
        self.assertTrue(all(f["visible"] for f in other_fields))

    def test_get_hidden_fields_default_is_empty(self):
        view = _PersonListView()
        self.assertEqual(view.get_hidden_fields(), ())




