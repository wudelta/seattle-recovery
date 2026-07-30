// ======================================================================
// FILE: aurora/static/aurora/js/planning/events/phase_events.js
// START: PHASE_EVENT_BINDINGS
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const phases = Planning.phases;

    function findInitiativeContent($source) {
        const initiativeId = Number(
            $source
                .closest(".planning-initiative")
                .attr("data-initiative-id")
        );

        if (!initiativeId) {
            return $();
        }

        return $("#planning-initiative-list")
            .find(".planning-initiative-content")
            .filter(function() {
                return Number(
                    $(this).attr("data-initiative-id")
                ) === initiativeId;
            })
            .first();
    }

    function togglePhase($button) {
        const $phase = $button.closest(
            ".planning-phase"
        );

        const $body = $phase.find(
            ".planning-phase-body"
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
                    ? "Expand Phase"
                    : "Collapse Phase"
            )
            .attr(
                "title",
                isExpanded
                    ? "Expand Phase"
                    : "Collapse Phase"
            );

        $button
            .find(".planning-phase-toggle-icon")
            .text(
                isExpanded ? "▸" : "▾"
            );

        $phase.toggleClass(
            "planning-phase-collapsed",
            isExpanded
        );

        $body.toggleClass(
            "d-none",
            isExpanded
        );
    }

    function bindPhaseEvents() {
        $("#planning-workbench")
            .off(".planningPhase")
            .on(
                "click.planningPhase",
                ".planning-toggle-phase-btn",
                function() {
                    togglePhase(
                        $(this)
                    );
                }
            )
            .on(
                "click.planningPhase",
                ".planning-new-phase-btn",
                function() {
                    const $initiative = findInitiativeContent(
                        $(this)
                    );

                    if (!$initiative.length) {
                        return;
                    }

                    phases.openForm(
                        $initiative,
                        null
                    );
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

                    phases.closeForm(
                        $initiative
                    );
                }
            )
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
            .on(
                "reset.planningPhase",
                ".planning-phase-form",
                function() {
                    const $initiative = $(this).closest(
                        ".planning-initiative"
                    );

                    phases.clearFormError(
                        $initiative
                    );
                }
            );
    }

    Planning.phaseEvents = {
        bind: bindPhaseEvents,
    };
})(window, jQuery);
// ======================================================================
// END: PHASE_EVENT_BINDINGS
// ======================================================================