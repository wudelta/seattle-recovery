// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 1 OF 8)
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
    let activeInitiative = null;

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
            activeInitiative = null;

            $projectSelect
                .append(
                    $("<option>", {
                        value: "",
                        text: "No active projects",
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
// ======================================================================
// END: PLANNING_STATE_AND_SHARED_UTILITIES (PATCH 1 OF 8)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 2 OF 8)
// START: PLANNING_WORKSPACE_STATE
// ======================================================================
    function setWorkbenchHeader(title, context, status) {
        $("#planning-workbench-title").text(
            title || "Decision Engine"
        );

        $("#planning-workbench-context").text(
            context || "Select a Project and Initiative to begin."
        );

        const $status = $("#planning-workbench-status");

        $status.empty();

        if (status) {
            $status.append(
                $("<span>", {
                    class: `badge ${statusClass(status.value)}`,
                    text: status.label || status.value,
                })
            );
        }
    }

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

    function renderNavigatorProject(project, initiativeCount) {
        const $projectButton = $("#planning-navigator-project");

        if (!project) {
            $projectButton
                .removeClass("is-active")
                .prop("disabled", true);

            $("#planning-navigator-project-title")
                .text("No active Project");

            $("#planning-navigator-project-meta")
                .text("Create or activate a Project to begin");

            return;
        }

        $("#planning-navigator-project-title")
            .text(project.title || "Untitled Project");

        $("#planning-navigator-project-meta")
            .text(
                `${initiativeCount} initiative`
                + `${initiativeCount === 1 ? "" : "s"}`
            );

        $projectButton
            .addClass("is-active")
            .prop("disabled", false);
    }

    function renderNavigatorInitiatives(
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

        initiatives.forEach(function(initiative) {
            const initiativeId = String(initiative.id);
            const selectedId = selectedInitiativeId !== null
                && selectedInitiativeId !== undefined
                ? String(selectedInitiativeId)
                : null;

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
                    isActive: initiativeId === selectedId,
                })
            );
        });
    }

    function resetNavigator() {
        renderNavigatorProject(null, 0);
        renderNavigatorInitiatives([], null);

        setWorkbenchHeader(
            "Decision Engine",
            "Select a Project and Initiative to begin.",
            null
        );
    }

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

        setWorkbenchHeader(
            "Decision Engine unavailable",
            message || "Planning data could not be loaded.",
            null
        );
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

        setWorkbenchHeader(
            "No active Initiative",
            "Create an Initiative for the selected Project.",
            null
        );
    }
