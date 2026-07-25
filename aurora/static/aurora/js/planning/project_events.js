// ======================================================================
// FILE: aurora/static/aurora/js/planning/project_events.js
// START: PROJECT_EVENT_BINDINGS
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const data = Planning.data;
    const projects = Planning.projects;
    const initiatives = Planning.initiatives;

    function bindProjectEvents() {
        $("#planning-project-select")
            .off("change.planningProject")
            .on("change.planningProject", function() {
                state.setActiveProjectSlug(
                    $(this).val() || null
                );

                state.clearActiveInitiative();

                projects.closeForm();
                initiatives.closeForm();

                data.loadPlanningData(
                    state.getActiveProjectSlug()
                );
            });

        $("#planning-create-project-btn")
            .off("click.planningProject")
            .on("click.planningProject", function() {
                projects.openForm(null);
            });

        $("#planning-cancel-project-btn")
            .off("click.planningProject")
            .on("click.planningProject", function() {
                projects.closeForm();
            });

        $("#planning-project-form")
            .off("submit.planningProject")
            .on("submit.planningProject", function(event) {
                event.preventDefault();
                projects.save();
            })
            .off("reset.planningProject")
            .on("reset.planningProject", function() {
                projects.clearFormError();
            });

        $("#planning-delete-project-btn")
            .off("click.planningProject")
            .on("click.planningProject", function() {
                projects.delete({
                    slug: (
                        $("#planning-project-form")
                            .attr("data-project-slug")
                        || state.getActiveProjectSlug()
                    ),
                });
            });
    }

    Planning.projectEvents = {
        bind: bindProjectEvents,
    };
})(window, jQuery);
// ======================================================================
// END: PROJECT_EVENT_BINDINGS
// ======================================================================