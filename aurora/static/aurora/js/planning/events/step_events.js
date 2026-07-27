// ======================================================================
// FILE: aurora/static/aurora/js/planning/events/step_events.js
// START: STEP_EVENT_BINDINGS
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const steps = Planning.steps;

    function bindStepEvents() {
        $("#planning-initiative-list")
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

    Planning.stepEvents = {
        bind: bindStepEvents,
    };
})(window, jQuery);
// ======================================================================
// END: STEP_EVENT_BINDINGS
// ======================================================================