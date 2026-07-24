// ======================================================================
// FILE: aurora/static/aurora/js/planning/events.js
// START: PLANNING_EVENT_BINDINGS_AND_PUBLIC_API
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const workspace = Planning.workspace;
    const data = Planning.data;
    const initiatives = Planning.initiatives;
    const phases = Planning.phases;
    const steps = Planning.steps;

    function bindPlanningEvents() {
        $("#planning-project-select")
            .off("change.planning")
            .on("change.planning", function() {
                state.setActiveProjectSlug(
                    $(this).val() || null
                );

                state.clearActiveInitiative();

                initiatives.closeForm();

                data.loadPlanningData(
                    state.getActiveProjectSlug()
                );
            });

        $("#planning-refresh-btn")
            .off("click.planning")
            .on("click.planning", function() {
                data.loadPlanningData(
                    state.getActiveProjectSlug(),
                    state.getActiveInitiativeId()
                );
            });

        $("#planning-navigator-initiative-list")
            .off("click.planningNavigator")
            .on(
                "click.planningNavigator",
                (
                    ".planning-navigator-item"
                    + "[data-item-type='initiative']"
                ),
                function() {
                    const selectedInitiativeId = Number(
                        $(this).attr("data-record-id")
                    );

                    if (
                        !selectedInitiativeId
                        || selectedInitiativeId
                            === state.getActiveInitiativeId()
                    ) {
                        return;
                    }

                    state.setActiveInitiativeId(
                        selectedInitiativeId
                    );

                    state.setActiveInitiative(null);

                    initiatives.closeForm();

                    data.loadPlanningData(
                        state.getActiveProjectSlug(),
                        state.getActiveInitiativeId()
                    );
                }
            );

        $(
            "#planning-create-initiative-btn, "
            + "#planning-empty-create-initiative-btn"
        )
            .off("click.planning")
            .on("click.planning", function() {
                initiatives.openForm(null);
            });

        $("#planning-cancel-initiative-btn")
            .off("click.planning")
            .on("click.planning", function() {
                initiatives.closeForm();
            });

        $("#planning-initiative-form")
            .off("submit.planning")
            .on("submit.planning", function(event) {
                event.preventDefault();
                initiatives.save();
            })
            .off("reset.planning")
            .on("reset.planning", function() {
                initiatives.clearFormError();

                window.setTimeout(function() {
                    $("#planning-initiative-status")
                        .val("PLANNED");
                }, 0);
            });

        $("#planning-initiative-list")
            .off("click.planningPhase")
            .on(
                "click.planningPhase",
                ".planning-edit-initiative-btn",
                function() {
                    initiatives.openForm(
                        state.getActiveInitiative()
                    );
                }
            )
            .on(
                "click.planningPhase",
                ".planning-delete-initiative-btn",
                function() {
                    initiatives.delete(
                        state.getActiveInitiative()
                    );
                }
            )
            .on(
                "click.planningPhase",
                ".planning-new-phase-btn",
                function() {
                    const $initiative = $(this).closest(
                        ".planning-initiative"
                    );

                    phases.openForm($initiative, null);
                }
            )
            .on(
                "click.planningPhase",
                ".planning-edit-phase-btn",
                function() {
                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    const $initiative = $phase.closest(
                        ".planning-initiative"
                    );

                    phases.openForm(
                        $initiative,
                        $phase.data("phase")
                    );
                }
            )
            .on(
                "click.planningPhase",
                ".planning-delete-phase-btn",
                function() {
                    phases.delete(
                        $(this).closest(
                            ".planning-phase"
                        )
                    );
                }
            )
            .on(
                "click.planningPhase",
                ".planning-cancel-phase-btn",
                function() {
                    const $initiative = $(this).closest(
                        ".planning-initiative"
                    );

                    phases.closeForm($initiative);
                }
            )
            .off("submit.planningPhase")
            .on(
                "submit.planningPhase",
                ".planning-phase-form",
                function(event) {
                    event.preventDefault();

                    phases.save(
                        $(this).closest(
                            ".planning-initiative"
                        )
                    );
                }
            )
            .off("reset.planningPhase")
            .on(
                "reset.planningPhase",
                ".planning-phase-form",
                function() {
                    const $initiative = $(this).closest(
                        ".planning-initiative"
                    );

                    phases.clearFormError($initiative);

                    window.setTimeout(function() {
                        $initiative
                            .find(
                                ".planning-phase-form-status"
                            )
                            .val("PLANNED");
                    }, 0);
                }
            )
            .off("click.planningStep")
            .on(
                "click.planningStep",
                ".planning-new-step-btn",
                function() {
                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    steps.openForm($phase, null);
                }
            )
            .on(
                "click.planningStep",
                ".planning-edit-step-btn",
                function() {
                    const $step = $(this).closest(
                        ".planning-step"
                    );

                    const $phase = $step.closest(
                        ".planning-phase"
                    );

                    steps.openForm(
                        $phase,
                        $step.data("step")
                    );
                }
            )
            .on(
                "click.planningStep",
                ".planning-delete-step-btn",
                function() {
                    steps.delete(
                        $(this).closest(
                            ".planning-step"
                        )
                    );
                }
            )
            .on(
                "click.planningStep",
                ".planning-cancel-step-btn",
                function() {
                    steps.closeForm(
                        $(this).closest(
                            ".planning-phase"
                        )
                    );
                }
            )
            .off("submit.planningStep")
            .on(
                "submit.planningStep",
                ".planning-step-form",
                function(event) {
                    event.preventDefault();

                    steps.save(
                        $(this).closest(
                            ".planning-phase"
                        )
                    );
                }
            )
            .off("reset.planningStep")
            .on(
                "reset.planningStep",
                ".planning-step-form",
                function() {
                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    steps.clearFormError($phase);

                    window.setTimeout(function() {
                        $phase
                            .find(
                                ".planning-step-form-status"
                            )
                            .val("PLANNED");

                        $phase
                            .find(
                                ".planning-step-form-estimate-confidence"
                            )
                            .val("");
                    }, 0);
                }
            );
    }

    function initialize(systemEndpoints) {
        state.setEndpoints(systemEndpoints || {});

        if (!state.isInitialized()) {
            workspace.resetNavigator();
            bindPlanningEvents();
            state.markInitialized();
        }

        data.loadPlanningData(
            state.getActiveProjectSlug(),
            state.getActiveInitiativeId()
        );
    }

    function refresh() {
        if (!state.isInitialized()) {
            return;
        }

        data.loadPlanningData(
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