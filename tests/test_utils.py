"""Tests for django_htmx_plus.utils"""
from django.test import TestCase
from django_htmx_plus.utils import (
    build_filter_dict,
    build_query_str,
    build_filters_template_dict,
    split_and_strip,
)


class TestBuildFilterDict(TestCase):
    # --- Allowed fields ---

    def test_basic_exact_filter(self):
        result = build_filter_dict({"name.eq": "Alice"}, ("name",))
        self.assertEqual(result, {"name__exact": "Alice"})

    def test_iexact_filter(self):
        result = build_filter_dict({"name.ieq": "alice"}, ("name",))
        self.assertEqual(result, {"name__iexact": "alice"})

    def test_gt_filter_coerces_numeric_string(self):
        result = build_filter_dict({"age.gt": "30"}, ("age",))
        self.assertEqual(result, {"age__gt": 30})

    def test_gte_filter(self):
        result = build_filter_dict({"age.gte": "18"}, ("age",))
        self.assertEqual(result, {"age__gte": 18})

    def test_lt_filter(self):
        result = build_filter_dict({"age.lt": "65"}, ("age",))
        self.assertEqual(result, {"age__lt": 65})

    def test_lte_filter(self):
        result = build_filter_dict({"age.lte": "64"}, ("age",))
        self.assertEqual(result, {"age__lte": 64})

    def test_startswith_filter(self):
        result = build_filter_dict({"name.sw": "Al"}, ("name",))
        self.assertEqual(result, {"name__startswith": "Al"})

    def test_endswith_filter(self):
        result = build_filter_dict({"name.ew": "ice"}, ("name",))
        self.assertEqual(result, {"name__endswith": "ice"})

    def test_isnull_filter(self):
        result = build_filter_dict({"deleted.nl": "True"}, ("deleted",))
        self.assertEqual(result, {"deleted__isnull": True})

    def test_filter_key_without_dot_is_ignored(self):
        result = build_filter_dict({"name": "Alice", "age.gt": "10"}, ("name", "age"))
        self.assertNotIn("name", result)
        self.assertIn("age__gt", result)

    def test_unknown_filter_suffix_is_ignored(self):
        result = build_filter_dict({"name.unknown": "Alice"}, ("name",))
        self.assertEqual(result, {})

    def test_field_not_in_allowed_list_is_ignored(self):
        result = build_filter_dict({"secret.eq": "value"}, ("name",))
        self.assertEqual(result, {})

    def test_traversal_in_field_name_is_blocked(self):
        result = build_filter_dict({"related__secret.eq": "value"}, ("related__secret",))
        self.assertEqual(result, {})

    # --- Unrestricted (all fields) ---

    def test_all_fields_allows_any_field(self):
        result = build_filter_dict({"title.eq": "Hello"}, ("__all__",))
        self.assertEqual(result, {"title__exact": "Hello"})

    def test_none_allowed_fields_allows_any_field(self):
        result = build_filter_dict({"title.eq": "Hello"}, None)
        self.assertEqual(result, {"title__exact": "Hello"})

    def test_empty_tuple_allowed_fields_allows_any_field(self):
        result = build_filter_dict({"title.eq": "Hello"}, ())
        self.assertEqual(result, {"title__exact": "Hello"})

    # --- Multiple filters ---

    def test_multiple_filters_combined(self):
        params = {"name.ieq": "alice", "age.gte": "18"}
        result = build_filter_dict(params, ("name", "age"))
        self.assertEqual(result, {"name__iexact": "alice", "age__gte": 18})

    # --- Case insensitivity of filter suffix ---

    def test_filter_suffix_is_case_insensitive(self):
        result = build_filter_dict({"name.EQ": "Alice"}, ("name",))
        self.assertEqual(result, {"name__exact": "Alice"})


class TestBuildQueryStr(TestCase):
    def test_includes_dot_params(self):
        result = build_query_str({"name.eq": "Alice", "age.gt": "18"})
        self.assertIn("name.eq=Alice", result)
        self.assertIn("age.gt=18", result)

    def test_excludes_plain_params(self):
        result = build_query_str({"order_by": "name", "page": "2"})
        self.assertEqual(result, "")

    def test_mixed_params(self):
        result = build_query_str({"name.eq": "Alice", "order_by": "name"})
        self.assertEqual(result, "name.eq=Alice")

    def test_empty_params(self):
        result = build_query_str({})
        self.assertEqual(result, "")


class TestBuildFiltersTemplateDict(TestCase):
    def test_strips_orm_lookup(self):
        result = build_filters_template_dict({"name__iexact": "Alice"})
        self.assertEqual(result, {"name": "Alice"})

    def test_multiple_fields(self):
        result = build_filters_template_dict({"name__iexact": "Alice", "age__gte": 18})
        self.assertEqual(result, {"name": "Alice", "age": 18})

    def test_empty_dict(self):
        result = build_filters_template_dict({})
        self.assertEqual(result, {})

    def test_related_field_lookup_uses_root_only(self):
        result = build_filters_template_dict({"department__name__iexact": "HR"})
        self.assertEqual(result, {"department": "HR"})


class TestSplitAndStrip(TestCase):
    def test_basic_lines(self):
        result = split_and_strip("  hello  \n  world  ")
        self.assertEqual(result, ["hello", "world"])

    def test_empty_lines_removed(self):
        result = split_and_strip("hello\n\nworld")
        self.assertEqual(result, ["hello", "world"])

    def test_windows_line_endings(self):
        result = split_and_strip("hello\r\nworld")
        self.assertEqual(result, ["hello", "world"])

    def test_non_breaking_spaces_removed(self):
        result = split_and_strip("hello\xa0world")
        self.assertEqual(result, ["helloworld"])

    def test_empty_string(self):
        result = split_and_strip("")
        self.assertEqual(result, [])

    def test_only_whitespace(self):
        result = split_and_strip("   \n   \n   ")
        self.assertEqual(result, [])

