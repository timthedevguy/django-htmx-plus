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
    const element_id = e.detail.target.id;

    if(element_id in dialogs) {
        dialogs[element_id].show();
    }
});

htmx.on("htmx:beforeSwap", (e) => {
    // Empty response targeting #dialog => hide the modal
    const element_id = e.detail.target.id;

    if(element_id in dialogs && !e.detail.xhr.response) {
        dialogs[element_id].hide();
        e.detail.shouldSwap = false;
    }
});

htmx.on("hidden.bs.modal", (e) => {
    // This resets modal body to ""
    document.getElementById(e.target.id).firstElementChild.innerHTML = "";
})

htmx.on("hidden.bs.offcanvas", (e) => {
    console.log("offcanvas", e);
})