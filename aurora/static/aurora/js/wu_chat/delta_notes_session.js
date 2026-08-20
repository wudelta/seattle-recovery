// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat/delta_notes_session.js
// START: DELTA_NOTES_SESSION_WORKFLOW
// ======================================================================
(function(window, $) {
    "use strict";

    function initWuDeltaNotesSession(options) {
        const processBtn = $('#wu-process-delta-notes-btn');
        const messages = $('#wu-session-management-messages');
        const endpoint = options.endpoint;
        const onWorkflowChanged = options.onWorkflowChanged || function() {};

        let activeNote = null;
        let pendingPlanningProposal = null;
        let sessionActive = false;
        let unprocessedCount = 0;
        let planningProjectSlug = null;

        const sendToPlanningBtn = $('<button>', {
            id: 'wu-send-delta-note-to-planning-btn',
            type: 'button',
            class: 'btn btn-outline-primary btn-sm font-monospace',
            text: 'Send to Planning',
        });

        const rejectPlanningBtn = $('<button>', {
            id: 'wu-reject-delta-note-planning-btn',
            type: 'button',
            class: 'btn btn-outline-warning btn-sm font-monospace d-none',
            text: 'Reject Proposal',
        });

        const approvePlanningBtn = $('<button>', {
            id: 'wu-approve-delta-note-planning-btn',
            type: 'button',
            class: 'btn btn-outline-success btn-sm font-monospace d-none',
            text: 'Approve Planning Proposal',
        });

        processBtn.after(sendToPlanningBtn);
        sendToPlanningBtn.after(rejectPlanningBtn);
        rejectPlanningBtn.after(approvePlanningBtn);

        function appendMessage(message, className = 'text-muted') {
            if (!messages.length) {
                return;
            }

            messages.append(
                $(`<div class="${className}"></div>`).text(message)
            );
            messages.scrollTop(messages[0].scrollHeight);
        }

        function extractErrorMessage(xhr, fallback) {
            let errorText = fallback;

            try {
                const response = JSON.parse(xhr.responseText);
                errorText = response.message || errorText;
            } catch (error) {
                // Preserve fallback message.
            }

            return errorText;
        }

        function refreshButtons() {
            const proposalPending = pendingPlanningProposal !== null;

            processBtn.text(
                activeNote
                    ? 'Resolve / No Action'
                    : 'Process Delta Notes'
            );

            processBtn.prop(
                'disabled',
                (
                    !sessionActive
                    || proposalPending
                    || (!activeNote && unprocessedCount === 0)
                )
            );

            sendToPlanningBtn.prop(
                'disabled',
                (
                    !sessionActive
                    || !activeNote
                    || !planningProjectSlug
                    || proposalPending
                )
            );

            rejectPlanningBtn
                .toggleClass('d-none', !proposalPending)
                .prop(
                    'disabled',
                    !sessionActive || !proposalPending
                );

            approvePlanningBtn
                .toggleClass('d-none', !proposalPending)
                .prop(
                    'disabled',
                    !sessionActive || !proposalPending
                );
        }

        function renderActiveNote() {
            if (!activeNote) {
                return;
            }

            appendMessage(
                `[DELTA NOTE ${activeNote.id}] ${activeNote.text}`,
                'text-info'
            );

            if (pendingPlanningProposal) {
                renderPlanningProposalSummary(
                    pendingPlanningProposal
                );
            }
        }

        function renderPlanningProposalSummary(proposal) {
            if (!proposal) {
                return;
            }

            const document = proposal.document || {};
            const addProjects = document.add_projects || [];
            const addInitiatives = document.add_initiatives || [];
            const addPhases = document.add_phases || [];
            const addSteps = document.add_steps || [];

            appendMessage(
                `[PLANNING PROPOSAL] Project: ${proposal.project_slug}`,
                'text-warning'
            );

            appendMessage(
                '[PLANNING PROPOSAL] Additions: '
                + `Projects ${addProjects.length}, `
                + `Initiatives ${addInitiatives.length}, `
                + `Phases ${addPhases.length}, `
                + `Steps ${addSteps.length}`,
                'text-warning'
            );

            addProjects.forEach(function(project) {
                appendMessage(
                    `[PLANNING PROPOSAL] New Project: ${project.title}`,
                    'text-warning'
                );
            });

            addInitiatives.forEach(function(initiative) {
                appendMessage(
                    `[PLANNING PROPOSAL] New Initiative: ${initiative.title}`,
                    'text-warning'
                );
            });

            addPhases.forEach(function(addition) {
                appendMessage(
                    '[PLANNING PROPOSAL] '
                    + `Existing Initiative: ${addition.initiative_title}`,
                    'text-warning'
                );

                (addition.phases || []).forEach(function(phase) {
                    appendMessage(
                        `[PLANNING PROPOSAL] New Phase: ${phase.title}`,
                        'text-warning'
                    );
                });
            });

            addSteps.forEach(function(addition) {
                appendMessage(
                    '[PLANNING PROPOSAL] '
                    + `Existing Path: ${addition.initiative_title} `
                    + `→ ${addition.phase_title}`,
                    'text-warning'
                );

                (addition.steps || []).forEach(function(step) {
                    appendMessage(
                        `[PLANNING PROPOSAL] New Step: ${step.title}`,
                        'text-warning'
                    );
                });
            });

            appendMessage(
                '[PLANNING PROPOSAL] Validated dry-run only. '
                + 'Approve to apply this exact proposal.',
                'text-success'
            );
        }

        function reset() {
            activeNote = null;
            pendingPlanningProposal = null;
            refreshButtons();
        }

        function updateStatus(data) {
            const workflow = data.workflow || {};
            const planning = workflow.planning || {};
            const executable = planning.executable || {};
            const navigation = planning.navigation || {};
            const deltaNotes = workflow.delta_notes || {};

            if (typeof data.active === 'boolean') {
                sessionActive = data.active;
            }

            planningProjectSlug = (
                executable.project_slug
                || navigation.project_slug
                || null
            );

            unprocessedCount = (
                deltaNotes.unprocessed_count
                ?? unprocessedCount
            );

            refreshButtons();
            renderActiveNote();
        }

        function loadNextNote() {
            processBtn.prop('disabled', true);
            sendToPlanningBtn.prop('disabled', true);
            rejectPlanningBtn.prop('disabled', true);
            approvePlanningBtn.prop('disabled', true);

            $.post(
                endpoint,
                {action: 'next_delta_note'},
                function(data) {
                    if (data.status !== 'success') {
                        return;
                    }

                    activeNote = data.note || null;
                    pendingPlanningProposal = null;
                    updateStatus(data);

                    if (!activeNote) {
                        appendMessage(
                            '[DELTA NOTES] No unprocessed notes.'
                        );
                    }
                }
            ).fail(function(xhr) {
                appendMessage(
                    `[DELTA NOTES ERROR] ${
                        extractErrorMessage(
                            xhr,
                            'Unable to load the next Delta Note.'
                        )
                    }`,
                    'text-danger'
                );
                refreshButtons();
            });
        }

        function resolveActiveNote() {
            if (!activeNote || pendingPlanningProposal) {
                return;
            }

            const noteId = activeNote.id;

            processBtn.prop('disabled', true);
            sendToPlanningBtn.prop('disabled', true);

            $.post(
                endpoint,
                {
                    action: 'resolve_delta_note',
                    note_id: noteId
                },
                function(data) {
                    if (data.status !== 'success') {
                        return;
                    }

                    activeNote = null;
                    pendingPlanningProposal = null;
                    updateStatus(data);

                    $(document).trigger(
                        'aurora:delta_notes_changed'
                    );

                    appendMessage(
                        `[DELTA NOTE ${noteId}] Resolved / no action.`,
                        'text-success'
                    );

                    if (unprocessedCount > 0) {
                        loadNextNote();
                        return;
                    }

                    onWorkflowChanged();
                }
            ).fail(function(xhr) {
                appendMessage(
                    `[DELTA NOTES ERROR] ${
                        extractErrorMessage(
                            xhr,
                            'Unable to resolve the Delta Note.'
                        )
                    }`,
                    'text-danger'
                );
                refreshButtons();
            });
        }

        function proposeActiveNotePlanning() {
            if (
                !activeNote
                || !planningProjectSlug
                || pendingPlanningProposal
            ) {
                return;
            }

            processBtn.prop('disabled', true);

            sendToPlanningBtn
                .prop('disabled', true)
                .text('Generating Planning Proposal...');

            $.post(
                endpoint,
                {
                    action: 'propose_delta_note_planning',
                    note_id: activeNote.id,
                    project_slug: planningProjectSlug
                },
                function(data) {
                    if (data.status !== 'success') {
                        return;
                    }

                    pendingPlanningProposal =
                        data.proposal || null;

                    if (!pendingPlanningProposal) {
                        appendMessage(
                            '[PLANNING ERROR] '
                            + 'No Planning proposal was returned.',
                            'text-danger'
                        );
                        return;
                    }

                    renderPlanningProposalSummary(
                        pendingPlanningProposal
                    );
                }
            ).fail(function(xhr) {
                appendMessage(
                    `[PLANNING ERROR] ${
                        extractErrorMessage(
                            xhr,
                            'Unable to generate a Planning proposal.'
                        )
                    }`,
                    'text-danger'
                );
            }).always(function() {
                sendToPlanningBtn.text('Send to Planning');
                refreshButtons();
            });
        }

        function rejectPlanningProposal() {
            if (!pendingPlanningProposal) {
                return;
            }

            pendingPlanningProposal = null;

            appendMessage(
                '[PLANNING PROPOSAL] Rejected. '
                + 'Delta Note remains unprocessed.',
                'text-warning'
            );

            refreshButtons();
        }

        function approvePlanningProposal() {
            if (!activeNote || !pendingPlanningProposal) {
                return;
            }

            const noteId = activeNote.id;
            const planningDocument =
                pendingPlanningProposal.document;

            processBtn.prop('disabled', true);
            sendToPlanningBtn.prop('disabled', true);
            rejectPlanningBtn.prop('disabled', true);

            approvePlanningBtn
                .prop('disabled', true)
                .text('Applying Planning Proposal...');

            $.post(
                endpoint,
                {
                    action: 'apply_delta_note_planning',
                    note_id: noteId,
                    planning_document: JSON.stringify(
                        planningDocument
                    )
                },
                function(data) {
                    if (data.status !== 'success') {
                        return;
                    }

                    const result = data.result || {};
                    const application = result.application || {};

                    appendMessage(
                        `[PLANNING APPLIED] Project: ${result.project_slug}`,
                        'text-success'
                    );

                    appendMessage(
                        '[PLANNING APPLIED] '
                        + `Projects ${application.projects ?? 0}, `
                        + `Initiatives ${application.initiatives ?? 0}, `
                        + `Phases ${application.phases ?? 0}, `
                        + `Steps ${application.steps ?? 0}`,
                        'text-success'
                    );

                    appendMessage(
                        `[DELTA NOTE ${noteId}] `
                        + 'Resolved after successful Planning application.',
                        'text-success'
                    );

                    activeNote = null;
                    pendingPlanningProposal = null;
                    updateStatus(data);

                    $(document).trigger(
                        'aurora:delta_notes_changed'
                    );

                    if (unprocessedCount > 0) {
                        loadNextNote();
                        return;
                    }

                    onWorkflowChanged();
                }
            ).fail(function(xhr) {
                appendMessage(
                    `[PLANNING ERROR] ${
                        extractErrorMessage(
                            xhr,
                            'Unable to apply the Planning proposal.'
                        )
                    }`,
                    'text-danger'
                );
            }).always(function() {
                approvePlanningBtn.text(
                    'Approve Planning Proposal'
                );
                refreshButtons();
            });
        }

        processBtn.on('click', function(event) {
            event.preventDefault();

            if (activeNote) {
                resolveActiveNote();
                return;
            }

            loadNextNote();
        });

        sendToPlanningBtn.on('click', function(event) {
            event.preventDefault();
            proposeActiveNotePlanning();
        });

        rejectPlanningBtn.on('click', function(event) {
            event.preventDefault();
            rejectPlanningProposal();
        });

        approvePlanningBtn.on('click', function(event) {
            event.preventDefault();
            approvePlanningProposal();
        });

        refreshButtons();

        return {
            reset: reset,
            updateStatus: updateStatus,
        };
    }

    window.WuDeltaNotesSession = {
        init: initWuDeltaNotesSession,
    };
})(window, jQuery);
// ======================================================================
// END: DELTA_NOTES_SESSION_WORKFLOW
// ======================================================================
