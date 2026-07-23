// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 1 OF 7)
// START: PLANNING_STATE_AND_SHARED_UTILITIES
// ======================================================================
(function(window, $) {
    "use strict";

    let planningInitialized = false;
    let planningEndpoints = {};
    let planningRequest = null;
    let initiativeRequest = null;
    let phaseRequest = null;
    let stepRequest = null;
    let activeProjectSlug = null;
    let activeInitiativeId = null;

    const STATUS_CLASSES = {
        PLANNED: "bg-secondary text-light",
        ACTIVE: "bg-primary text-light",
        PAUSED: "bg-warning text-dark",
        COMPLETED: "bg-success text-light",
        CANCELLED: "bg-danger text-light",
    };

    function formatDate(value) {
        if (!value) {
            return "";
        }

        const parsedDate = new Date(value);

        if (Number.isNaN(parsedDate.getTime())) {
            return "";
        }

        return parsedDate.toLocaleString();
    }

    function statusClass(status) {
        return STATUS_CLASSES[status] || "bg-dark text-light";
    }

    function cloneTemplate(templateId) {
        const template = document.getElementById(templateId);

        if (!template) {
            throw new Error(`Missing planning template: ${templateId}`);
        }

        return $(template.content.cloneNode(true));
    }

    function getCsrfToken() {
        const cookie = document.cookie
            .split("; ")
            .find(function(item) {
                return item.startsWith("csrftoken=");
            });

        if (!cookie) {
            return "";
        }

        return decodeURIComponent(cookie.split("=")[1]);
    }

    function renderProjectSelector(projects, activeProject) {
        const $projectSelect = $("#planning-project-select");

        $projectSelect.empty();

        if (!Array.isArray(projects) || !projects.length) {
            activeProjectSlug = null;
            activeInitiativeId = null;

            $projectSelect
                .append(
                    $("<option>", {
                        value: "",
                        text: "No active projects",
                    })
                )
                .prop("disabled", true);

            $("#planning-initiative-select")
                .empty()
                .append(
                    $("<option>", {
                        value: "",
                        text: "Create a Project first",
                    })
                )
                .prop("disabled", true);

            $(
                "#planning-create-initiative-btn, "
                + "#planning-empty-create-initiative-btn"
            ).prop("disabled", true);

            return;
        }

        projects.forEach(function(project) {
            $projectSelect.append(
                $("<option>", {
                    value: project.slug,
                    text: project.title,
                })
            );
        });

        activeProjectSlug = (
            activeProject
            && activeProject.slug
        )
            ? activeProject.slug
            : projects[0].slug;

        $projectSelect
            .val(activeProjectSlug)
            .prop("disabled", false);

        $(
            "#planning-create-initiative-btn, "
            + "#planning-empty-create-initiative-btn"
        ).prop("disabled", false);
    }

    function renderInitiativeSelector(
        initiatives,
        preferredInitiativeId
    ) {
        const $initiativeSelect = $("#planning-initiative-select");

        $initiativeSelect.empty();

        if (!Array.isArray(initiatives) || !initiatives.length) {
            activeInitiativeId = null;

            $initiativeSelect
                .append(
                    $("<option>", {
                        value: "",
                        text: "No initiatives",
                    })
                )
                .prop("disabled", true);

            return null;
        }

        initiatives.forEach(function(initiative) {
            $initiativeSelect.append(
                $("<option>", {
                    value: String(initiative.id),
                    text: initiative.title || "Untitled initiative",
                })
            );
        });

        const preferredId = preferredInitiativeId !== null
            && preferredInitiativeId !== undefined
            ? String(preferredInitiativeId)
            : null;

        const selectedInitiative = initiatives.find(
            function(initiative) {
                return preferredId !== null
                    && String(initiative.id) === preferredId;
            }
        ) || initiatives[0];

        activeInitiativeId = selectedInitiative.id;

        $initiativeSelect
            .val(String(activeInitiativeId))
            .prop("disabled", false);

        return selectedInitiative;
    }
// ======================================================================
// END: PLANNING_STATE_AND_SHARED_UTILITIES (PATCH 1 OF 7)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 2 OF 7)
// START: PLANNING_WORKSPACE_STATE
// ======================================================================
    function setLoadingState(isLoading) {
        const $loadingState = $("#planning-loading-state");
        const $refreshButton = $("#planning-refresh-btn");

        $loadingState.toggleClass("d-none", !isLoading);
        $loadingState.toggleClass("d-flex", isLoading);

        $refreshButton.prop("disabled", isLoading);
        $refreshButton.text(isLoading ? "Loading..." : "Refresh");
    }

    function showError(message) {
        $("#planning-initiative-list").empty();

        $("#planning-empty-state")
            .addClass("d-none")
            .removeClass("d-flex");

        $("#planning-error-message").text(
            message || "An unexpected error occurred."
        );

        $("#planning-error-state").removeClass("d-none");

        $("#planning-status-bar")
            .removeClass("text-muted text-success")
            .addClass("text-danger")
            .text("Decision Engine data failed to load.");

        $("#planning-summary-badge")
            .removeClass("text-info text-success")
            .addClass("text-danger")
            .text("Load failed");
    }

    function showEmptyState() {
        $("#planning-initiative-list").empty();
        $("#planning-error-state").addClass("d-none");

        $("#planning-empty-state")
            .removeClass("d-none")
            .addClass("d-flex");

        $("#planning-status-bar")
            .removeClass("text-danger text-success")
            .addClass("text-muted")
            .text("No persisted initiatives were returned.");

        $("#planning-summary-badge")
            .removeClass("text-danger text-success")
            .addClass("text-info")
            .text("0 initiatives");
    }
// ======================================================================
// END: PLANNING_WORKSPACE_STATE (PATCH 2 OF 7)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 3 OF 7)
// START: PLANNING_HIERARCHY_RENDERERS
// ======================================================================
    function renderStep(step) {
        const $fragment = cloneTemplate("planning-step-template");
        const $step = $fragment.find(".planning-step");

        $step.attr("data-step-id", step.id);

        $fragment
            .find(".planning-step-position")
            .text(`Step ${step.position}`);

        $fragment
            .find(".planning-step-title")
            .text(step.title || "Untitled step");

        $fragment
            .find(".planning-step-status")
            .addClass(statusClass(step.status))
            .text(step.status_label || step.status || "Unknown");

        const estimateParts = [];

        if (step.estimated_minutes !== null) {
            estimateParts.push(`${step.estimated_minutes} min`);
        }

        if (step.estimate_confidence_label) {
            estimateParts.push(step.estimate_confidence_label);
        }

        const $estimate = $fragment.find(".planning-step-estimate");

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
                .text(`Validated by ${step.validated_by.display_name}`);
        }

        if (step.updated_at) {
            $fragment
                .find(".planning-step-updated")
                .text(`Updated ${formatDate(step.updated_at)}`);
        }

        return $fragment;
    }

    function renderPhase(phase) {
        const $fragment = cloneTemplate("planning-phase-template");
        const $phase = $fragment.find(".planning-phase");
        const $stepList = $fragment.find(".planning-step-list");

        $phase.attr("data-phase-id", phase.id);

        $fragment
            .find(".planning-phase-position")
            .text(`Phase ${phase.position}`);

        $fragment
            .find(".planning-phase-title")
            .text(phase.title || "Untitled phase");

        $fragment
            .find(".planning-phase-status")
            .addClass(statusClass(phase.status))
            .text(phase.status_label || phase.status || "Unknown");

        const $description = $fragment.find(
            ".planning-phase-description"
        );

        if (phase.description) {
            $description.text(phase.description);
        } else {
            $description.addClass("d-none");
        }

        const stepCount = phase.step_count || 0;

        $fragment
            .find(".planning-phase-summary")
            .text(`${stepCount} step${stepCount === 1 ? "" : "s"}`);

        if (Array.isArray(phase.steps) && phase.steps.length) {
            phase.steps.forEach(function(step) {
                $stepList.append(renderStep(step));
            });
        } else {
            $stepList.append(
                $("<div>", {
                    class: "px-3 py-3 text-muted small",
                    text: "No implementation steps are defined.",
                })
            );
        }

        return $fragment;
    }

    function renderInitiative(initiative) {
        const $fragment = cloneTemplate(
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

        $fragment
            .find(".planning-initiative-position")
            .text(`Initiative ${initiative.position}`);

        $fragment
            .find(".planning-initiative-title")
            .text(initiative.title || "Untitled initiative");

        $fragment
            .find(".planning-initiative-status")
            .addClass(statusClass(initiative.status))
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
                .text(`Owner: ${initiative.created_by.display_name}`);
        }

        if (initiative.updated_at) {
            $fragment
                .find(".planning-initiative-updated")
                .text(`Updated ${formatDate(initiative.updated_at)}`);
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
                    text: "No phases are defined for this initiative.",
                })
            );
        }

        return $fragment;
    }

    function renderPlanningPayload(payload) {
        const projects = payload.projects || [];
        const activeProject = payload.active_project || null;
        const initiatives = payload.initiatives || [];
        const $initiativeList = $("#planning-initiative-list");

        renderProjectSelector(projects, activeProject);

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

        if (!initiatives.length) {
            renderInitiativeSelector([], null);
            showEmptyState();
            return;
        }

        const selectedInitiative = renderInitiativeSelector(
            initiatives,
            activeInitiativeId
        );

        if (!selectedInitiative) {
            showEmptyState();
            return;
        }

        $initiativeList.append(
            renderInitiative(selectedInitiative)
        );

        const initiativeCount = initiatives.length;
        const phaseCount = selectedInitiative.phase_count || 0;
        const stepCount = (selectedInitiative.phases || []).reduce(
            function(total, phase) {
                return total + (phase.step_count || 0);
            },
            0
        );

        const projectTitle = activeProject
            ? activeProject.title
            : "No Project";

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
                + `showing ${selectedInitiative.title}.`
            );
    }
