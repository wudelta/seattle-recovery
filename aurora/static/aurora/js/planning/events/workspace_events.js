// ======================================================================
// FILE: aurora/static/aurora/js/planning/events/workspace_events.js
// START: PLANNING_EVENT_BINDINGS_AND_PUBLIC_API
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const orchestrator = Planning.orchestrator;

    const projectEvents = Planning.projectEvents;
    const initiativeEvents = Planning.initiativeEvents;
    const phaseEvents = Planning.phaseEvents;
    const stepEvents = Planning.stepEvents;

    function bindPlanningEvents() {
        projectEvents.bind();
        initiativeEvents.bind();
        phaseEvents.bind();
        stepEvents.bind();

        $("#planning-refresh-btn")
            .off("click.planning")
            .on("click.planning", function() {
                orchestrator.loadPlanningData(
                    state.getActiveProjectSlug(),
                    state.getActiveInitiativeId()
                );
            });
    }

    function initialize(systemEndpoints) {
        state.setEndpoints(systemEndpoints || {});

        if (!state.isInitialized()) {
            Planning.renderers.navigator.reset();
            bindPlanningEvents();
            state.markInitialized();
        }

        orchestrator.loadPlanningData(
            state.getActiveProjectSlug(),
            state.getActiveInitiativeId()
        );
    }

    function refresh() {
        if (!state.isInitialized()) {
            return;
        }

        orchestrator.loadPlanningData(
            state.getActiveProjectSlug(),
            state.getActiveInitiativeId()
        );
    }

    Planning.events = {
        bind: bindPlanningEvents,
        initialize: initialize,
        refresh: refresh,
    };

    window.initPlanningConsole = initialize;
    window.refreshPlanningConsole = refresh;

})(window, jQuery);
// ======================================================================
// END: PLANNING_EVENT_BINDINGS_AND_PUBLIC_API
// ======================================================================