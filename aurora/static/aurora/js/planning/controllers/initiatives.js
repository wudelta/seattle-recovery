// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/initiatives.js
// START: INITIATIVE_CREATION_CONTROLLER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const utilities = Planning.utilities;
    const workspace = Planning.workspace;
    const orchestrator = Planning.orchestrator;

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
        if (!state.getActiveProjectSlug()) {
            workspace.showError(
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

    function setInitiativeDeleteState(isDeleting) {
        $(".planning-delete-initiative-btn")
            .prop("disabled", isDeleting)
            .text(
                isDeleting
                    ? "Deleting..."
                    : "Delete Initiative"
            );
    }

    function saveInitiative() {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;
        const activeProjectSlug = state.getActiveProjectSlug();

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

        if (state.getRequest("initiative")) {
            return;
        }

        setInitiativeSaveState(true);

        const request = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": utilities.getCsrfToken(),
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
                if (
                    !response
                    || response.status !== "success"
                ) {
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
                    state.setActiveInitiativeId(
                        savedInitiative.id
                    );
                }

                closeInitiativeForm();

                orchestrator.loadPlanningData(
                    state.getActiveProjectSlug(),
                    state.getActiveInitiativeId()
                );
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                showInitiativeFormError(
                    response.message
                    || "The Initiative request failed.",
                    response.field_errors
                );
            })
            .always(function() {
                state.setRequest("initiative", null);
                setInitiativeSaveState(false);
            });

        state.setRequest("initiative", request);
    }

    function deleteInitiative(initiative) {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;
        const initiativeId = Number(
            initiative && initiative.id
        );

        if (!endpoint) {
            workspace.showError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!initiativeId) {
            workspace.showError(
                "The selected Initiative could not be identified."
            );
            return;
        }

        if (
            !window.confirm(
                "Delete this Initiative and all of its Phases and Steps?"
            )
        ) {
            return;
        }

        if (state.getRequest("initiative")) {
            return;
        }

        setInitiativeDeleteState(true);

        const request = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": utilities.getCsrfToken(),
            },
            data: JSON.stringify({
                operation: "delete_initiative",
                initiative_id: initiativeId,
            }),
        })
            .done(function(response) {
                if (
                    !response
                    || response.status !== "success"
                ) {
                    workspace.showError(
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                state.clearActiveInitiative();

                closeInitiativeForm();

                orchestrator.loadPlanningData(
                    state.getActiveProjectSlug()
                );
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                workspace.showError(
                    response.message
                    || "The Initiative delete request failed."
                );
            })
            .always(function() {
                state.setRequest("initiative", null);
                setInitiativeDeleteState(false);
            });

        state.setRequest("initiative", request);
    }

    Planning.initiatives = {
        clearFormError: clearInitiativeFormError,
        openForm: openInitiativeForm,
        closeForm: closeInitiativeForm,
        save: saveInitiative,
        delete: deleteInitiative,
    };
})(window, jQuery);
// ======================================================================
// END: INITIATIVE_CREATION_CONTROLLER
// ======================================================================