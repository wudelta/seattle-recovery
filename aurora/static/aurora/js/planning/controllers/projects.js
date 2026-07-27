// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/projects.js
// START: PROJECT_CONTROLLER_SETUP
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
// ======================================================================
// END: PROJECT_CONTROLLER_SETUP
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/projects.js
// START: PROJECT_FORM_ERRORS
// ======================================================================
    function clearProjectFormError() {
        $("#planning-project-form-error")
            .addClass("d-none")
            .empty();
    }

    function showProjectFormError(message, fieldErrors) {
        const errors = [];

        if (fieldErrors) {
            Object.keys(fieldErrors).forEach(function(fieldName) {
                errors.push(fieldErrors[fieldName]);
            });
        }

        $("#planning-project-form-error")
            .removeClass("d-none")
            .text(
                errors.length
                    ? errors.join(" ")
                    : message || "The Project could not be saved."
            );
    }
// ======================================================================
// END: PROJECT_FORM_ERRORS
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/projects.js
// START: PROJECT_FORM_LIFECYCLE
// ======================================================================
    function renderProjectAssigneeOptions(selectedUserId) {
        const users = state.getUsers();
        const selectedValue = (
            selectedUserId === null
            || selectedUserId === undefined
        )
            ? ""
            : String(selectedUserId);

        const $assignedTo = $("#planning-project-assigned-to");

        $assignedTo.empty();

        $assignedTo.append(
            $("<option>", {
                value: "",
                text: "Unassigned",
            })
        );

        users.forEach(function(user) {
            $assignedTo.append(
                $("<option>", {
                    value: user.id,
                    text: user.display_name || `User ${user.id}`,
                })
            );
        });

        $assignedTo.val(selectedValue);
    }

    function resetProjectForm() {
        const form = document.getElementById(
            "planning-project-form"
        );

        if (form) {
            form.reset();
        }

        $("#planning-project-form")
            .removeAttr("data-project-slug");

        $("#planning-project-status").val("PLANNED");
        $("#planning-project-created-by").val("");

        renderProjectAssigneeOptions(null);

        $("#planning-project-active").prop("checked", true);

        $("#planning-delete-project-btn")
            .addClass("d-none")
            .prop("disabled", false)
            .text("Delete Project");

        clearProjectFormError();
    }

    function openProjectForm(project) {
        resetProjectForm();

        if (project && project.slug) {
            $("#planning-project-form")
                .attr("data-project-slug", project.slug);

            $("#planning-project-title")
                .val(project.title || "");

            $("#planning-project-description")
                .val(project.description || "");

            $("#planning-project-color")
                .val(project.color || "");

            $("#planning-project-icon")
                .val(project.icon || "");

            $("#planning-project-status")
                .val(project.status || "PLANNED");

            renderProjectAssigneeOptions(
                project.assigned_to_id
            );

            $("#planning-project-created-by")
                .val(project.created_by_name || "");

            $("#planning-project-active")
                .prop("checked", project.active !== false);

            $("#planning-project-form-heading")
                .text("Edit Project");

            $("#planning-project-form-guidance")
                .text(
                    "Update this Project without changing its internal slug."
                );

            $("#planning-delete-project-btn")
                .removeClass("d-none");
        } else {
            $("#planning-project-form-heading")
                .text("Create Project");

            $("#planning-project-form-guidance")
                .text(
                    "Create a product, application, or engineering domain."
                );
        }

        $("#planning-workspace")
            .addClass("d-none");

        $("#planning-initiative-form-panel")
            .addClass("d-none");

        $("#planning-project-form-panel")
            .removeClass("d-none flex-shrink-0")
            .addClass("flex-grow-1 overflow-auto")
            .css("min-height", 0)
            .scrollTop(0);

        $("#planning-project-title").trigger("focus");
    }

    function closeProjectForm() {
        resetProjectForm();

        $("#planning-project-form-panel")
            .addClass("d-none")
            .removeClass("flex-grow-1 overflow-auto")
            .addClass("flex-shrink-0")
            .css("min-height", "");

        $("#planning-workspace")
            .removeClass("d-none");
    }
// ======================================================================
// END: PROJECT_FORM_LIFECYCLE
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/projects.js
// START: PROJECT_REQUEST_STATES
// ======================================================================
    function setProjectSaveState(isSaving) {
        $("#planning-save-project-btn")
            .prop("disabled", isSaving)
            .text(isSaving ? "Saving..." : "Save Project");

        $("#planning-cancel-project-btn")
            .prop("disabled", isSaving);

        $("#planning-project-form")
            .find("input, textarea, select, button[type='reset']")
            .prop("disabled", isSaving);
    }

    function setProjectDeleteState(isDeleting) {
        $("#planning-delete-project-btn")
            .prop("disabled", isDeleting)
            .text(
                isDeleting
                    ? "Deleting..."
                    : "Delete Project"
            );
    }
