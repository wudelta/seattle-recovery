// ======================================================================
// FILE: aurora/static/aurora/js/planning/renderers.js
// START: PLANNING_HIERARCHY_RENDERERS
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const utilities = Planning.utilities;
    const workspace = Planning.workspace;

    function renderStep(step) {
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

    function renderPhase(phase) {
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
                $stepList.append(renderStep(step));
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

    function renderInitiative(initiative) {
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
                $phaseList.append(renderPhase(phase));
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

    function renderPlanningPayload(payload) {
        const projects = payload.projects || [];
        const activeProject = payload.active_project || null;
        const initiativeOptions = (
            payload.initiative_options || []
        );
        const renderedInitiative = (
            payload.active_initiative || null
        );
        const summary = payload.summary || {};

        const $initiativeList = $(
            "#planning-initiative-list"
        );

        state.setActiveProject(activeProject);

        workspace.renderProjectSelector(
            projects,
            activeProject
        );

        workspace.renderNavigatorProject(
            activeProject,
            initiativeOptions.length
        );

        $("#planning-error-state").addClass("d-none");

        $("#planning-empty-state")
            .addClass("d-none")
            .removeClass("d-flex");

        $initiativeList.empty();

        $("#planning-empty-project-name").text(
            activeProject
                ? activeProject.title
                : ""
        );

        if (
            !initiativeOptions.length
            || !renderedInitiative
        ) {
            state.clearActiveInitiative();

            workspace.renderNavigatorInitiatives(
                [],
                null
            );

            workspace.showEmptyState();
            return;
        }

        state.setActiveInitiativeId(
            renderedInitiative.id
        );

        state.setActiveInitiative(
            renderedInitiative
        );

        workspace.renderNavigatorInitiatives(
            initiativeOptions,
            renderedInitiative.id
        );

        $initiativeList.append(
            renderInitiative(renderedInitiative)
        );

        const initiativeCount = initiativeOptions.length;
        const phaseCount = summary.phase_count || 0;
        const stepCount = summary.step_count || 0;
        const projectTitle = activeProject
            ? activeProject.title
            : "No Project";

        const initiativeStatus = renderedInitiative.status
            ? {
                value: renderedInitiative.status,
                label: (
                    renderedInitiative.status_label
                    || renderedInitiative.status
                ),
            }
            : null;

        workspace.setWorkbenchHeader(
            (
                renderedInitiative.title
                || "Untitled Initiative"
            ),
            (
                `${projectTitle} · `
                + `${phaseCount} phase`
                + `${phaseCount === 1 ? "" : "s"} · `
                + `${stepCount} step`
                + `${stepCount === 1 ? "" : "s"}`
            ),
            initiativeStatus
        );

        $("#planning-summary-badge")
            .removeClass("text-danger text-info")
            .addClass("text-success")
            .text(
                `${phaseCount} phase`
                + `${phaseCount === 1 ? "" : "s"} · `
                + `${stepCount} step`
                + `${stepCount === 1 ? "" : "s"}`
            );

        $("#planning-status-bar")
            .removeClass("text-danger text-muted")
            .addClass("text-success")
            .text(
                `${projectTitle} · `
                + `${initiativeCount} initiative`
                + `${initiativeCount === 1 ? "" : "s"} · `
                + `showing ${renderedInitiative.title}.`
            );
    }

    Planning.renderers = {
        renderStep: renderStep,
        renderPhase: renderPhase,
        renderInitiative: renderInitiative,
        renderPlanningPayload: renderPlanningPayload,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_HIERARCHY_RENDERERS
// ======================================================================