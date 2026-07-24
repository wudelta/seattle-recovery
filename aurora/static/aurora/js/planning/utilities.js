// ======================================================================
// FILE: aurora/static/aurora/js/planning/utilities.js
// START: PLANNING_SHARED_UTILITIES
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const STATUS_CLASSES = {
        PLANNED: "bg-secondary text-light",
        ACTIVE: "bg-primary text-light",
        PAUSED: "bg-warning text-dark",
        COMPLETED: "bg-success text-light",
        CANCELLED: "bg-danger text-light",
    };

    function formatDate(value) {
        if (!value) {
            return "";
        }

        const parsedDate = new Date(value);

        if (Number.isNaN(parsedDate.getTime())) {
            return "";
        }

        return parsedDate.toLocaleString();
    }

    function statusClass(status) {
        return STATUS_CLASSES[status] || "bg-dark text-light";
    }

    function cloneTemplate(templateId) {
        const template = document.getElementById(templateId);

        if (!template) {
            throw new Error(
                `Missing planning template: ${templateId}`
            );
        }

        return $(template.content.cloneNode(true));
    }

    function getCsrfToken() {
        const cookie = document.cookie
            .split("; ")
            .find(function(item) {
                return item.startsWith("csrftoken=");
            });

        if (!cookie) {
            return "";
        }

        return decodeURIComponent(cookie.split("=")[1]);
    }

    Planning.utilities = {
        formatDate: formatDate,
        statusClass: statusClass,
        cloneTemplate: cloneTemplate,
        getCsrfToken: getCsrfToken,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_SHARED_UTILITIES
// ======================================================================