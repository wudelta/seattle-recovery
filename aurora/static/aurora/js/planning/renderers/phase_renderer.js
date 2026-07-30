// ======================================================================
// FILE: aurora/static/aurora/js/planning/renderers/phase_renderer.js
// START: PLANNING_PHASE_RENDERER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const utilities = Planning.utilities;

    function getStepCounts(phase) {
        const steps = Array.isArray(phase.steps)
            ? phase.steps
            : [];

        const total = steps.length
            ? steps.length
            : phase.step_count || 0;

        const completed = steps.length
            ? steps.filter(function(step) {
                return step.status === "COMPLETED";
            }).length
            : phase.completed_step_count || 0;

        return {
            total: total,
            completed: completed,
        };
    }

    function populateProgress(
        $fragment,
        stepCounts
    ) {
        const percentage = stepCounts.total
            ? Math.round(
                (
                    stepCounts.completed
                    / stepCounts.total
                ) * 100
            )
            : 0;

        $fragment
            .find(".planning-phase-progress-label")
            .text(
                `${stepCounts.completed}`
                + `/${stepCounts.total} complete`
            );

        $fragment
            .find(".planning-phase-progress-track")
            .attr("aria-valuenow", percentage)
            .attr(
                "aria-label",
                `${percentage}% complete`
            );

        $fragment
            .find(".planning-phase-progress-value")
            .css("width", `${percentage}%`);
    }

    function applyInitialCollapsedState(
        $fragment,
        phase
    ) {
        if (phase.status !== "COMPLETED") {
            return;
        }

        $fragment
            .find(".planning-phase")
            .addClass("planning-phase-collapsed");

        $fragment
            .find(".planning-phase-body")
            .addClass("d-none");

        $fragment
            .find(".planning-toggle-phase-btn")
            .attr({
                "aria-expanded": "false",
                "aria-label": "Expand Phase",
                title: "Expand Phase",
            });

        $fragment
            .find(".planning-phase-toggle-icon")
            .text("▸");
    }

    function render(phase) {
        const $fragment = utilities.cloneTemplate(
            "planning-phase-template"
        );

        const $phase = $fragment.find(
            ".planning-phase"
        );

        const $stepList = $fragment.find(
            ".planning-step-list"
        );

        $phase.attr(
            "data-phase-id",
            phase.id
        );

        $phase.data(
            "phase",
            phase
        );

        $fragment
            .find(".planning-phase-position")
            .text(
                `Phase ${phase.position}`
            );

        $fragment
            .find(".planning-phase-title")
            .text(
                phase.title || "Untitled phase"
            );

        $fragment
            .find(".planning-phase-status")
            .addClass(
                utilities.statusClass(
                    phase.status
                )
            )
            .text(
                phase.status_label
                || phase.status
                || "Unknown"
            );

        const $description = $fragment.find(
            ".planning-phase-description"
        );

        if (phase.description) {
            $description.text(
                phase.description
            );
        } else {
            $description.addClass("d-none");
        }

        const stepCounts = getStepCounts(phase);

        $fragment
            .find(".planning-phase-summary")
            .text(
                `${stepCounts.total} step`
                + `${stepCounts.total === 1 ? "" : "s"}`
            );

        populateProgress(
            $fragment,
            stepCounts
        );

        if (
            Array.isArray(phase.steps)
            && phase.steps.length
        ) {
            phase.steps.forEach(function(step) {
                $stepList.append(
                    Planning.renderers.step.render(
                        step
                    )
                );
            });
        } else {
            $stepList.append(
                $("<div>", {
                    class:
                        "px-3 py-3 text-muted small",
                    text:
                        "No implementation steps are defined.",
                })
            );
        }

        applyInitialCollapsedState(
            $fragment,
            phase
        );

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