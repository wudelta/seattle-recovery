// ======================================================================
// FILE: aurora/static/aurora/js/planning/renderers/initiative_renderer.js
// START: PLANNING_INITIATIVE_RENDERER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const utilities = Planning.utilities;

    function populateInitiativeHeader(
        $fragment,
        initiative
    ) {
        const $initiative = $fragment.find(
            ".planning-initiative"
        );

        $initiative.attr(
            "data-initiative-id",
            initiative.id
        );

        $initiative.data(
            "initiative-id",
            initiative.id
        );

        $fragment
            .find(".planning-initiative-position")
            .text(
                `Initiative ${initiative.position}`
            );

        $fragment
            .find(".planning-initiative-title")
            .text(
                initiative.title || "Untitled initiative"
            );

        $fragment
            .find(".planning-initiative-status")
            .addClass(
                utilities.statusClass(
                    initiative.status
                )
            )
            .text(
                initiative.status_label
                || initiative.status
                || "Unknown"
            );

        const $description = $fragment.find(
            ".planning-initiative-description"
        );

        if (initiative.description) {
            $description.text(
                initiative.description
            );
        } else {
            $description.addClass("d-none");
        }

        const $owner = $fragment.find(
            ".planning-initiative-owner"
        );

        const $updated = $fragment.find(
            ".planning-initiative-updated"
        );

        const $separator = $fragment.find(
            ".planning-initiative-meta-separator"
        );

        if (initiative.created_by) {
            $owner.text(
                `Owner: ${
                    initiative.created_by.display_name
                }`
            );
        } else {
            $owner.addClass("d-none");
        }

        if (initiative.updated_at) {
            $updated.text(
                `Updated ${
                    utilities.formatDate(
                        initiative.updated_at
                    )
                }`
            );
        } else {
            $updated.addClass("d-none");
        }

        if (
            !initiative.created_by
            || !initiative.updated_at
        ) {
            $separator.addClass("d-none");
        }

        return $fragment;
    }

    function populatePhaseList(
        $fragment,
        initiative
    ) {
        const $initiative = $fragment.find(
            ".planning-initiative"
        );

        const $phaseList = $fragment.find(
            ".planning-phase-list"
        );

        $initiative.attr(
            "data-initiative-id",
            initiative.id
        );

        $initiative.data(
            "initiative-id",
            initiative.id
        );

        if (
            Array.isArray(initiative.phases)
            && initiative.phases.length
        ) {
            initiative.phases.forEach(
                function(phase) {
                    $phaseList.append(
                        Planning.renderers.phase.render(
                            phase
                        )
                    );
                }
            );
        } else {
            $phaseList.append(
                $("<div>", {
                    class: "text-muted small",
                    text: (
                        "No phases are defined for "
                        + "this initiative."
                    ),
                })
            );
        }

        return $fragment;
    }

    function renderHeader(initiative) {
        const $fragment = utilities.cloneTemplate(
            "planning-initiative-header-template"
        );

        return populateInitiativeHeader(
            $fragment,
            initiative
        );
    }

    function renderContent(initiative) {
        const $fragment = utilities.cloneTemplate(
            "planning-initiative-content-template"
        );

        return populatePhaseList(
            $fragment,
            initiative
        );
    }

    Planning.renderers = Planning.renderers || {};

    Planning.renderers.initiative = {
        renderHeader: renderHeader,
        renderContent: renderContent,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_INITIATIVE_RENDERER
// ======================================================================