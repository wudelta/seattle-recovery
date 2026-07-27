// ======================================================================
// FILE: aurora/static/aurora/js/planning/phase_renderer.js 
// START: PLANNING_PHASE_RENDERER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const utilities = Planning.utilities;

    function render(phase) {
        const $fragment = utilities.cloneTemplate(
            "planning-phase-template"
        );

        const $phase = $fragment.find(".planning-phase");
        const $stepList = $fragment.find(
            ".planning-step-list"
        );

        $phase.attr("data-phase-id", phase.id);
        $phase.data("phase", phase);

        $fragment
            .find(".planning-phase-position")
            .text(`Phase ${phase.position}`);

        $fragment
            .find(".planning-phase-title")
            .text(phase.title || "Untitled phase");

        $fragment
            .find(".planning-phase-status")
            .addClass(utilities.statusClass(phase.status))
            .text(
                phase.status_label
                || phase.status
                || "Unknown"
            );

        const $description = $fragment.find(
            ".planning-phase-description"
        );

        if (phase.description) {
            $description.text(phase.description);
        } else {
            $description.addClass("d-none");
        }

        const stepCount = Array.isArray(phase.steps)
            ? phase.steps.length
            : phase.step_count || 0;

        $fragment
            .find(".planning-phase-summary")
            .text(
                `${stepCount} step`
                + `${stepCount === 1 ? "" : "s"}`
            );

        if (
            Array.isArray(phase.steps)
            && phase.steps.length
        ) {
            phase.steps.forEach(function(step) {
                $stepList.append(
                    Planning.renderers.step.render(step)
                );
            });
        } else {
            $stepList.append(
                $("<div>", {
                    class: "px-3 py-3 text-muted small",
                    text: (
                        "No implementation steps are defined."
                    ),
                })
            );
        }

        return $fragment;
    }

    Planning.renderers = Planning.renderers || {};

    Planning.renderers.phase = {
        render: render,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_PHASE_RENDERER 
// ======================================================================