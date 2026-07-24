// ======================================================================
// FILE: aurora/static/aurora/js/planning/phases.js
// START: PHASE_CREATION_CONTROLLER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const utilities = Planning.utilities;
    const data = Planning.data;

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
        const $form = $initiative.find(
            ".planning-phase-form"
        );

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
                .text(
                    "Revise this milestone and save the changes."
                );
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
            .find(
                "input, textarea, select, button[type='reset']"
            )
            .prop("disabled", isSaving);
    }

    function setPhaseDeleteState($phase, isDeleting) {
        $phase
            .find(".planning-delete-phase-btn")
            .prop("disabled", isDeleting)
            .text(isDeleting ? "Deleting..." : "Delete Phase");

        $phase
            .find(
                ".planning-edit-phase-btn, "
                + ".planning-new-step-btn"
            )
            .prop("disabled", isDeleting);
    }

    function savePhase($initiative) {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;
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

        if (state.getRequest("phase")) {
            return;
        }

        setPhaseSaveState($initiative, true);

        const request = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": utilities.getCsrfToken(),
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
                if (
                    !response
                    || response.status !== "success"
                ) {
                    showPhaseFormError(
                        $initiative,
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                closePhaseForm($initiative);

                data.loadPlanningData(
                    state.getActiveProjectSlug(),
                    state.getActiveInitiativeId()
                );
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
                state.setRequest("phase", null);
                setPhaseSaveState($initiative, false);
            });

        state.setRequest("phase", request);
    }

    function deletePhase($phase) {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;
        const phase = $phase.data("phase") || {};
        const phaseId = phase.id || $phase.data("phase-id");
        const phaseTitle = phase.title || "this Phase";
        const $initiative = $phase.closest(
            ".planning-initiative"
        );

        clearPhaseFormError($initiative);

        if (!endpoint) {
            showPhaseFormError(
                $initiative,
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!phaseId) {
            showPhaseFormError(
                $initiative,
                "The selected Phase could not be identified."
            );
            return;
        }

        if (
            !window.confirm(
                `Delete "${phaseTitle}" and all of its Steps? `
                + "This cannot be undone."
            )
        ) {
            return;
        }

        if (state.getRequest("phase")) {
            return;
        }

        setPhaseDeleteState($phase, true);

        const request = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": utilities.getCsrfToken(),
            },
            data: JSON.stringify({
                operation: "delete_phase",
                phase_id: phaseId,
            }),
        })
            .done(function(response) {
                if (
                    !response
                    || response.status !== "success"
                ) {
                    showPhaseFormError(
                        $initiative,
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                data.loadPlanningData(
                    state.getActiveProjectSlug(),
                    state.getActiveInitiativeId()
                );
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                showPhaseFormError(
                    $initiative,
                    response.message || "The Phase deletion failed.",
                    response.field_errors
                );
            })
            .always(function() {
                state.setRequest("phase", null);
                setPhaseDeleteState($phase, false);
            });

        state.setRequest("phase", request);
    }

    Planning.phases = {
        clearFormError: clearPhaseFormError,
        openForm: openPhaseForm,
        closeForm: closePhaseForm,
        save: savePhase,
        delete: deletePhase,
    };
})(window, jQuery);
// ======================================================================
// END: PHASE_CREATION_CONTROLLER
// ======================================================================