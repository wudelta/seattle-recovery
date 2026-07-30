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

    function updateStepFileEmptyState(
        $phase,
        fileKind
    ) {
        const $list = $phase.find(
            `.planning-step-form-file-list[data-file-kind="${fileKind}"]`
        );

        const hasRows = (
            $list.find(".planning-step-form-file-row").length > 0
        );

        $phase
            .find(
                `.planning-step-form-file-empty[data-file-kind="${fileKind}"]`
            )
            .toggleClass(
                "d-none",
                hasRows
            );
    }

    function createStepFileRow(
        fileKind,
        stepFile
    ) {
        const file = stepFile || {};

        return $("<div>", {
            class: (
                "planning-step-form-file-row "
                + "border border-secondary rounded p-2"
            ),
            "data-file-kind": fileKind,
        }).append(
            $("<div>", {
                class: "d-flex align-items-start gap-2",
            }).append(
                $("<div>", {
                    class: "flex-grow-1",
                }).append(
                    $("<input>", {
                        type: "text",
                        class: (
                            "planning-step-form-file-path "
                            + "form-control form-control-sm "
                            + "bg-black text-light border-secondary "
                            + "font-monospace"
                        ),
                        value: file.file_path || "",
                        placeholder: "aurora/path/to/file.py",
                        spellcheck: "false",
                    }),
                    $("<textarea>", {
                        class: (
                            "planning-step-form-file-reason "
                            + "form-control form-control-sm "
                            + "bg-black text-light border-secondary "
                            + "mt-2"
                        ),
                        rows: 2,
                        placeholder: "Why will this file change?",
                    }).val(
                        file.reason || ""
                    )
                ),
                $("<button>", {
                    type: "button",
                    class: (
                        "planning-remove-step-file-btn "
                        + "btn btn-outline-danger btn-sm"
                    ),
                    title: "Remove file",
                    "aria-label": "Remove file",
                }).text("Remove")
            )
        );
    }

    function addStepFileRow(
        $phase,
        fileKind,
        stepFile
    ) {
        const $list = $phase.find(
            `.planning-step-form-file-list[data-file-kind="${fileKind}"]`
        );

        if (!$list.length) {
            return;
        }

        const $row = createStepFileRow(
            fileKind,
            stepFile
        );

        $list.append($row);

        updateStepFileEmptyState(
            $phase,
            fileKind
        );

        $row
            .find(".planning-step-form-file-path")
            .trigger("focus");
    }

    function clearStepFileRows($phase) {
        $phase
            .find(".planning-step-form-file-list")
            .empty();

        updateStepFileEmptyState(
            $phase,
            "planned"
        );

        updateStepFileEmptyState(
            $phase,
            "actual"
        );
    }

    function removeStepFileRow($button) {
        const $row = $button.closest(
            ".planning-step-form-file-row"
        );

        const fileKind = $row.data("file-kind");

        const $phase = $row.closest(
            ".planning-phase"
        );

        $row.remove();

        updateStepFileEmptyState(
            $phase,
            fileKind
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
                ".planning-add-step-file-btn",
                function() {
                    const $button = $(this);

                    addStepFileRow(
                        $button.closest(".planning-phase"),
                        $button.data("file-kind"),
                        null
                    );
                }
            )
            .on(
                "click.planningStep",
                ".planning-remove-step-file-btn",
                function() {
                    removeStepFileRow(
                        $(this)
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
        addFileRow: addStepFileRow,
        clearFileRows: clearStepFileRows,
    };
})(window, jQuery);
// ======================================================================
// END: STEP_EVENT_BINDINGS
// ======================================================================