// ======================================================================
// END: PLANNING_WORKSPACE_STATE (PATCH 2 OF 8)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 3 OF 8)
// START: PLANNING_HIERARCHY_RENDERERS
// ======================================================================
    function renderStep(step) {
        const $fragment = cloneTemplate("planning-step-template");
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
        $phase.data("phase", phase);

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

        const stepCount = Array.isArray(phase.steps)
            ? phase.steps.length
            : phase.step_count || 0;

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
        const initiativeOptions = payload.initiative_options || [];
        const renderedInitiative = payload.active_initiative || null;
        const summary = payload.summary || {};
        const $initiativeList = $("#planning-initiative-list");

        renderProjectSelector(projects, activeProject);

        renderNavigatorProject(
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

        if (!initiativeOptions.length || !renderedInitiative) {
            activeInitiativeId = null;
            activeInitiative = null;

            renderNavigatorInitiatives([], null);

            showEmptyState();
            return;
        }

        activeInitiativeId = renderedInitiative.id;
        activeInitiative = renderedInitiative;

        renderNavigatorInitiatives(
            initiativeOptions,
            activeInitiativeId
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

        setWorkbenchHeader(
            renderedInitiative.title || "Untitled Initiative",
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
// ======================================================================
// END: PLANNING_HIERARCHY_RENDERERS (PATCH 3 OF 8)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 4 OF 8)
// START: PLANNING_DATA_LOADER
// ======================================================================
    function loadPlanningData(projectSlug, initiativeId) {
        const endpoint = planningEndpoints.planning_endpoint;
        const requestedProjectSlug = (
            projectSlug
            || activeProjectSlug
            || ""
        );
        const requestedInitiativeId = (
            initiativeId
            || activeInitiativeId
            || ""
        );
        const requestData = {};

        if (!endpoint) {
            showError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (requestedProjectSlug) {
            requestData.project = requestedProjectSlug;
        }

        if (requestedInitiativeId) {
            requestData.initiative = requestedInitiativeId;
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
            .text("Loading persisted execution plan...");

        setWorkbenchHeader(
            "Loading Decision Engine",
            (
                requestedProjectSlug
                    ? `Opening ${requestedProjectSlug}...`
                    : "Resolving active Project context..."
            ),
            null
        );

        planningRequest = $.ajax({
            url: endpoint,
            method: "GET",
            dataType: "json",
            data: requestData,
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
// END: PLANNING_DATA_LOADER (PATCH 4 OF 8)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 5 OF 8)
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

        $("#planning-initiative-form")
            .removeAttr("data-initiative-id");

        $("#planning-initiative-status").val("PLANNED");
        clearInitiativeFormError();
    }

    function openInitiativeForm(initiative) {
        if (!activeProjectSlug) {
            showError(
                "Select an active Project before creating an Initiative."
            );
            return;
        }

        resetInitiativeForm();

        if (initiative && initiative.id) {
            $("#planning-initiative-form")
                .attr("data-initiative-id", initiative.id);

            $("#planning-initiative-title")
                .val(initiative.title || "");

            $("#planning-initiative-description")
                .val(initiative.description || "");

            $("#planning-initiative-status")
                .val(initiative.status || "PLANNED");
        }

        $("#planning-workspace")
            .addClass("d-none");

        $("#planning-initiative-form-panel")
            .removeClass("d-none flex-shrink-0")
            .addClass("flex-grow-1 overflow-auto")
            .css("min-height", 0)
            .scrollTop(0);

        $("#planning-initiative-title").trigger("focus");
    }

    function closeInitiativeForm() {
        resetInitiativeForm();

        $("#planning-initiative-form-panel")
            .addClass("d-none")
            .removeClass("flex-grow-1 overflow-auto")
            .addClass("flex-shrink-0")
            .css("min-height", "");

        $("#planning-workspace")
            .removeClass("d-none");
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

    function saveInitiative() {
        const endpoint = planningEndpoints.planning_endpoint;
        const initiativeId = Number(
            $("#planning-initiative-form")
                .attr("data-initiative-id")
        ) || null;

        const title = $("#planning-initiative-title")
            .val()
            .trim();

        clearInitiativeFormError();

        if (!endpoint) {
            showInitiativeFormError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!activeProjectSlug) {
            showInitiativeFormError(
                "Select an active Project before saving an Initiative."
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
                operation: "save_initiative",
                initiative_id: initiativeId,
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

                const savedInitiative = (
                    response.initiative
                    || response.active_initiative
                    || null
                );

                if (savedInitiative && savedInitiative.id) {
                    activeInitiativeId = savedInitiative.id;
                }

                closeInitiativeForm();

                loadPlanningData(
                    activeProjectSlug,
                    activeInitiativeId
                );
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
// END: INITIATIVE_CREATION_CONTROLLER (PATCH 5 OF 8)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 6 OF 8)
// START: PHASE_CREATION_CONTROLLER
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
        const $form = $initiative.find(".planning-phase-form");
        const form = $form.get(0);

        if (form) {
            form.reset();
        }

        $form.attr("data-phase-id", "");

        $initiative
            .find(".planning-phase-form-status")
            .val("PLANNED");

        $initiative
            .find(".planning-phase-form-heading")
            .text("Create Phase");

        $initiative
            .find(".planning-phase-form-guidance")
            .text("Add an ordered milestone to this Initiative.");

        clearPhaseFormError($initiative);
    }

    function openPhaseForm($initiative, phase) {
        $(".planning-initiative").each(function() {
            const $otherInitiative = $(this);

            if (!$otherInitiative.is($initiative)) {
                closePhaseForm($otherInitiative);
            }
        });

        resetPhaseForm($initiative);

        if (phase) {
            $initiative
                .find(".planning-phase-form")
                .attr("data-phase-id", phase.id);

            $initiative
                .find(".planning-phase-form-title")
                .val(phase.title || "");

            $initiative
                .find(".planning-phase-form-description")
                .val(phase.description || "");

            $initiative
                .find(".planning-phase-form-status")
                .val(phase.status || "PLANNED");

            $initiative
                .find(".planning-phase-form-heading")
                .text("Edit Phase");

            $initiative
                .find(".planning-phase-form-guidance")
                .text("Revise this milestone and save the changes.");
        }

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

    function savePhase($initiative) {
        const endpoint = planningEndpoints.planning_endpoint;
        const initiativeId = $initiative.data("initiative-id");
        const phaseId = $initiative
            .find(".planning-phase-form")
            .attr("data-phase-id");

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
                operation: "save_phase",
                initiative_id: initiativeId,
                phase_id: phaseId || null,
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
// ======================================================================
// END: PHASE_CREATION_CONTROLLER (PATCH 6 OF 8)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 7 OF 8)
// START: STEP_CREATION_CONTROLLER
// ======================================================================
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
        const $form = $phase.find(".planning-step-form");
        const form = $form.get(0);

        if (form) {
            form.reset();
        }

        $form.attr("data-step-id", "");

        $phase
            .find(".planning-step-form-status")
            .val("PLANNED");

        $phase
            .find(".planning-step-form-estimate-confidence")
            .val("");

        clearStepFormError($phase);
    }

    function openStepForm($phase, step) {
        $(".planning-phase").each(function() {
            const $otherPhase = $(this);

            if (!$otherPhase.is($phase)) {
                closeStepForm($otherPhase);
            }
        });

        resetStepForm($phase);

        if (step) {
            $phase
                .find(".planning-step-form")
                .attr("data-step-id", step.id);

            $phase
                .find(".planning-step-form-title")
                .val(step.title || "");

            $phase
                .find(".planning-step-form-description")
                .val(step.description || "");

            $phase
                .find(".planning-step-form-status")
                .val(step.status || "PLANNED");

            $phase
                .find(".planning-step-form-estimated-minutes")
                .val(
                    step.estimated_minutes === null
                        || step.estimated_minutes === undefined
                        ? ""
                        : step.estimated_minutes
                );

            $phase
                .find(".planning-step-form-estimate-confidence")
                .val(step.estimate_confidence || "");

            $phase
                .find(".planning-step-form-validation-description")
                .val(step.validation_description || "");
        }

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

    function saveStep($phase) {
        const endpoint = planningEndpoints.planning_endpoint;
        const phaseId = $phase.data("phase-id");
        const stepId = $phase
            .find(".planning-step-form")
            .attr("data-step-id");

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
                operation: "save_step",
                phase_id: phaseId,
                step_id: stepId || null,
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
// END: STEP_CREATION_CONTROLLER (PATCH 7 OF 8)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 8 OF 8)
// START: PLANNING_EVENT_BINDINGS_AND_PUBLIC_API
// ======================================================================
    function bindPlanningEvents() {
        $("#planning-project-select")
            .off("change.planning")
            .on("change.planning", function() {
                activeProjectSlug = $(this).val() || null;
                activeInitiativeId = null;
                activeInitiative = null;

                closeInitiativeForm();
                loadPlanningData(activeProjectSlug);
            });

        $("#planning-refresh-btn")
            .off("click.planning")
            .on("click.planning", function() {
                loadPlanningData(
                    activeProjectSlug,
                    activeInitiativeId
                );
            });

        $("#planning-navigator-initiative-list")
            .off("click.planningNavigator")
            .on(
                "click.planningNavigator",
                ".planning-navigator-item[data-item-type='initiative']",
                function() {
                    const selectedInitiativeId = Number(
                        $(this).attr("data-record-id")
                    );

                    if (
                        !selectedInitiativeId
                        || selectedInitiativeId === activeInitiativeId
                    ) {
                        return;
                    }

                    activeInitiativeId = selectedInitiativeId;
                    activeInitiative = null;

                    closeInitiativeForm();

                    loadPlanningData(
                        activeProjectSlug,
                        activeInitiativeId
                    );
                }
            );

        $(
            "#planning-create-initiative-btn, "
            + "#planning-empty-create-initiative-btn"
        )
            .off("click.planning")
            .on("click.planning", function() {
                openInitiativeForm(null);
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
                saveInitiative();
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
                ".planning-edit-initiative-btn",
                function() {
                    openInitiativeForm(activeInitiative);
                }
            )
            .on(
                "click.planningPhase",
                ".planning-new-phase-btn",
                function() {
                    const $initiative = $(this).closest(
                        ".planning-initiative"
                    );

                    openPhaseForm($initiative, null);
                }
            )
            .on(
                "click.planningPhase",
                ".planning-edit-phase-btn",
                function() {
                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    const $initiative = $phase.closest(
                        ".planning-initiative"
                    );

                    openPhaseForm(
                        $initiative,
                        $phase.data("phase")
                    );
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

                    savePhase($initiative);
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

                    openStepForm($phase, null);
                }
            )
            .on(
                "click.planningStep",
                ".planning-edit-step-btn",
                function() {
                    const $step = $(this).closest(
                        ".planning-step"
                    );

                    const $phase = $step.closest(
                        ".planning-phase"
                    );

                    openStepForm(
                        $phase,
                        $step.data("step")
                    );
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

                    saveStep($phase);
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
            resetNavigator();
            bindPlanningEvents();
            planningInitialized = true;
        }

        loadPlanningData(
            activeProjectSlug,
            activeInitiativeId
        );
    };

    window.refreshPlanningConsole = function() {
        if (!planningInitialized) {
            return;
        }

        loadPlanningData(
            activeProjectSlug,
            activeInitiativeId
        );
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_EVENT_BINDINGS_AND_PUBLIC_API (PATCH 8 OF 8)
// ======================================================================