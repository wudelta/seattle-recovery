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

            $stepList
                .children(".planning-step:last")
                .removeClass("border-bottom");
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
        const initiatives = payload.initiatives || [];
        const summary = payload.summary || {};
        const $initiativeList = $("#planning-initiative-list");

        $("#planning-error-state").addClass("d-none");

        $("#planning-empty-state")
            .addClass("d-none")
            .removeClass("d-flex");

        $initiativeList.empty();

        if (!initiatives.length) {
            showEmptyState();
            return;
        }

        initiatives.forEach(function(initiative) {
            $initiativeList.append(
                renderInitiative(initiative)
            );
        });

        const initiativeCount = summary.initiative_count || 0;
        const phaseCount = summary.phase_count || 0;
        const stepCount = summary.step_count || 0;

        $("#planning-summary-badge")
            .removeClass("text-danger text-info")
            .addClass("text-success")
            .text(
                `${initiativeCount} initiative`
                + `${initiativeCount === 1 ? "" : "s"} · `
                + `${phaseCount} phase`
                + `${phaseCount === 1 ? "" : "s"} · `
                + `${stepCount} step`
                + `${stepCount === 1 ? "" : "s"}`
            );

        $("#planning-status-bar")
            .removeClass("text-danger text-muted")
            .addClass("text-success")
            .text(
                `Decision Engine synchronized at `
                + `${new Date().toLocaleTimeString()}.`
            );
    }
// ======================================================================
// END: PLANNING_HIERARCHY_RENDERERS (PATCH 3 OF 7)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 4 OF 7)
// START: PLANNING_DATA_LOADER
// ======================================================================
    function loadPlanningData() {
        const endpoint = planningEndpoints.planning_endpoint;

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
                loadPlanningData();
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
// ======================================================================
// END: PHASE_CREATION_CONTROLLER (PATCH 6 OF 7)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 7 OF 7)
// START: PLANNING_EVENT_BINDINGS_AND_PUBLIC_API
// ======================================================================
    function bindPlanningEvents() {
        $("#planning-refresh-btn")
            .off("click.planning")
            .on("click.planning", function() {
                loadPlanningData();
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
            );
    }

    window.initPlanningConsole = function(
        systemEndpoints
    ) {
        planningEndpoints = systemEndpoints || {};

        if (!planningInitialized) {
            bindPlanningEvents();
            planningInitialized = true;
        }

        loadPlanningData();
    };

    window.refreshPlanningConsole = function() {
        if (!planningInitialized) {
            return;
        }

        loadPlanningData();
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_EVENT_BINDINGS_AND_PUBLIC_API (PATCH 7 OF 7)
// ======================================================================