// ======================================================================
// END: PROJECT_REQUEST_STATES
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/projects.js
// START: PROJECT_DELETE_GUARD
// ======================================================================
    function projectDeleteBlockedMessage(project) {
        const initiativeCount = Number(
            project.initiative_count || 0
        );

        const phaseCount = Number(
            project.phase_count || 0
        );

        const stepCount = Number(
            project.step_count || 0
        );

        return (
            "This Project cannot be deleted because it contains "
            + `${initiativeCount} Initiative`
            + `${initiativeCount === 1 ? "" : "s"}, `
            + `${phaseCount} Phase`
            + `${phaseCount === 1 ? "" : "s"}, and `
            + `${stepCount} Step`
            + `${stepCount === 1 ? "" : "s"}. `
            + "Delete its children before deleting the Project."
        );
    }
// ======================================================================
// END: PROJECT_DELETE_GUARD
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/projects.js
// START: PROJECT_SAVE
// ======================================================================
    function saveProject() {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;

        const projectSlug = (
            $("#planning-project-form")
                .attr("data-project-slug")
            || null
        );

        const title = $("#planning-project-title")
            .val()
            .trim();

        const assignedToValue = (
            $("#planning-project-assigned-to").val() || ""
        ).trim();

        clearProjectFormError();

        if (!endpoint) {
            showProjectFormError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!title) {
            showProjectFormError(
                "Project title is required.",
                {
                    title: "Enter a Project title.",
                }
            );

            $("#planning-project-title").trigger("focus");
            return;
        }

        if (state.getRequest("project")) {
            return;
        }

        setProjectSaveState(true);

        const request = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": utilities.getCsrfToken(),
            },
            data: JSON.stringify({
                operation: "save_project",
                project_slug: projectSlug,
                title: title,
                description: $("#planning-project-description")
                    .val()
                    .trim(),
                color: $("#planning-project-color")
                    .val()
                    .trim(),
                icon: $("#planning-project-icon")
                    .val()
                    .trim(),
                status: $("#planning-project-status").val(),
                assigned_to_id: assignedToValue || null,
                active: $("#planning-project-active")
                    .prop("checked"),
            }),
        })
            .done(function(response) {
                if (
                    !response
                    || response.status !== "success"
                    || !response.project
                    || !response.project.slug
                ) {
                    showProjectFormError(
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                state.setActiveProjectSlug(
                    response.project.slug
                );

                state.clearActiveInitiative();

                closeProjectForm();

                orchestrator.loadPlanningData(
                    response.project.slug
                );
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                showProjectFormError(
                    response.message
                    || "The Project request failed.",
                    response.field_errors
                );
            })
            .always(function() {
                state.setRequest("project", null);
                setProjectSaveState(false);
            });

        state.setRequest("project", request);
    }
// ======================================================================
// END: PROJECT_SAVE
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/projects.js
// START: PROJECT_DELETE
// ======================================================================
    function deleteProject(project) {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;
        const activeProject = state.getActiveProject();

        const projectSlug = String(
            project && project.slug
            || state.getActiveProjectSlug()
            || ""
        ).trim();

        clearProjectFormError();

        if (!endpoint) {
            showProjectFormError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!projectSlug) {
            showProjectFormError(
                "The selected Project could not be identified."
            );
            return;
        }

        if (
            activeProject
            && activeProject.slug === projectSlug
            && activeProject.can_delete === false
        ) {
            window.alert(
                projectDeleteBlockedMessage(activeProject)
            );
            return;
        }

        if (
            !window.confirm(
                "Delete this empty Project permanently?"
            )
        ) {
            return;
        }

        if (state.getRequest("project")) {
            return;
        }

        setProjectDeleteState(true);

        const request = $.ajax({
            url: endpoint,
            method: "POST",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": utilities.getCsrfToken(),
            },
            data: JSON.stringify({
                operation: "delete_project",
                project_slug: projectSlug,
            }),
        })
            .done(function(response) {
                if (
                    !response
                    || response.status !== "success"
                ) {
                    showProjectFormError(
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                state.clearActiveProject();
                state.clearActiveInitiative();

                closeProjectForm();

                orchestrator.loadPlanningData();
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                showProjectFormError(
                    response.message
                    || "The Project delete request failed.",
                    response.field_errors
                );
            })
            .always(function() {
                state.setRequest("project", null);
                setProjectDeleteState(false);
            });

        state.setRequest("project", request);
    }
// ======================================================================
// END: PROJECT_DELETE
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/planning/controllers/projects.js
// START: PROJECT_CONTROLLER_PUBLIC_API
// ======================================================================
    Planning.projects = {
        clearFormError: clearProjectFormError,
        openForm: openProjectForm,
        closeForm: closeProjectForm,
        save: saveProject,
        delete: deleteProject,
    };
})(window, jQuery);
// ======================================================================
// END: PROJECT_CONTROLLER_PUBLIC_API
// ======================================================================