// ======================================================================
// FILE: aurora/static/aurora/js/planning/renderers/project_renderer.js
// START: PROJECT_RENDERER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;

    function renderSelector(projects, activeProject) {
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

    Planning.renderers = Planning.renderers || {};

    Planning.renderers.project = {
        renderSelector: renderSelector,
    };
})(window, jQuery);
// ======================================================================
// END: PROJECT_RENDERER
// ======================================================================