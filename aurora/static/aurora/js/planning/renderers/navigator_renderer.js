// ======================================================================
// FILE: aurora/static/aurora/js/planning/renderers/navigator_renderer.js
// START: PLANNING_NAVIGATOR_RENDERER
// ======================================================================
(function(window, $) {
"use strict";

const Planning = window.AuroraPlanning = (
    window.AuroraPlanning || {}
);

Planning.renderers = Planning.renderers || {};

const INITIATIVE_STATUS_ORDER = [
    "PLANNED",
    "ACTIVE",
    "PAUSED",
    "COMPLETED",
    "CANCELLED",
];

let currentInitiatives = [];
let currentSelectedInitiativeId = null;

function navigatorItem(options) {
    const $button = $("<button>", {
        type: "button",
        class: "planning-navigator-item text-start",
    });

    if (options.id) {
        $button.attr("data-record-id", options.id);
    }

    if (options.itemType) {
        $button.attr("data-item-type", options.itemType);
    }

    if (options.isActive) {
        $button.addClass("is-active");
    }

    if (options.disabled) {
        $button.prop("disabled", true);
    }

    const $body = $("<span>", {
        class: "planning-navigator-item-body",
    });

    $body.append(
        $("<span>", {
            class: "planning-navigator-item-title",
            text: options.title || "Untitled",
        })
    );

    if (options.meta) {
        $body.append(
            $("<span>", {
                class: "planning-navigator-item-meta",
                text: options.meta,
            })
        );
    }

    $button.append(
        $("<span>", {
            class: "planning-navigator-marker",
        }),
        $body
    );

    return $button;
}

function getInitiativeStatusFilter() {
    return (
        $(
            'input[name="planning-initiative-status-filter"]:checked'
        ).val()
        || "ALL"
    );
}

function normalizeInitiatives(initiatives) {
    return initiatives
        .slice()
        .sort(function(left, right) {
            const leftStatusIndex = INITIATIVE_STATUS_ORDER.indexOf(
                left.status
            );
            const rightStatusIndex = INITIATIVE_STATUS_ORDER.indexOf(
                right.status
            );

            const normalizedLeftStatusIndex = (
                leftStatusIndex === -1
                    ? INITIATIVE_STATUS_ORDER.length
                    : leftStatusIndex
            );

            const normalizedRightStatusIndex = (
                rightStatusIndex === -1
                    ? INITIATIVE_STATUS_ORDER.length
                    : rightStatusIndex
            );

            if (
                normalizedLeftStatusIndex
                !== normalizedRightStatusIndex
            ) {
                return (
                    normalizedLeftStatusIndex
                    - normalizedRightStatusIndex
                );
            }

            return (
                left.title || ""
            ).localeCompare(
                right.title || "",
                undefined,
                {
                    sensitivity: "base",
                }
            );
        });
}

function renderCurrentInitiatives() {
    const $list = $("#planning-navigator-initiative-list");

    $list.empty();

    if (!currentInitiatives.length) {
        $list.append(
            $("<div>", {
                class: "planning-navigator-placeholder",
                text: "This Project has no Initiatives.",
            })
        );

        return;
    }

    const selectedStatus = getInitiativeStatusFilter();

    const visibleInitiatives = normalizeInitiatives(
        currentInitiatives
    ).filter(function(initiative) {
        return (
            selectedStatus === "ALL"
            || initiative.status === selectedStatus
        );
    });

    if (!visibleInitiatives.length) {
        $list.append(
            $("<div>", {
                class: "planning-navigator-placeholder",
                text: (
                    "No "
                    + selectedStatus.toLowerCase()
                    + " Initiatives."
                ),
            })
        );

        return;
    }

    const selectedId = (
        currentSelectedInitiativeId !== null
        && currentSelectedInitiativeId !== undefined
    )
        ? String(currentSelectedInitiativeId)
        : null;

    visibleInitiatives.forEach(function(initiative) {
        $list.append(
            navigatorItem({
                id: initiative.id,
                itemType: "initiative",
                title: initiative.title || "Untitled Initiative",
                meta: (
                    initiative.status_label
                    || initiative.status
                    || "Unknown status"
                ),
                isActive: String(initiative.id) === selectedId,
            })
        );
    });
}

function renderInitiatives(
    initiatives,
    selectedInitiativeId
) {
    currentInitiatives = Array.isArray(initiatives)
        ? initiatives.slice()
        : [];

    currentSelectedInitiativeId = selectedInitiativeId;

    renderCurrentInitiatives();
}

function refreshInitiatives() {
    renderCurrentInitiatives();
}

function reset() {
    currentInitiatives = [];
    currentSelectedInitiativeId = null;

    renderCurrentInitiatives();
}

Planning.renderers.navigator = {
    renderInitiatives: renderInitiatives,
    refreshInitiatives: refreshInitiatives,
    reset: reset,
};

})(window, jQuery);
// ======================================================================
// END: PLANNING_NAVIGATOR_RENDERER
// ======================================================================