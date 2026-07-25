// ======================================================================
// FILE: aurora/static/aurora/js/planning/workspace.js
// START: PLANNING_WORKSPACE_STATE
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;

    function renderProjectSelector(projects, activeProject) {
        const $projectSelect = $("#planning-project-select");
        const $editProjectButton = $("#planning-edit-project-btn");

        $projectSelect.empty();

        if (!Array.isArray(projects) || !projects.length) {
            state.setActiveProjectSlug(null);
            state.clearActiveInitiative();

            $projectSelect
                .append(
                    $("<option>", {
                        value: "",
                        text: "No active projects",
                    })
                )
                .prop("disabled", true);

            $editProjectButton.prop("disabled", true);

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

        const projectSlug = (
            activeProject
            && activeProject.slug
        )
            ? activeProject.slug
            : projects[0].slug;

        state.setActiveProjectSlug(projectSlug);

        $projectSelect
            .val(projectSlug)
            .prop("disabled", false);

        $editProjectButton.prop("disabled", false);

        $(
            "#planning-create-initiative-btn, "
            + "#planning-empty-create-initiative-btn"
        ).prop("disabled", false);
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
            const selectedId = (
                selectedInitiativeId !== null
                && selectedInitiativeId !== undefined
            )
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
        renderNavigatorInitiatives([], null);
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

        $("#planning-summary-badge")
            .removeClass("text-danger text-success")
            .addClass("text-info")
            .text("0 initiatives · 0 phases · 0 steps");
    }

    Planning.workspace = {
        renderProjectSelector: renderProjectSelector,
        renderNavigatorInitiatives: renderNavigatorInitiatives,
        resetNavigator: resetNavigator,
        setLoadingState: setLoadingState,
        showError: showError,
        showEmptyState: showEmptyState,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_WORKSPACE_STATE
// ======================================================================