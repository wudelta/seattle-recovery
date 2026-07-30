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

    function populateDocumentSection(
        $fragment,
        sectionSelector,
        valueSelector,
        value
    ) {
        const $section = $fragment.find(
            sectionSelector
        );

        if (!value) {
            $section.addClass("d-none");
            return;
        }

        $section
            .find(valueSelector)
            .text(value);
    }

    function populateFileSection(
        $fragment,
        sectionSelector,
        listSelector,
        files
    ) {
        const $section = $fragment.find(
            sectionSelector
        );

        const $list = $section.find(
            listSelector
        );

        if (!Array.isArray(files) || !files.length) {
            $section.addClass("d-none");
            return;
        }

        files.forEach(function(stepFile) {
            const $entry = $("<div>", {
                class: "planning-step-file",
            });

            $("<div>", {
                class: "planning-step-file-path planning-text",
                text: stepFile.file_path || "",
            }).appendTo($entry);

            if (stepFile.reason) {
                $("<div>", {
                    class: "planning-step-file-reason planning-muted small",
                    text: stepFile.reason,
                }).appendTo($entry);
            }

            $list.append($entry);
        });
    }

    function render(step) {
        const $fragment = utilities.cloneTemplate(
            "planning-step-template"
        );

        const $step = $fragment.find(
            ".planning-step"
        );

        const document = step.document || {};
        const validation = step.validation || {};
        const plannedFiles = step.planned_files || [];
        const actualFiles = step.actual_files || [];

        const validationDescription = (
            validation.description
            || step.validation_description
            || ""
        );

        const validationNotes = (
            validation.notes
            || step.validation_notes
            || ""
        );

        const validatedBy = (
            validation.validated_by
            || step.validated_by
            || null
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

        populateDocumentSection(
            $fragment,
            ".planning-step-technical-design-section",
            ".planning-step-technical-design",
            document.technical_design
        );

        populateDocumentSection(
            $fragment,
            ".planning-step-dependencies-section",
            ".planning-step-dependencies",
            document.dependencies
        );

        populateDocumentSection(
            $fragment,
            ".planning-step-assumptions-section",
            ".planning-step-assumptions",
            document.assumptions
        );

        populateDocumentSection(
            $fragment,
            ".planning-step-implementation-notes-section",
            ".planning-step-implementation-notes",
            document.implementation_notes
        );

        populateDocumentSection(
            $fragment,
            ".planning-step-discussion-section",
            ".planning-step-discussion",
            document.discussion
        );

        populateFileSection(
            $fragment,
            ".planning-step-planned-files-section",
            ".planning-step-planned-files",
            plannedFiles
        );

        populateFileSection(
            $fragment,
            ".planning-step-actual-files-section",
            ".planning-step-actual-files",
            actualFiles
        );

        populateDocumentSection(
            $fragment,
            ".planning-step-validation-plan-section",
            ".planning-step-validation-description",
            validationDescription
        );

        if (validationNotes) {
            $fragment
                .find(
                    ".planning-step-validation-notes"
                )
                .text(
                    validationNotes
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
            validatedBy
            && validatedBy.display_name
        ) {
            $validator.text(
                "Validated by "
                + validatedBy.display_name
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

        const hasDocumentContent = (
            document.technical_design
            || document.dependencies
            || document.assumptions
            || document.implementation_notes
            || document.discussion
            || plannedFiles.length
            || actualFiles.length
            || validationDescription
            || validationNotes
            || hasFooterContent
        );

        if (!hasDocumentContent) {
            $fragment
                .find(".planning-step-document")
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