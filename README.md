# django-htmx-plus

A Django utility library that extends [django-htmx](https://github.com/adamchainz/django-htmx) and [django-cotton](https://github.com/wrabit/django-cotton) with ready-made views, mixins, middleware, response helpers, and Cotton components for building HTMX-powered list views with filtering, sorting, and pagination.

This package was created for my own projects but it was handy enough to share, I learned how to use HTMX with Django and Boostrap Modals from the following two posts from [Josh Karamuth](https://www.linkedin.com/in/josh-karamuth/): 
* [How to show a modal in Django + HTMX](https://joshkaramuth.com/blog/django-htmx-modal/)
* [Show Django forms inside a modal using HTMX](https://joshkaramuth.com/blog/django-htmx-modal-forms/)

---

## Features

- **`HtmxResponse`** – a 204 No Content response that fires `HX-Trigger` events on the client.
- **`HtmxRedirectResponse`** – a response that sends an `HX-Redirect` header to navigate the browser.
- **`HtmxMessagesMiddleware`** – automatically forwards Django messages to the client via the `HX-Trigger` header on every HTMX request.
- **`HtmxFormResponseMixin`** – a `FormView`/`CreateView` mixin that replaces the success redirect with an HTMX trigger response.
- **`HtmxListView`** – a `ListView` subclass with built-in URL-based filtering, column sorting, and elided pagination.
- **Filter helpers** – parse `field.filter_type=value` query parameters safely into Django ORM filter dicts.
- **Cotton components** – drop-in table, header cell, and pager components styled for Bootstrap 5.
- **Template filters** – `get_attr` and `get_key_value` for accessing object attributes and dict values in templates.
- **Built-in JavaScript helper** – a `django-htmx-plus.js` ES module that wires Bootstrap 5 Modals and Offcanvases to HTMX swap events, with a `{% htmx_plus_script %}` template tag to include it.

---

## Requirements

- Python 3.11+
- Django (any version compatible with the above)
- [django-htmx](https://github.com/adamchainz/django-htmx) ≥ 1.27
- [django-cotton](https://github.com/wrabit/django-cotton) ≥ 2.6

---

## Installation

```bash
pip install django-htmx-plus
```

Add to `INSTALLED_APPS` and configure middleware in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_htmx",
    "django_cotton",
    "django_htmx_plus",
]

MIDDLEWARE = [
    # ...
    "django_htmx.middleware.HtmxMiddleware",        # required by django-htmx
    "django_htmx_plus.middleware.HtmxMessagesMiddleware",
]
```

---

## Usage

### HtmxResponse

Return a `204 No Content` response that triggers one or more HTMX events on the client:

```python
from django_htmx_plus.http import HtmxResponse

def my_view(request):
    # ... do some work ...
    return HtmxResponse(triggers=["itemUpdated", "refreshStats"])
```

The response sets `HX-Trigger: itemUpdated,refreshStats`, which HTMX picks up to re-fetch any elements listening for those events.

---

### HtmxRedirectResponse

Instruct HTMX to navigate the browser to a new URL without a traditional HTTP redirect:

```python
from django_htmx_plus.http import HtmxRedirectResponse

def my_view(request):
    return HtmxRedirectResponse(destination="/dashboard/")
```

---

### HtmxMessagesMiddleware

Once the middleware is installed, any Django message added during an HTMX request is automatically serialised into the `HX-Trigger` header as a `messages` key:

```json
{
  "messages": [
    {"message": "Record saved.", "tags": "success"}
  ]
}
```

If the view already sets its own `HX-Trigger` header (either string or JSON object syntax), the middleware merges the messages in without overwriting existing triggers.

Listen for the `messages` event in your HTMX setup to display the messages, for example:

```javascript
document.body.addEventListener("messages", (event) => {
    event.detail.value.forEach(({message, tags}) => {
        showToast(message, tags); // your toast implementation
    });
});
```

---

### HtmxFormResponseMixin

Mix into any `FormView` or `CreateView` to replace the default success redirect with an HTMX trigger response:

```python
from django.views.generic.edit import CreateView
from django_htmx_plus.mixins import HtmxFormResponseMixin
from myapp.models import Article
from myapp.forms import ArticleForm

class ArticleCreateView(HtmxFormResponseMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/form.html"

    valid_triggers = ["articleCreated"]
    success_message = "Article created successfully."
```

After a valid submission, `form.save()` is called, an optional Django success message is queued, and an `HtmxResponse` carrying `articleCreated` in `HX-Trigger` is returned.

| Attribute | Type | Description |
|---|---|---|
| `valid_triggers` | `List[str]` | Events to include in `HX-Trigger` on success. |
| `success_message` | `str` | Optional Django success message to queue. |

---

### HtmxListView

A drop-in replacement for Django's `ListView` that adds URL-driven filtering, sorting, and elided pagination:

```python
from django.views.generic import ListView
from django_htmx_plus.views import HtmxListView
from myapp.models import Article

class ArticleListView(HtmxListView):
    model = Article
    template_name = "articles/list.html"
    paginate_by = 20
    target_id = "#article-table"

    # Restrict filtering and sorting to these fields only
    fields = ("id", "title", "status", "created_at")

    # Optional custom column labels
    labels = {
        "created_at": "Date Created",
    }
```

#### URL-based filtering

Filters are expressed as `field_name.filter_type=value` query parameters:

| Filter key | Django lookup | Example |
|---|---|---|
| `eq` | `exact` | `status.eq=published` |
| `ieq` | `iexact` | `title.ieq=hello` |
| `gt` / `gte` / `lt` / `lte` | `gt` / `gte` / `lt` / `lte` | `views.gte=100` |
| `like` / `ilike` | `like` / `ilike` | `title.ilike=django` |
| `sw` / `isw` | `startswith` / `istartswith` | `title.sw=Django` |
| `ew` / `iew` | `endswith` / `iendswith` | `title.ew=plus` |
| `in` | `in` | `status.in=['draft','published']` |
| `nl` | `isnull` | `deleted_at.nl=True` |
| `rng` | `range` | `created_at.rng=['2024-01-01','2024-12-31']` |
| `sch` | `search` | `body.sch=htmx` |

Only fields listed in `fields` are accepted. Setting `fields = ("__all__",)` lifts the restriction.

#### Sorting

Add `order_by=field_name` (or `order_by=-field_name` for descending) to the query string. Only fields in `fields` are permitted.

#### Context variables

| Variable | Description |
|---|---|
| `query_params` | URL-encoded query string (without `page`). |
| `page_range` | Elided page range for pagination controls. |
| `order_by` | The currently active ordering field. |
| `path` | The current request path. |
| `target_id` | The HTMX target element ID. |
| `query` | Full query string including `order_by`. |
| `filter_query` | Query string containing only filter parameters. |
| `filters` | Template-ready dict mapping plain field names to their filter values. |
| `fields` | Dict with `keys` (field names) and `labels` (display names). |

---

### Cotton Table Components

`django-htmx-plus` ships a set of [django-cotton](https://github.com/wrabit/django-cotton) components for rendering sortable, paginated HTMX tables with Bootstrap 5.

#### `<c-tables.htmx_table />`

Renders a full table with auto-generated sortable headers, rows, and an optional pager:

```html
{% load cotton_extras %}

<c-tables.htmx_table class="table table-striped" />
```

The component uses the `fields`, `objects`, `order_by`, `path`, `filter_query`, `target_id`, `page_obj`, and `paginator` context variables provided automatically by `HtmxListView`.

#### `<c-tables.header_cell name="field_name" />`

Renders a single `<th>` with an `hx-get` attribute that toggles ascending/descending order and a chevron icon indicating the current sort direction:

```html
<c-tables.head>
    <c-tables.header_cell name="title">Title</c-tables.header_cell>
    <c-tables.header_cell name="created_at">Date</c-tables.header_cell>
</c-tables.head>
```

#### `<c-tables.pager />`

Renders a Bootstrap 5 pagination control with previous/next buttons and elided page numbers, all wired to `hx-get`.

#### Icon components

| Component | Description |
|---|---|
| `<c-icons.chevron_up />` | Up chevron (ascending sort indicator). |
| `<c-icons.chevron_down />` | Down chevron (descending sort indicator). |
| `<c-icons.chevron_left />` | Left chevron (previous page). |
| `<c-icons.chevron_right />` | Right chevron (next page). |

All icon components accept an optional `add_class` attribute to append extra CSS classes.

---

### Template filters

Load the `cotton_extras` tag library in any template:

```html
{% load cotton_extras %}
```

| Filter | Description | Example |
|---|---|---|
| `get_attr` | Get an attribute from an object by name. | `{{ item\|get_attr:"title" }}` |
| `get_key_value` | Get a value from a dict by key. | `{{ my_dict\|get_key_value:"name" }}` |

---

### Built-in JavaScript Helper

`django-htmx-plus` ships a small ES module (`django-htmx-plus.js`) that integrates Bootstrap 5 **Modals** and **Offcanvases** with HTMX swap events, so they open and close automatically based on HTMX responses.

#### How it works

| Behaviour | Trigger |
|---|---|
| Show a Modal or Offcanvas | HTMX swaps content into the element → `htmx:afterSwap` fires and calls `.show()`. |
| Hide a Modal or Offcanvas | HTMX receives an **empty** response targeting the element → `htmx:beforeSwap` fires, calls `.hide()`, and cancels the swap. |
| Reset Modal body | Bootstrap's `hidden.bs.modal` event fires → the modal body is cleared to `""`. |

#### Setup

Mark your Bootstrap Modal root elements with `data-htmx-plus-modal="<id>"` and your Offcanvas root elements with `data-htmx-plus-offcanvas="<id>"`, where id is the id of the element that will be swapped,:

```html
<!-- Bootstrap Modal managed by django-htmx-plus -->
<div class="modal fade" data-htmx-plus-modal="dialog">
    <div id="dialog" class="modal-dialog">
        <!-- Modal content will be swapped here by HTMX and shown/hidden by django-htmx-plus.js -->
    </div>
</div>

<!-- Bootstrap Offcanvas managed by django-htmx-plus -->
<div id="flyout" class="offcanvas offcanvas-end" data-htmx-plus-offcanvas="flyout">
    <!-- Offcanvas content will be swapped here by HTMX and shown/hidden by django-htmx-plus.js -->
</div>
```

Then point an HTMX element at the matching target ID:

```html
<button hx-get="/person/add/" hx-target="#dialog">
    Add Person
</button>
```

- When the response has content the modal/offcanvas is shown automatically.
- When the server returns an empty `200` (or you use `HtmxResponse`) the modal/offcanvas is hidden automatically.

#### Including the script

Use the `{% htmx_plus_script %}` template tag to render the `<script>` tag. The script is loaded as an ES module and optionally forwards a CSP nonce if one is present in the template context:

```html
{% load django_htmx_plus %}

<!-- Place near the bottom of your base template, after Bootstrap JS -->
{% htmx_plus_script %}
```

This renders:

```html
<script src="/static/django_htmx_plus/django-htmx-plus.js" type="module"></script>
```

If a `nonce` variable is present in the template context it is automatically added as a `nonce="..."` attribute.

> **Note:** The script imports `Modal` and `Offcanvas` from `bootstrap`, so Bootstrap 5 must be available as an ES module (e.g. via an import map or a bundler). If you load Bootstrap as a plain global script instead, adjust your bundler or import map accordingly.

For example
```html
<script type="importmap">
{
  "imports": {
	"@popperjs/core": "{% static '@popperjs/core/dist/esm/index.js' %}",
	"bootstrap": "{% static 'bootstrap/js/index.esm.js' %}",
  }
}
</script>
```
---

## License

MIT — see [LICENSE](LICENSE) for details.
