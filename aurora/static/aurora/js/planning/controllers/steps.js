// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/steps.js
// START: STEP_CREATION_CONTROLLER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const utilities = Planning.utilities;
    const orchestrator = Planning.orchestrator;

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
        const $form = $phase.find(
            ".planning-step-form"
        );

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
                .find(
                    ".planning-step-form-validation-description"
                )
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
            .find(
                "input, textarea, select, button[type='reset']"
            )
            .prop("disabled", isSaving);
    }

    function setStepDeleteState($step, isDeleting) {
        $step
            .find(".planning-delete-step-btn")
            .prop("disabled", isDeleting)
            .text(isDeleting ? "Deleting..." : "Delete");

        $step
            .find(".planning-edit-step-btn")
            .prop("disabled", isDeleting);
    }

    function saveStep($phase) {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;
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

        if (state.getRequest("step")) {
            return;
        }

        setStepSaveState($phase, true);

        const request = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": utilities.getCsrfToken(),
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
                    .find(
                        ".planning-step-form-estimated-minutes"
                    )
                    .val(),
                estimate_confidence: $phase
                    .find(
                        ".planning-step-form-estimate-confidence"
                    )
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
                if (
                    !response
                    || response.status !== "success"
                ) {
                    showStepFormError(
                        $phase,
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                closeStepForm($phase);

                orchestrator.loadPlanningData(
                    state.getActiveProjectSlug(),
                    state.getActiveInitiativeId()
                );
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
                state.setRequest("step", null);
                setStepSaveState($phase, false);
            });

        state.setRequest("step", request);
    }

    function deleteStep($step) {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;
        const step = $step.data("step") || {};
        const stepId = step.id || $step.data("step-id");
        const stepTitle = step.title || "this Step";
        const $phase = $step.closest(".planning-phase");

        clearStepFormError($phase);

        if (!endpoint) {
            showStepFormError(
                $phase,
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!stepId) {
            showStepFormError(
                $phase,
                "The selected Step could not be identified."
            );
            return;
        }

        if (
            !window.confirm(
                `Delete "${stepTitle}"? This cannot be undone.`
            )
        ) {
            return;
        }

        if (state.getRequest("step")) {
            return;
        }

        setStepDeleteState($step, true);

        const request = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": utilities.getCsrfToken(),
            },
            data: JSON.stringify({
                operation: "delete_step",
                step_id: stepId,
            }),
        })
            .done(function(response) {
                if (
                    !response
                    || response.status !== "success"
                ) {
                    showStepFormError(
                        $phase,
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                orchestrator.loadPlanningData(
                    state.getActiveProjectSlug(),
                    state.getActiveInitiativeId()
                );
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                showStepFormError(
                    $phase,
                    response.message || "The Step deletion failed.",
                    response.field_errors
                );
            })
            .always(function() {
                state.setRequest("step", null);
                setStepDeleteState($step, false);
            });

        state.setRequest("step", request);
    }

    Planning.steps = {
        clearFormError: clearStepFormError,
        openForm: openStepForm,
        closeForm: closeStepForm,
        save: saveStep,
        delete: deleteStep,
    };
})(window, jQuery);
// ======================================================================
// END: STEP_CREATION_CONTROLLER
// ======================================================================