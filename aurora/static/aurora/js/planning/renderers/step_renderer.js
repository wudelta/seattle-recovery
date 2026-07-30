// ======================================================================
// FILE: aurora/static/aurora/js/planning/renderers/step_renderer.js
// START: STEP_RENDERER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const utilities = Planning.utilities;

    function applyInitialCollapsedState(
        $fragment,
        step
    ) {
        if (step.status !== "COMPLETED") {
            return;
        }

        $fragment
            .find(".planning-step")
            .addClass("planning-step-collapsed");

        $fragment
            .find(".planning-step-document")
            .addClass("d-none");

        $fragment
            .find(".planning-toggle-step-btn")
            .attr({
                "aria-expanded": "false",
                "aria-label": "Expand Step",
                title: "Expand Step",
            });

        $fragment
            .find(".planning-step-toggle-icon")
            .text("▸");
    }

    function render(step) {
        const $fragment = utilities.cloneTemplate(
            "planning-step-template"
        );

        const $step = $fragment.find(
            ".planning-step"
        );

        $step.attr(
            "data-step-id",
            step.id
        );

        $step.data(
            "step",
            step
        );

        $fragment
            .find(".planning-step-position")
            .text(
                `Step ${step.position}`
            );

        $fragment
            .find(".planning-step-title")
            .text(
                step.title || "Untitled step"
            );

        $fragment
            .find(".planning-step-status")
            .addClass(
                utilities.statusClass(
                    step.status
                )
            )
            .text(
                step.status_label
                || step.status
                || "Unknown"
            );

        const estimateParts = [];

        if (
            step.estimated_minutes !== null
            && step.estimated_minutes !== undefined
        ) {
            estimateParts.push(
                `${step.estimated_minutes} min`
            );
        }

        if (step.estimate_confidence_label) {
            estimateParts.push(
                step.estimate_confidence_label
            );
        }

        const $estimate = $fragment.find(
            ".planning-step-estimate"
        );

        if (estimateParts.length) {
            $estimate.text(
                estimateParts.join(" · ")
            );
        } else {
            $estimate.addClass("d-none");
        }

        const $description = $fragment.find(
            ".planning-step-description"
        );

        if (step.description) {
            $description.text(
                step.description
            );
        } else {
            $description.addClass("d-none");
        }

        const $validationPlan = $fragment.find(
            ".planning-step-validation-description"
        );

        const $validationPlanSection = (
            $validationPlan.closest(
                ".planning-step-section"
            )
        );

        if (step.validation_description) {
            $validationPlan.text(
                step.validation_description
            );
        } else {
            $validationPlanSection.addClass(
                "d-none"
            );
        }

        if (step.validation_notes) {
            $fragment
                .find(
                    ".planning-step-validation-notes"
                )
                .text(
                    step.validation_notes
                );

            $fragment
                .find(
                    ".planning-step-validation-result"
                )
                .removeClass("d-none");
        }

        const $validator = $fragment.find(
            ".planning-step-validator"
        );

        if (
            step.validated_by
            && step.validated_by.display_name
        ) {
            $validator.text(
                "Validated by "
                + step.validated_by.display_name
            );
        } else {
            $validator.addClass("d-none");
        }

        const $updated = $fragment.find(
            ".planning-step-updated"
        );

        if (step.updated_at) {
            $updated.text(
                "Updated "
                + utilities.formatDate(
                    step.updated_at
                )
            );
        } else {
            $updated.addClass("d-none");
        }

        const hasFooterContent = (
            !$validator.hasClass("d-none")
            || !$updated.hasClass("d-none")
        );

        if (!hasFooterContent) {
            $fragment
                .find(".planning-step-footer")
                .addClass("d-none");
        }

        applyInitialCollapsedState(
            $fragment,
            step
        );

        return $fragment;
    }

    Planning.renderers = Planning.renderers || {};

    Planning.renderers.step = {
        render: render,
    };
})(window, jQuery);
// ======================================================================
// END: STEP_RENDERER
// ======================================================================