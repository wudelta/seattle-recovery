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

    function renderInitiatives(
        initiatives,
        selectedInitiativeId
    ) {
        const $list = $("#planning-navigator-initiative-list");

        $list.empty();

        if (!Array.isArray(initiatives) || !initiatives.length) {
            $list.append(
                $("<div>", {
                    class: "planning-navigator-placeholder",
                    text: "This Project has no Initiatives.",
                })
            );

            return;
        }

        const selectedId = (
            selectedInitiativeId !== null
            && selectedInitiativeId !== undefined
        )
            ? String(selectedInitiativeId)
            : null;

        initiatives.forEach(function(initiative) {
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

    function reset() {
        renderInitiatives([], null);
    }

    Planning.renderers.navigator = {
        renderInitiatives: renderInitiatives,
        reset: reset,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_NAVIGATOR_RENDERER
// ======================================================================