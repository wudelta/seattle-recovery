// ======================================================================
// FILE: aurora/static/aurora/js/planning/projects.js
// START: PROJECT_PERSISTENCE_CONTROLLER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const utilities = Planning.utilities;
    const workspace = Planning.workspace;
    const data = Planning.data;

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

    function resetProjectForm() {
        const form = document.getElementById(
            "planning-project-form"
        );

        if (form) {
            form.reset();
        }

        $("#planning-project-form")
            .removeAttr("data-project-slug");

        $("#planning-project-active").prop("checked", true);

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

            $("#planning-project-active")
                .prop("checked", project.active !== false);

            $("#planning-project-form-heading")
                .text("Edit Project");

            $("#planning-project-form-guidance")
                .text(
                    "Update this Project without changing its internal slug."
                );
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

                data.loadPlanningData(
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

    function deleteProject(project) {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;

        const projectSlug = String(
            project && project.slug
            || state.getActiveProjectSlug()
            || ""
        ).trim();

        if (!endpoint) {
            workspace.showError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (!projectSlug) {
            workspace.showError(
                "The selected Project could not be identified."
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
                    workspace.showError(
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                state.setActiveProjectSlug(null);
                state.clearActiveInitiative();

                closeProjectForm();

                data.loadPlanningData();
            })
            .fail(function(xhr) {
                const response = xhr.responseJSON || {};

                workspace.showError(
                    response.message
                    || "The Project delete request failed."
                );
            })
            .always(function() {
                state.setRequest("project", null);
                setProjectDeleteState(false);
            });

        state.setRequest("project", request);
    }

    Planning.projects = {
        clearFormError: clearProjectFormError,
        openForm: openProjectForm,
        closeForm: closeProjectForm,
        save: saveProject,
        delete: deleteProject,
    };
})(window, jQuery);
// ======================================================================
// END: PROJECT_PERSISTENCE_CONTROLLER
// ======================================================================