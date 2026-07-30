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

    function populateStepAssignees(
        $phase,
        selectedUserId
    ) {
        const $select = $phase.find(
            ".planning-step-form-assigned-to"
        );

        const users = state.getUsers() || [];

        $select
            .empty()
            .append(
                $("<option>", {
                    value: "",
                    text: "Select a user",
                })
            );

        users.forEach(function(user) {
            const userId = user.id;

            const label = (
                user.display_name
                || user.username
                || user.email
                || `User ${userId}`
            );

            $select.append(
                $("<option>", {
                    value: userId,
                    text: label,
                })
            );
        });

        $select.val(
            selectedUserId === null
            || selectedUserId === undefined
                ? ""
                : String(selectedUserId)
        );
    }

    function clearStepFileRows($phase) {
        if (
            Planning.stepEvents
            && Planning.stepEvents.clearFileRows
        ) {
            Planning.stepEvents.clearFileRows($phase);
            return;
        }

        $phase
            .find(".planning-step-form-file-list")
            .empty();

        $phase
            .find(".planning-step-form-file-empty")
            .removeClass("d-none");
    }

    function populateStepFileRows(
        $phase,
        fileKind,
        files
    ) {
        if (
            !Planning.stepEvents
            || !Planning.stepEvents.addFileRow
        ) {
            return;
        }

        (files || []).forEach(function(stepFile) {
            Planning.stepEvents.addFileRow(
                $phase,
                fileKind,
                stepFile
            );
        });
    }

    function collectStepFiles(
        $phase,
        fileKind
    ) {
        const files = [];
        const seenPaths = {};

        $phase
            .find(
                `.planning-step-form-file-row[data-file-kind="${fileKind}"]`
            )
            .each(function() {
                const $row = $(this);

                const filePath = $row
                    .find(".planning-step-form-file-path")
                    .val()
                    .trim();

                const reason = $row
                    .find(".planning-step-form-file-reason")
                    .val()
                    .trim();

                if (!filePath || seenPaths[filePath]) {
                    return;
                }

                seenPaths[filePath] = true;

                files.push({
                    file_path: filePath,
                    reason: reason,
                });
            });

        return files;
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

        clearStepFileRows($phase);
        populateStepAssignees($phase, null);
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

        populateStepAssignees(
            $phase,
            step ? step.assigned_to_id : null
        );

        if (step) {
            const document = step.document || {};
            const validation = step.validation || {};
            const plannedFiles = step.planned_files || [];
            const actualFiles = step.actual_files || [];

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
                    ".planning-step-form-technical-design"
                )
                .val(document.technical_design || "");

            $phase
                .find(
                    ".planning-step-form-dependencies"
                )
                .val(document.dependencies || "");

            $phase
                .find(
                    ".planning-step-form-assumptions"
                )
                .val(document.assumptions || "");

            $phase
                .find(
                    ".planning-step-form-implementation-notes"
                )
                .val(document.implementation_notes || "");

            $phase
                .find(
                    ".planning-step-form-discussion"
                )
                .val(document.discussion || "");

            populateStepFileRows(
                $phase,
                "planned",
                plannedFiles
            );

            populateStepFileRows(
                $phase,
                "actual",
                actualFiles
            );

            $phase
                .find(
                    ".planning-step-form-validation-description"
                )
                .val(
                    validation.description
                    || step.validation_description
                    || ""
                );
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
                "input, textarea, select, button"
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

        const assignedToId = $phase
            .find(".planning-step-form-assigned-to")
            .val();

        const plannedFiles = collectStepFiles(
            $phase,
            "planned"
        );

        const actualFiles = collectStepFiles(
            $phase,
            "actual"
        );

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

        if (!assignedToId) {
            showStepFormError(
                $phase,
                "Step assignee is required.",
                {
                    assigned_to_id: "Select a user.",
                }
            );

            $phase
                .find(".planning-step-form-assigned-to")
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
                assigned_to_id: assignedToId,
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
                document: {
                    technical_design: $phase
                        .find(
                            ".planning-step-form-technical-design"
                        )
                        .val()
                        .trim(),
                    dependencies: $phase
                        .find(
                            ".planning-step-form-dependencies"
                        )
                        .val()
                        .trim(),
                    assumptions: $phase
                        .find(
                            ".planning-step-form-assumptions"
                        )
                        .val()
                        .trim(),
                    implementation_notes: $phase
                        .find(
                            ".planning-step-form-implementation-notes"
                        )
                        .val()
                        .trim(),
                    discussion: $phase
                        .find(
                            ".planning-step-form-discussion"
                        )
                        .val()
                        .trim(),
                },
                validation: {
                    description: $phase
                        .find(
                            ".planning-step-form-validation-description"
                        )
                        .val()
                        .trim(),
                },
                planned_files: plannedFiles,
                actual_files: actualFiles,
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