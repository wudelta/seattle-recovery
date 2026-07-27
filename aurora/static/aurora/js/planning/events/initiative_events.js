// ======================================================================
// FILE: aurora/static/aurora/js/planning/events/initiative_events.js
// START: INITIATIVE_EVENT_BINDINGS
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const orchestrator = Planning.orchestrator;
    const initiatives = Planning.initiatives;

    function bindInitiativeEvents() {
        $("#planning-navigator-initiative-list")
            .off("click.planningInitiative")
            .on(
                "click.planningInitiative",
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

                    orchestrator.loadPlanningData(
                        state.getActiveProjectSlug(),
                        state.getActiveInitiativeId()
                    );
                }
            );

        $(
            "#planning-create-initiative-btn, "
            + "#planning-empty-create-initiative-btn"
        )
            .off("click.planningInitiative")
            .on("click.planningInitiative", function() {
                initiatives.openForm(null);
            });

        $("#planning-cancel-initiative-btn")
            .off("click.planningInitiative")
            .on("click.planningInitiative", function() {
                initiatives.closeForm();
            });

        $("#planning-initiative-form")
            .off("submit.planningInitiative")
            .on("submit.planningInitiative", function(event) {
                event.preventDefault();
                initiatives.save();
            })
            .off("reset.planningInitiative")
            .on("reset.planningInitiative", function() {
                initiatives.clearFormError();

                window.setTimeout(function() {
                    $("#planning-initiative-status")
                        .val("PLANNED");
                }, 0);
            });

        $("#planning-initiative-list")
            .off("click.planningInitiative")
            .on(
                "click.planningInitiative",
                ".planning-edit-initiative-btn",
                function() {
                    initiatives.openForm(
                        state.getActiveInitiative()
                    );
                }
            )
            .on(
                "click.planningInitiative",
                ".planning-delete-initiative-btn",
                function() {
                    initiatives.delete(
                        state.getActiveInitiative()
                    );
                }
            );
    }

    Planning.initiativeEvents = {
        bind: bindInitiativeEvents,
    };
})(window, jQuery);
// ======================================================================
// END: INITIATIVE_EVENT_BINDINGS
// ======================================================================