// ======================================================================
// FILE: aurora/static/aurora/js/planning/renderers/workspace_renderer.js
// START: PLANNING_RENDERER_SETUP
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const workspace = Planning.workspace;
// ======================================================================
// END: PLANNING_RENDERER_SETUP
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/planning/renderers/workspace_renderer.js
// START: PLANNING_PAYLOAD_RENDERER
// ======================================================================
    function renderPlanningPayload(payload) {
        const projects = payload.projects || [];
        const users = payload.users || [];
        const activeProject = payload.active_project || null;
        const initiativeOptions = (
            payload.initiative_options || []
        );

        const renderedInitiative = (
            payload.active_initiative || null
        );

        const summary = payload.summary || {};

        const $initiativeList = $(
            "#planning-initiative-list"
        );

        state.setUsers(users);
        state.setActiveProject(activeProject);

        Planning.renderers.project.renderSelector(
            projects,
            activeProject
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

        if (
            !initiativeOptions.length
            || !renderedInitiative
        ) {
            state.clearActiveInitiative();

            Planning.renderers.navigator.renderInitiatives(
                [],
                null
            );

            workspace.showEmptyState();
            return;
        }

        state.setActiveInitiativeId(
            renderedInitiative.id
        );

        state.setActiveInitiative(
            renderedInitiative
        );

        Planning.renderers.navigator.renderInitiatives(
            initiativeOptions,
            renderedInitiative.id
        );

        $initiativeList.append(
            Planning.renderers.initiative.render(
                renderedInitiative
            )
        );

        const initiativeCount = initiativeOptions.length;
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
    }
// ======================================================================
// END: PLANNING_PAYLOAD_RENDERER
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/planning/renderers/workspace_renderer.js
// START: PLANNING_RENDERER_PUBLIC_API
// ======================================================================
    Planning.renderers = Planning.renderers || {};

    Planning.renderers.workspace = {
        renderPayload: renderPlanningPayload,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_RENDERER_PUBLIC_API
// ======================================================================