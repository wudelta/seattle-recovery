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

    function toggleStep($button) {
        const $step = $button.closest(
            ".planning-step"
        );

        const $document = $step.find(
            ".planning-step-document"
        ).first();

        const isExpanded = (
            $button.attr("aria-expanded") === "true"
        );

        $button
            .attr(
                "aria-expanded",
                isExpanded ? "false" : "true"
            )
            .attr(
                "aria-label",
                isExpanded
                    ? "Expand Step"
                    : "Collapse Step"
            )
            .attr(
                "title",
                isExpanded
                    ? "Expand Step"
                    : "Collapse Step"
            );

        $button
            .find(".planning-step-toggle-icon")
            .text(
                isExpanded ? "▸" : "▾"
            );

        $step.toggleClass(
            "planning-step-collapsed",
            isExpanded
        );

        $document.toggleClass(
            "d-none",
            isExpanded
        );
    }

    function bindStepEvents() {
        $("#planning-initiative-list")
            .off(".planningStep")
            .on(
                "click.planningStep",
                ".planning-toggle-step-btn",
                function() {
                    toggleStep(
                        $(this)
                    );
                }
            )
            .on(
                "click.planningStep",
                ".planning-new-step-btn",
                function() {
                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    steps.openForm(
                        $phase,
                        null
                    );
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
            .on(
                "reset.planningStep",
                ".planning-step-form",
                function() {
                    const $phase = $(this).closest(
                        ".planning-phase"
                    );

                    steps.clearFormError(
                        $phase
                    );
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