// ======================================================================
// END: PLANNING_HIERARCHY_RENDERERS (PATCH 3 OF 7)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 4 OF 7)
// START: PLANNING_DATA_LOADER
// ======================================================================
    function loadPlanningData(projectSlug) {
        const endpoint = planningEndpoints.planning_endpoint;
        const requestedProjectSlug = (
            projectSlug
            || activeProjectSlug
            || ""
        );

        if (!endpoint) {
            showError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (planningRequest) {
            planningRequest.abort();
        }

        setLoadingState(true);

        $("#planning-error-state").addClass("d-none");

        $("#planning-empty-state")
            .addClass("d-none")
            .removeClass("d-flex");

        $("#planning-status-bar")
            .removeClass("text-danger text-success")
            .addClass("text-muted")
            .text("Loading persisted execution plans...");

        planningRequest = $.ajax({
            url: endpoint,
            method: "GET",
            dataType: "json",
            data: requestedProjectSlug
                ? {
                    project: requestedProjectSlug,
                }
                : {},
        })
            .done(function(response) {
                if (!response || response.status !== "success") {
                    showError(
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                renderPlanningPayload(response);
            })
            .fail(function(xhr, textStatus) {
                if (textStatus === "abort") {
                    return;
                }

                let message = "The planning request failed.";

                if (
                    xhr.responseJSON
                    && xhr.responseJSON.error
                ) {
                    message = xhr.responseJSON.error;
                } else if (xhr.status) {
                    message += ` HTTP ${xhr.status}.`;
                }

                showError(message);
            })
            .always(function() {
                planningRequest = null;
                setLoadingState(false);
            });
    }
// ======================================================================
// END: PLANNING_DATA_LOADER (PATCH 4 OF 7)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 5 OF 7)
// START: INITIATIVE_CREATION_CONTROLLER
// ======================================================================
    function clearInitiativeFormError() {
        $("#planning-initiative-form-error")
            .addClass("d-none")
            .empty();
    }

    function showInitiativeFormError(message, fieldErrors) {
        const errors = [];

        if (fieldErrors) {
            Object.keys(fieldErrors).forEach(function(fieldName) {
                errors.push(fieldErrors[fieldName]);
            });
        }

        $("#planning-initiative-form-error")
            .removeClass("d-none")
            .text(
                errors.length
                    ? errors.join(" ")
                    : message || "The Initiative could not be saved."
            );
    }

    function resetInitiativeForm() {
        const form = document.getElementById(
            "planning-initiative-form"
        );

        if (form) {
            form.reset();
        }

        $("#planning-initiative-status").val("PLANNED");
        clearInitiativeFormError();
    }

    function openInitiativeForm() {
        if (!activeProjectSlug) {
            showError(
                "Select an active Project before creating an Initiative."
            );
            return;
        }

        resetInitiativeForm();

        $("#planning-initiative-form-panel")
            .removeClass("d-none");

        $("#planning-initiative-title").trigger("focus");
    }

    function closeInitiativeForm() {
        resetInitiativeForm();

        $("#planning-initiative-form-panel")
            .addClass("d-none");
    }

    function setInitiativeSaveState(isSaving) {
        $("#planning-save-initiative-btn")
            .prop("disabled", isSaving)
            .text(isSaving ? "Saving..." : "Save Initiative");

        $("#planning-cancel-initiative-btn")
            .prop("disabled", isSaving);

        $("#planning-initiative-form")
            .find("input, textarea, select, button[type='reset']")
            .prop("disabled", isSaving);
    }

    function createInitiative() {
        const endpoint = planningEndpoints.planning_endpoint;
        const title = $("#planning-initiative-title").val().trim();

        clearInitiativeFormError();

        if (!endpoint) {
            showInitiativeFormError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!activeProjectSlug) {
            showInitiativeFormError(
                "Select an active Project before creating an Initiative."
            );
            return;
        }

        if (!title) {
            showInitiativeFormError(
                "Initiative title is required.",
                {
                    title: "Enter an Initiative title.",
                }
            );

            $("#planning-initiative-title").trigger("focus");
            return;
        }

        if (initiativeRequest) {
            return;
        }

        setInitiativeSaveState(true);

        initiativeRequest = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCsrfToken(),
            },
            data: JSON.stringify({
                operation: "create_initiative",
                project_slug: activeProjectSlug,
                title: title,
                description: $("#planning-initiative-description")
                    .val()
                    .trim(),
                status: $("#planning-initiative-status").val(),
            }),
        })
            .done(function(response) {
                if (!response || response.status !== "success") {
                    showInitiativeFormError(
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                closeInitiativeForm();
                loadPlanningData(activeProjectSlug);
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                showInitiativeFormError(
                    response.message || "The Initiative request failed.",
                    response.field_errors
                );
            })
            .always(function() {
                initiativeRequest = null;
                setInitiativeSaveState(false);
            });
    }
// ======================================================================
// END: INITIATIVE_CREATION_CONTROLLER (PATCH 5 OF 7)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 6 OF 7)
// START: PHASE_AND_STEP_CREATION_CONTROLLERS
// ======================================================================
    function clearPhaseFormError($initiative) {
        $initiative
            .find(".planning-phase-form-error")
            .addClass("d-none")
            .empty();
    }

    function showPhaseFormError(
        $initiative,
        message,
        fieldErrors
    ) {
        const errors = [];

        if (fieldErrors) {
            Object.keys(fieldErrors).forEach(function(fieldName) {
                errors.push(fieldErrors[fieldName]);
            });
        }

        $initiative
            .find(".planning-phase-form-error")
            .removeClass("d-none")
            .text(
                errors.length
                    ? errors.join(" ")
                    : message || "The Phase could not be saved."
            );
    }

    function resetPhaseForm($initiative) {
        const form = $initiative
            .find(".planning-phase-form")
            .get(0);

        if (form) {
            form.reset();
        }

        $initiative
            .find(".planning-phase-form-status")
            .val("PLANNED");

        clearPhaseFormError($initiative);
    }

    function openPhaseForm($initiative) {
        $(".planning-initiative").each(function() {
            const $otherInitiative = $(this);

            if (!$otherInitiative.is($initiative)) {
                closePhaseForm($otherInitiative);
            }
        });

        resetPhaseForm($initiative);

        $initiative
            .find(".planning-phase-form-panel")
            .removeClass("d-none");

        $initiative
            .find(".planning-phase-form-title")
            .trigger("focus");
    }

    function closePhaseForm($initiative) {
        resetPhaseForm($initiative);

        $initiative
            .find(".planning-phase-form-panel")
            .addClass("d-none");
    }

    function setPhaseSaveState($initiative, isSaving) {
        $initiative
            .find(".planning-save-phase-btn")
            .prop("disabled", isSaving)
            .text(isSaving ? "Saving..." : "Save Phase");

        $initiative
            .find(".planning-cancel-phase-btn")
            .prop("disabled", isSaving);

        $initiative
            .find(".planning-phase-form")
            .find("input, textarea, select, button[type='reset']")
            .prop("disabled", isSaving);
    }

    function createPhase($initiative) {
        const endpoint = planningEndpoints.planning_endpoint;
        const initiativeId = $initiative.data("initiative-id");

        const title = $initiative
            .find(".planning-phase-form-title")
            .val()
            .trim();

        clearPhaseFormError($initiative);

        if (!endpoint) {
            showPhaseFormError(
                $initiative,
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!initiativeId) {
            showPhaseFormError(
                $initiative,
                "The parent Initiative could not be identified."
            );
            return;
        }

        if (!title) {
            showPhaseFormError(
                $initiative,
                "Phase title is required.",
                {
                    title: "Enter a Phase title.",
                }
            );

            $initiative
                .find(".planning-phase-form-title")
                .trigger("focus");

            return;
        }

        if (phaseRequest) {
            return;
        }

        setPhaseSaveState($initiative, true);

        phaseRequest = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCsrfToken(),
            },
            data: JSON.stringify({
                operation: "create_phase",
                initiative_id: initiativeId,
                title: title,
                description: $initiative
                    .find(".planning-phase-form-description")
                    .val()
                    .trim(),
                status: $initiative
                    .find(".planning-phase-form-status")
                    .val(),
            }),
        })
            .done(function(response) {
                if (!response || response.status !== "success") {
                    showPhaseFormError(
                        $initiative,
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                closePhaseForm($initiative);
                loadPlanningData();
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                showPhaseFormError(
                    $initiative,
                    response.message || "The Phase request failed.",
                    response.field_errors
                );
            })
            .always(function() {
                phaseRequest = null;
                setPhaseSaveState($initiative, false);
            });
    }

    function clearStepFormError($phase) {
        $phase
            .find(".planning-step-form-error")
            .addClass("d-none")
            .empty();
    }

    function showStepFormError(
        $phase,
        message,
        fieldErrors
    ) {
        const errors = [];

        if (fieldErrors) {
            Object.keys(fieldErrors).forEach(function(fieldName) {
                errors.push(fieldErrors[fieldName]);
            });
        }

        $phase
            .find(".planning-step-form-error")
            .removeClass("d-none")
            .text(
                errors.length
                    ? errors.join(" ")
                    : message || "The Step could not be saved."
            );
    }

    function resetStepForm($phase) {
        const form = $phase
            .find(".planning-step-form")
            .get(0);

        if (form) {
            form.reset();
        }

        $phase
            .find(".planning-step-form-status")
            .val("PLANNED");

        $phase
            .find(".planning-step-form-estimate-confidence")
            .val("");

        clearStepFormError($phase);
    }

    function openStepForm($phase) {
        $(".planning-phase").each(function() {
            const $otherPhase = $(this);

            if (!$otherPhase.is($phase)) {
                closeStepForm($otherPhase);
            }
        });

        resetStepForm($phase);

        $phase
            .find(".planning-step-form-panel")
            .removeClass("d-none");

        $phase
            .find(".planning-step-form-title")
            .trigger("focus");
    }

    function closeStepForm($phase) {
        resetStepForm($phase);

        $phase
            .find(".planning-step-form-panel")
            .addClass("d-none");
    }

    function setStepSaveState($phase, isSaving) {
        $phase
            .find(".planning-save-step-btn")
            .prop("disabled", isSaving)
            .text(isSaving ? "Saving..." : "Save Step");

        $phase
            .find(".planning-cancel-step-btn")
            .prop("disabled", isSaving);

        $phase
            .find(".planning-step-form")
            .find("input, textarea, select, button[type='reset']")
            .prop("disabled", isSaving);
    }

    function createStep($phase) {
        const endpoint = planningEndpoints.planning_endpoint;
        const phaseId = $phase.data("phase-id");

        const title = $phase
            .find(".planning-step-form-title")
            .val()
            .trim();

        clearStepFormError($phase);

        if (!endpoint) {
            showStepFormError(
                $phase,
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!phaseId) {
            showStepFormError(
                $phase,
                "The parent Phase could not be identified."
            );
            return;
        }

        if (!title) {
            showStepFormError(
                $phase,
                "Step title is required.",
                {
                    title: "Enter a Step title.",
                }
            );

            $phase
                .find(".planning-step-form-title")
                .trigger("focus");

            return;
        }

        if (stepRequest) {
            return;
        }

        setStepSaveState($phase, true);

        stepRequest = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCsrfToken(),
            },
            data: JSON.stringify({
                operation: "create_step",
                phase_id: phaseId,
                title: title,
                description: $phase
                    .find(".planning-step-form-description")
                    .val()
                    .trim(),
                status: $phase
                    .find(".planning-step-form-status")
                    .val(),
                estimated_minutes: $phase
                    .find(".planning-step-form-estimated-minutes")
                    .val(),
                estimate_confidence: $phase
                    .find(".planning-step-form-estimate-confidence")
                    .val(),
                validation_description: $phase
                    .find(
                        ".planning-step-form-validation-description"
                    )
                    .val()
                    .trim(),
            }),
        })
            .done(function(response) {
                if (!response || response.status !== "success") {
                    showStepFormError(
                        $phase,
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                closeStepForm($phase);
                loadPlanningData();
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                showStepFormError(
                    $phase,
                    response.message || "The Step request failed.",
                    response.field_errors
                );
            })
            .always(function() {
                stepRequest = null;
                setStepSaveState($phase, false);
            });
    }
// ======================================================================
// END: PHASE_AND_STEP_CREATION_CONTROLLERS (PATCH 6 OF 7)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 7 OF 7)
// START: PLANNING_EVENT_BINDINGS_AND_PUBLIC_API
// ======================================================================
    function bindPlanningEvents() {
        $("#planning-project-select")
            .off("change.planning")
            .on("change.planning", function() {
                activeProjectSlug = $(this).val() || null;
                activeInitiativeId = null;

                closeInitiativeForm();
                loadPlanningData(activeProjectSlug);
            });

        $("#planning-initiative-select")
            .off("change.planning")
            .on("change.planning", function() {
                const selectedValue = $(this).val();

                activeInitiativeId = selectedValue
                    ? Number(selectedValue)
                    : null;

                closeInitiativeForm();
                loadPlanningData(activeProjectSlug);
            });

        $("#planning-refresh-btn")
            .off("click.planning")
            .on("click.planning", function() {
                loadPlanningData(activeProjectSlug);
            });

        $(
            "#planning-create-initiative-btn, "
            + "#planning-empty-create-initiative-btn"
        )
            .off("click.planning")
            .on("click.planning", function() {
                openInitiativeForm();
            });

        $("#planning-cancel-initiative-btn")
            .off("click.planning")
            .on("click.planning", function() {
                closeInitiativeForm();
            });

        $("#planning-initiative-form")
            .off("submit.planning")
            .on("submit.planning", function(event) {
                event.preventDefault();
                createInitiative();
            })
            .off("reset.planning")
            .on("reset.planning", function() {
                clearInitiativeFormError();

                window.setTimeout(function() {
                    $("#planning-initiative-status").val("PLANNED");
                }, 0);
            });

        $("#planning-initiative-list")
            .off("click.planningPhase")
            .on(
                "click.planningPhase",
                ".planning-new-phase-btn",
                function() {
                    const $initiative = $(this).closest(
                        ".planning-initiative"
                    );

                    openPhaseForm($initiative);
                }
            )
            .on(
                "click.planningPhase",
                ".planning-cancel-phase-btn",
                function() {
                    const $initiative = $(this).closest(
                        ".planning-initiative"
                    );

                    closePhaseForm($initiative);
                }
            )
            .off("submit.planningPhase")
            .on(
                "submit.planningPhase",
                ".planning-phase-form",
                function(event) {
                    event.preventDefault();

                    const $initiative = $(this).closest(
                        ".planning-initiative"
                    );

                    createPhase($initiative);
                }
            )
            .off("reset.planningPhase")
            .on(
                "reset.planningPhase",
                ".planning-phase-form",
                function() {
                    const $initiative = $(this).closest(
                        ".planning-initiative"
                    );

                    clearPhaseFormError($initiative);

                    window.setTimeout(function() {
                        $initiative
                            .find(".planning-phase-form-status")
                            .val("PLANNED");
                    }, 0);
                }
            )
            .off("click.planningStep")
            .on(
                "click.planningStep",
                ".planning-new-step-btn",
                function() {
                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    openStepForm($phase);
                }
            )
            .on(
                "click.planningStep",
                ".planning-cancel-step-btn",
                function() {
                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    closeStepForm($phase);
                }
            )
            .off("submit.planningStep")
            .on(
                "submit.planningStep",
                ".planning-step-form",
                function(event) {
                    event.preventDefault();

                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    createStep($phase);
                }
            )
            .off("reset.planningStep")
            .on(
                "reset.planningStep",
                ".planning-step-form",
                function() {
                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    clearStepFormError($phase);

                    window.setTimeout(function() {
                        $phase
                            .find(".planning-step-form-status")
                            .val("PLANNED");

                        $phase
                            .find(
                                ".planning-step-form-estimate-confidence"
                            )
                            .val("");
                    }, 0);
                }
            );
    }

    window.initPlanningConsole = function(systemEndpoints) {
        planningEndpoints = systemEndpoints || {};

        if (!planningInitialized) {
            bindPlanningEvents();
            planningInitialized = true;
        }

        loadPlanningData(activeProjectSlug);
    };

    window.refreshPlanningConsole = function() {
        if (!planningInitialized) {
            return;
        }

        loadPlanningData(activeProjectSlug);
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_EVENT_BINDINGS_AND_PUBLIC_API (PATCH 7 OF 7)
// ======================================================================