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

    function render(step) {
        const $fragment = utilities.cloneTemplate(
            "planning-step-template"
        );

        const $step = $fragment.find(".planning-step");

        $step.attr("data-step-id", step.id);
        $step.data("step", step);

        $fragment
            .find(".planning-step-position")
            .text(`Step ${step.position}`);

        $fragment
            .find(".planning-step-title")
            .text(step.title || "Untitled step");

        $fragment
            .find(".planning-step-status")
            .addClass(utilities.statusClass(step.status))
            .text(
                step.status_label
                || step.status
                || "Unknown"
            );

        const estimateParts = [];

        if (step.estimated_minutes !== null) {
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
            $estimate.text(estimateParts.join(" · "));
        } else {
            $estimate.addClass("d-none");
        }

        const $description = $fragment.find(
            ".planning-step-description"
        );

        if (step.description) {
            $description.text(step.description);
        } else {
            $description.addClass("d-none");
        }

        const $validation = $fragment.find(
            ".planning-step-validation"
        );

        if (step.validation_description) {
            $fragment
                .find(".planning-step-validation-description")
                .text(step.validation_description);
        } else {
            $validation.addClass("d-none");
        }

        if (step.validation_notes) {
            $fragment
                .find(".planning-step-validation-notes")
                .text(step.validation_notes);

            $fragment
                .find(".planning-step-validation-result")
                .removeClass("d-none");
        }

        if (step.validated_by) {
            $fragment
                .find(".planning-step-validator")
                .text(
                    `Validated by ${step.validated_by.display_name}`
                );
        }

        if (step.updated_at) {
            $fragment
                .find(".planning-step-updated")
                .text(
                    `Updated ${utilities.formatDate(step.updated_at)}`
                );
        }

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