// ======================================================================
// FILE: aurora/static/aurora/js/planning/initiative_renderer.js
// START: PLANNING_INITIATIVE_RENDERER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const utilities = Planning.utilities;

    function render(initiative) {
        const $fragment = utilities.cloneTemplate(
            "planning-initiative-template"
        );

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

        $initiative.data("initiative-id", initiative.id);

        $fragment
            .find(".planning-initiative-position")
            .text(`Initiative ${initiative.position}`);

        $fragment
            .find(".planning-initiative-title")
            .text(
                initiative.title || "Untitled initiative"
            );

        $fragment
            .find(".planning-initiative-status")
            .addClass(
                utilities.statusClass(initiative.status)
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
            $description.text(initiative.description);
        } else {
            $description.addClass("d-none");
        }

        if (initiative.created_by) {
            $fragment
                .find(".planning-initiative-owner")
                .text(
                    `Owner: ${initiative.created_by.display_name}`
                );
        }

        if (initiative.updated_at) {
            $fragment
                .find(".planning-initiative-updated")
                .text(
                    `Updated ${
                        utilities.formatDate(
                            initiative.updated_at
                        )
                    }`
                );
        }

        if (
            Array.isArray(initiative.phases)
            && initiative.phases.length
        ) {
            initiative.phases.forEach(function(phase) {
                $phaseList.append(
                    Planning.renderers.phase.render(phase)
                );
            });
        } else {
            $phaseList.append(
                $("<div>", {
                    class: "text-muted small",
                    text: (
                        "No phases are defined for this initiative."
                    ),
                })
            );
        }

        return $fragment;
    }

    Planning.renderers = Planning.renderers || {};

    Planning.renderers.initiative = {
        render: render,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_INITIATIVE_RENDERER
// ======================================================================