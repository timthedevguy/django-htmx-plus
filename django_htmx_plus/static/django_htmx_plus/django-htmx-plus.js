import {Modal, Offcanvas} from 'bootstrap';

const dialogs = {}

for (const element of document.querySelectorAll('[data-htmx-plus-modal]')) {
    dialogs[element.dataset.htmxPlusModal] = new Modal(element);
}

for (const element of document.querySelectorAll('[data-htmx-plus-offcanvas]'))  {
    dialogs[element.dataset.htmxPlusOffcanvas] = new Offcanvas(element);
}

htmx.on("htmx:afterSwap", (e) => {
    // Response targeting #dialog => show the modal
    if(e.detail.target) {
        const element_id = e.detail.target.id;

        if (element_id in dialogs) {
            dialogs[element_id].show();
        }
    }
});

htmx.on("htmx:beforeSwap", (e) => {
    // Empty response targeting #dialog => hide the modal
    if(e.detail.target) {
        const element_id = e.detail.target.id;

        if(element_id in dialogs && !e.detail.xhr.response) {
            dialogs[element_id].hide();
            e.detail.shouldSwap = false;
        }
    }
});

htmx.on("hidden.bs.modal", (e) => {
    // This resets modal body to ""
    document.getElementById(e.target.id).firstElementChild.innerHTML = "";
})

htmx.on("hidden.bs.offcanvas", (e) => {
    console.log("offcanvas", e);
})

htmx.on("htmx:afterRequest", (e) => {
    // Elements marked with data-htmx-plus-push-url (e.g. the table's "Show N
    // entries" selector) push their own current value onto a relative
    // (path-less) URL, since the value isn't known server-side until after
    // the request fires and a plain hx-push-url="true" would instead push
    // the element's hx-get fetch path (which may differ from the page's own
    // URL, e.g. a nested partial-fetch endpoint).
    let element = null;

    if(e.detail?.requestConfig?.triggeringEvent?.srcElement) {
        if (e.detail.requestConfig.triggeringEvent.srcElement.id === "django-htmx-plus-paginate-select") {
            element = e.detail.requestConfig.triggeringEvent.srcElement;
        }
    }

    if (element && e.detail.successful && "htmxPlusPushUrl" in element.dataset) {
        history.pushState(null, "", element.dataset.htmxPlusPushUrl + element.value);
    }
});