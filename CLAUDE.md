# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`django-htmx-plus` is a small Django utility library (works alongside [django-cotton](https://github.com/wrabit/django-cotton)) providing HTMX-aware responses, middleware, mixins, a `ListView` subclass with URL-driven filtering/sorting/pagination, and matching Cotton components for Bootstrap 5 tables. It is published to PyPI, versioned via `poetry-dynamic-versioning` from git tags (no manual version bumps in `pyproject.toml`).

## Commands

Managed with Poetry; a `.venv` already exists in the repo root.

```bash
poetry install              # install deps (or use .venv directly)
poetry run tests            # run the full test suite (tests/run_tests.py -> tests/)
poetry run docs             # sphinx-autobuild docs/ -> build/, live-reloading docs server
```

Running a single test file/case (the test runner is Django's `DiscoverRunner`, invoked manually rather than via `manage.py`):

```bash
python -c "import os,django; os.environ['DJANGO_SETTINGS_MODULE']='tests.settings'; django.setup(); from django.test.utils import get_runner; from django.conf import settings; get_runner(settings)().run_tests(['tests.test_views.SomeTestCase'])"
```

or simply point Django's test runner at a dotted path once `DJANGO_SETTINGS_MODULE=tests.settings` is exported:

```bash
$env:DJANGO_SETTINGS_MODULE="tests.settings"   # PowerShell
python -m django test tests.test_views.SomeTestCase.test_something
```

**Note:** In this dev environment `poetry run tests` fails with `No module named 'jinja2'` — poetry resolves to a different Python than the project's `.venv` (which does have `jinja2`/`Django` installed). If that happens, bypass poetry and invoke the runner via the venv's Python directly:

```bash
.venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'scripts'); import run_tests; run_tests.main()"
```

(`scripts/run_tests.py`'s `main()` isn't called at module level — it's only wired up as the `tests` Poetry entry point — so it must be imported and called explicitly like above rather than run as a script.)

There is no dedicated lint/format command wired into Poetry scripts, but `black`, `pylint`, and `ruff` are configured in `pyproject.toml` (line length 120, `py311` target) and are dev dependencies — run them directly (`black .`, `pylint django_htmx_plus`, `ruff check .`) if asked to lint/format.

Test settings live at [tests/settings.py](tests/settings.py) — a minimal Django project with only `contenttypes`, `auth`, `messages`, `sessions`, and `django_htmx_plus` installed, SQLite in-memory DB, and `HtmxMessagesMiddleware` wired in.

## Architecture

The package has two halves that are meant to be used together but are independently testable:

**Python side** (`django_htmx_plus/`):
- [http.py](django_htmx_plus/http.py) — `HtmxResponse` (204 + `HX-Trigger` header) and `HtmxRedirectResponse` (`HX-Redirect` header). These are the primitives everything else builds on.
- [middleware.py](django_htmx_plus/middleware.py) — `HtmxMessagesMiddleware` inspects `HX-Request` header, pulls pending Django `messages`, and merges them into the response's `HX-Trigger` header under a `messages` key. It has to handle three cases for an existing `HX-Trigger`: absent, string syntax (`"a,b"`), or JSON object syntax — merging without clobbering.
- [mixins.py](django_htmx_plus/mixins.py) — `HtmxFormResponseMixin` for `FormView`/`CreateView`: on `form_valid`, saves the form, optionally queues a success message, and returns an `HtmxResponse` with `valid_triggers` instead of a redirect.
- [views.py](django_htmx_plus/views.py) — `HtmxListView` is the core piece. It parses `field.filter_type=value` query params (via `utils.build_filter_dict`) into ORM filter kwargs, parses `order_by`, and builds pagination context (elided page range). Security-relevant detail: `fields` acts as an allowlist for both filtering and ordering — `_is_order_by_allowed` and `build_filter_dict` both explicitly reject field names containing `__` to block relation traversal past the allowlist. There is no wildcard/bypass value — every field must be listed explicitly (secure by default).
- [types.py](django_htmx_plus/types.py) — `Filter` `StrEnum` mapping URL filter suffixes (`eq`, `ieq`, `gt`, `like`, `in`, `nl`, `rng`, `sch`, etc.) to Django ORM lookup names. Adding a new filter suffix means adding a member here and it's automatically picked up by `build_filter_dict`.
- [utils.py](django_htmx_plus/utils.py) — pure functions used by `HtmxListView`: `build_filter_dict`, `build_query_str` (preserves only `field.filter` params across pagination/sort links), `build_filters_template_dict` (strips ORM lookup suffixes for template display).
- [templatetags/django_htmx_plus.py](django_htmx_plus/templatetags/django_htmx_plus.py) — `{% htmx_plus_script %}` tag renders the static JS module include, forwarding a CSP `nonce` from context if present.
- [templatetags/cotton_extras.py](django_htmx_plus/templatetags/cotton_extras.py) — `get_attr` / `get_key_value` filters, needed because Cotton templates can't do `item[field]` dynamic lookups natively.

**Template/JS side**:
- [templates/cotton/tables/](django_htmx_plus/templates/cotton/tables/) — `htmx_table` (full table), `header_cell` (sortable `<th>` that toggles `order_by=field` / `-field` via `hx-get`), `pager` (Bootstrap pagination wired to `hx-get`). These consume the context dict built by `HtmxListView.get_context_data` (`fields`, `object_list`, `order_by`, `path`, `filter_query`, `hx_target_id`, `page_obj`, `paginator`) — the view and templates are tightly coupled through this contract, so changing context keys in `views.py` requires updating the templates too.
- [templates/cotton/icons/](django_htmx_plus/templates/cotton/icons/) — chevron icon components used by `header_cell` and `pager`.
- [static/django_htmx_plus/django-htmx-plus.js](django_htmx_plus/static/django_htmx_plus/django-htmx-plus.js) — ES module wiring Bootstrap 5 `Modal`/`Offcanvas` show/hide to HTMX swap events via `data-htmx-plus-modal`/`data-htmx-plus-offcanvas` attributes. Reads `window.bootstrap.Modal`/`window.bootstrap.Offcanvas`, so consumers just need Bootstrap 5's regular JS bundle loaded (no import map or bundler needed).

## Key conventions

- The `fields` allowlist pattern (view attribute restricting which model fields can be filtered/sorted from the URL) is the main security boundary in this codebase — any change touching filtering or ordering in `views.py` or `utils.py` should preserve the `__` traversal block and the allowlist check. There is no wildcard/bypass value (no `"__all__"`) — every field a view needs must be listed explicitly, secure by default. Always read `fields` through `HtmxListView.get_fields()` rather than `self.fields` directly — it mutates in `"pk"` on first call so rows stay uniquely identifiable even when a subclass doesn't list `pk` explicitly. The `htmx_table` template hides the `pk` column unless `show_pk` is truthy in the context.
- `HtmxListView.get_queryset()` always returns a `.values(*fields)` queryset (dicts) rather than model instances — templates therefore use `get_key_value` instead of attribute access, and `get_transform_data` is the override point for views that need to post-process rows before rendering.
- Docs are written in reST under `docs/` and built with Sphinx (`shibuya` theme) into `build/` — `build/` and `dist/` are generated output, not hand-edited.
