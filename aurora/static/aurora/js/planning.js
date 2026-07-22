// ======================================================================
// FILE: aurora/static/aurora/js/planning.js (PATCH 1 OF 1)
// START: PLANNING_CONSOLE_CONTROLLER
// ======================================================================
(function(window, $) {
    "use strict";

    let planningInitialized = false;
    let planningEndpoints = {};
    let planningRequest = null;

    const STATUS_CLASSES = {
        PLANNED: "bg-secondary text-light",
        ACTIVE: "bg-primary text-light",
        PAUSED: "bg-warning text-dark",
        COMPLETED: "bg-success text-light",
        CANCELLED: "bg-danger text-light",
    };

    function escapeHtml(value) {
        return $("<div>").text(value || "").html();
    }

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

    function bindPlanningEvents() {
        $("#planning-refresh-btn")
            .off("click.planning")
            .on("click.planning", function() {
                loadPlanningData();
            });
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
// END: PLANNING_CONSOLE_CONTROLLER (PATCH 1 OF 1)
// ======================================================================