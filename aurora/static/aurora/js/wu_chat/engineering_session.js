// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat/engineering_session.js
// START: ENGINEERING_SESSION_WORKFLOW
// ======================================================================
(function(window, $) {
    "use strict";

    function initWuEngineeringSession() {
    const workflowState = $(
        '#wu-session-workflow-state'
    );

    const sessionManagementMessages = $(
        '#wu-session-management-messages'
    );

    const startStepWorkBtn = $(
        '#wu-start-step-work-btn'
    );

    const endStepWorkBtn = $(
        '#wu-end-step-work-btn'
    );

    const completeStepBtn = $(
        '#wu-complete-step-btn'
    );

    const refreshRegistryBtn = $(
        '#wu-refresh-registry-btn'
    );

    const enrichRegistryBtn = $(
        '#wu-enrich-registry-btn'
    );

    const completionReview = $(
        '#wu-planning-completion-review'
    );

    const completionReviewMessage = $(
        '#wu-planning-completion-review-message'
    );

    const completionApproveBtn = $(
        '#wu-planning-completion-approve-btn'
    );

    const completionRejectBtn = $(
        '#wu-planning-completion-reject-btn'
    );

    const engineeringSessionEndpoint =
        '/aurora/api/engineering_session/';

    let pendingCompletionReview = null;
    let deltaNotesSession = null;

    function appendSessionManagementMessage(
        message,
        className = 'text-muted'
    ) {
        if (!sessionManagementMessages.length) {
            return;
        }

        sessionManagementMessages.prepend(
            $(`<div class="${className}"></div>`).text(
                message
            )
        );

        sessionManagementMessages.scrollTop(0);
    }

    function appendWorkflowStateMessage(
        message,
        className = 'text-muted'
    ) {
        if (!workflowState.length) {
            return;
        }

        workflowState.append(
            $(`<div class="${className}"></div>`).text(
                message
            )
        );
    }

    function setRegistryButtonsDisabled(disabled) {
        refreshRegistryBtn.prop(
            'disabled',
            disabled
        );

        enrichRegistryBtn.prop(
            'disabled',
            disabled
        );
    }

    function clearCompletionReview() {
        pendingCompletionReview = null;

        completionReview
            .addClass('d-none');

        completionReviewMessage.text('');

        completionApproveBtn.prop(
            'disabled',
            false
        );

        completionRejectBtn.prop(
            'disabled',
            false
        );
    }

    function showPhaseCompletionReview(
        phaseCompletion
    ) {
        if (
            !phaseCompletion
            || !phaseCompletion.eligible
            || !phaseCompletion.review_required
        ) {
            return;
        }

        pendingCompletionReview = {
            level: 'phase',
            id: phaseCompletion.phase_id,
            title: phaseCompletion.phase,
        };

        completionReviewMessage.text(
            `[PLANNING] Phase "${phaseCompletion.phase}" `
            + 'is eligible for completion.'
        );

        completionReview.removeClass('d-none');
    }

    function showInitiativeCompletionReview(
        initiativeCompletion
    ) {
        if (
            !initiativeCompletion
            || !initiativeCompletion.eligible
            || !initiativeCompletion.review_required
        ) {
            return;
        }

        pendingCompletionReview = {
            level: 'initiative',
            id: initiativeCompletion.initiative_id,
            title: initiativeCompletion.initiative,
        };

        completionReviewMessage.text(
            `[PLANNING] Initiative "${initiativeCompletion.initiative}" `
            + 'is eligible for completion.'
        );

        completionReview.removeClass('d-none');
    }

    function renderSessionWorkflowStatus(data) {
        if (!workflowState.length) {
            return;
        }

        const workflow = data.workflow || {};
        const planning = workflow.planning || {};
        const executable = planning.executable || {};
        const navigation = planning.navigation || {};
        const deltaNotes = workflow.delta_notes || {};
        const registry = workflow.component_registry || {};

        const activeTimeEntry =
            executable.active_time_entry || null;

        workflowState.empty();

        appendWorkflowStateMessage(
            data.active
                ? '[SESSION] Engineering session active'
                : '[SESSION] No active engineering session'
        );

        if (executable.available) {
            appendWorkflowStateMessage(
                `[PLANNING] Initiative: ${
                    executable.initiative
                }`
            );

            appendWorkflowStateMessage(
                `[PLANNING] Phase: ${
                    executable.phase
                }`
            );

            appendWorkflowStateMessage(
                `[PLANNING] Step: ${
                    executable.step
                }`,
                'text-info'
            );
        } else {
            appendWorkflowStateMessage(
                '[PLANNING] No executable work',
                'text-warning'
            );

            if (executable.reason) {
                appendWorkflowStateMessage(
                    `[PLANNING] ${executable.reason}`
                );
            }
        }

        if (
            navigation.initiative
            || navigation.phase
            || navigation.step
        ) {
            const navigationParts = [];

            if (navigation.initiative) {
                navigationParts.push(
                    navigation.initiative
                );
            }

            if (navigation.phase) {
                navigationParts.push(
                    navigation.phase
                );
            }

            if (navigation.step) {
                navigationParts.push(
                    navigation.step
                );
            }

            appendWorkflowStateMessage(
                `[NAVIGATION] ${
                    navigationParts.join(' → ')
                }`
            );
        }

        appendWorkflowStateMessage(
            activeTimeEntry
                ? `[STEP WORK] Active: ${
                    activeTimeEntry.step
                }`
                : '[STEP WORK] No active work interval'
        );

        appendWorkflowStateMessage(
            `[DELTA NOTES] Unprocessed: ${
                deltaNotes.unprocessed_count ?? 0
            }`
        );

        appendWorkflowStateMessage(
            `[REGISTRY] Pending enrichment: ${
                registry.pending_enrichment_count ?? 0
            }`
        );

        startStepWorkBtn.prop(
            'disabled',
            (
                !data.active
                || !executable.available
                || !executable.step_id
                || activeTimeEntry !== null
            )
        );

        endStepWorkBtn.prop(
            'disabled',
            activeTimeEntry === null
        );

        completeStepBtn.prop(
            'disabled',
            (
                !data.active
                || !executable.available
                || !executable.step_id
            )
        );

        if (deltaNotesSession) {
            deltaNotesSession.updateStatus(data);
        }
    }

    function loadSessionWorkflowStatus() {
        $.get(
            engineeringSessionEndpoint,
            function(data) {
                if (data.status !== 'success') {
                    return;
                }

                renderSessionWorkflowStatus(data);
            }
        ).fail(function(xhr) {
            console.error(
                '[Engineering Session] '
                + 'Unable to load workflow status.',
                xhr.responseText
            );
        });
    }

    function extractErrorMessage(
        xhr,
        fallback
    ) {
        let errorText = fallback;

        try {
            const response = JSON.parse(
                xhr.responseText
            );

            errorText =
                response.message
                || errorText;
        } catch (error) {
            // Preserve fallback message.
        }

        return errorText;
    }

    function runStepWorkAction(
        action
    ) {
        startStepWorkBtn.prop(
            'disabled',
            true
        );

        endStepWorkBtn.prop(
            'disabled',
            true
        );

        completeStepBtn.prop(
            'disabled',
            true
        );

        $.post(
            engineeringSessionEndpoint,
            {
                action: action
            },
            function(data) {
                if (data.status !== 'success') {
                    return;
                }

                if (action === 'start_step_work') {
                    appendSessionManagementMessage(
                        `[STEP WORK] Started: ${
                            data.time_entry.step
                        }`,
                        'text-success'
                    );
                } else {
                    appendSessionManagementMessage(
                        `[STEP WORK] Ended: ${
                            data.time_entry.step
                        }`,
                        'text-warning'
                    );
                }

                loadSessionWorkflowStatus();
            }
        ).fail(function(xhr) {
            appendSessionManagementMessage(
                `[STEP WORK ERROR] ${
                    extractErrorMessage(
                        xhr,
                        'Step work transition failed.'
                    )
                }`,
                'text-danger'
            );

            loadSessionWorkflowStatus();
        });
    }


    function refreshComponentRegistry() {
        setRegistryButtonsDisabled(true);

        appendSessionManagementMessage(
            '[REGISTRY] Deterministic refresh started.',
            'text-info'
        );

        $.post(
            engineeringSessionEndpoint,
            {
                action: 'refresh_component_registry'
            },
            function(data) {
                if (data.status !== 'success') {
                    return;
                }

                const maintenance =
                    data.maintenance || {};

                const counts =
                    maintenance.counts || {};

                appendSessionManagementMessage(
                    '[REGISTRY] Refresh complete: '
                    + `updated ${counts.UPDATED ?? 0}, `
                    + `registered ${counts.REGISTERED ?? 0}, `
                    + `archived ${counts.ARCHIVED ?? 0}, `
                    + `review ${counts.REVIEW ?? 0}, `
                    + `failures ${counts.FAILURES ?? 0}.`,
                    (
                        (counts.FAILURES ?? 0) > 0
                            ? 'text-danger'
                            : 'text-success'
                    )
                );

                loadSessionWorkflowStatus();
            }
        ).fail(function(xhr) {
            appendSessionManagementMessage(
                `[REGISTRY ERROR] ${
                    extractErrorMessage(
                        xhr,
                        'Component Registry refresh failed.'
                    )
                }`,
                'text-danger'
            );

            loadSessionWorkflowStatus();
        }).always(function() {
            setRegistryButtonsDisabled(false);
        });
    }

    function enrichComponentRegistry() {
        setRegistryButtonsDisabled(true);

        appendSessionManagementMessage(
            '[REGISTRY] AI enrichment started.',
            'text-info'
        );

        $.post(
            engineeringSessionEndpoint,
            {
                action: 'enrich_component_registry'
            },
            function(data) {
                if (data.status !== 'success') {
                    return;
                }

                const enrichment =
                    data.enrichment || {};

                appendSessionManagementMessage(
                    '[REGISTRY] Enrichment complete: '
                    + `completed ${enrichment.completed ?? 0}, `
                    + `skipped ${enrichment.skipped ?? 0}, `
                    + `remaining ${enrichment.remaining ?? 0}, `
                    + `failures ${enrichment.failures ?? 0}.`,
                    (
                        (enrichment.failures ?? 0) > 0
                        || enrichment.stopped
                            ? 'text-warning'
                            : 'text-success'
                    )
                );

                loadSessionWorkflowStatus();
            }
        ).fail(function(xhr) {
            appendSessionManagementMessage(
                `[REGISTRY ERROR] ${
                    extractErrorMessage(
                        xhr,
                        'Component Registry enrichment failed.'
                    )
                }`,
                'text-danger'
            );

            loadSessionWorkflowStatus();
        }).always(function() {
            setRegistryButtonsDisabled(false);
        });
    }

    function completeCurrentStep() {
        clearCompletionReview();

        completeStepBtn.prop(
            'disabled',
            true
        );

        $.post(
            engineeringSessionEndpoint,
            {
                action: 'complete_step'
            },
            function(data) {
                if (data.status !== 'success') {
                    return;
                }

                const lifecycle =
                    data.lifecycle || {};

                const step =
                    lifecycle.step || {};

                appendSessionManagementMessage(
                    `[PLANNING] Step completed: ${
                        step.title || 'unknown'
                    }`,
                    'text-success'
                );

                showPhaseCompletionReview(
                    lifecycle.phase_completion
                );

                loadSessionWorkflowStatus();
            }
        ).fail(function(xhr) {
            appendSessionManagementMessage(
                `[PLANNING ERROR] ${
                    extractErrorMessage(
                        xhr,
                        'Step completion failed.'
                    )
                }`,
                'text-danger'
            );

            loadSessionWorkflowStatus();
        });
    }

    function submitCompletionDecision(
        approved
    ) {
        if (!pendingCompletionReview) {
            return;
        }

        completionApproveBtn.prop(
            'disabled',
            true
        );

        completionRejectBtn.prop(
            'disabled',
            true
        );

        const review =
            pendingCompletionReview;

        let action;
        const payload = {};

        if (review.level === 'phase') {
            action = approved
                ? 'approve_phase_completion'
                : 'reject_phase_completion';

            payload.phase_id = review.id;
        } else {
            action = approved
                ? 'approve_initiative_completion'
                : 'reject_initiative_completion';

            payload.initiative_id = review.id;
        }

        payload.action = action;

        $.post(
            engineeringSessionEndpoint,
            payload,
            function(data) {
                if (data.status !== 'success') {
                    return;
                }

                appendSessionManagementMessage(
                    approved
                        ? `[PLANNING] Approved completion: ${
                            review.title
                        }`
                        : `[PLANNING] Rejected completion: ${
                            review.title
                        }`,
                    approved
                        ? 'text-success'
                        : 'text-warning'
                );

                clearCompletionReview();

                if (
                    approved
                    && review.level === 'phase'
                ) {
                    showInitiativeCompletionReview(
                        data.initiative_completion
                    );
                }

                loadSessionWorkflowStatus();
            }
        ).fail(function(xhr) {
            appendSessionManagementMessage(
                `[PLANNING ERROR] ${
                    extractErrorMessage(
                        xhr,
                        'Completion decision failed.'
                    )
                }`,
                'text-danger'
            );

            completionApproveBtn.prop(
                'disabled',
                false
            );

            completionRejectBtn.prop(
                'disabled',
                false
            );
        });
    }

    startStepWorkBtn.on(
        'click',
        function(event) {
            event.preventDefault();

            runStepWorkAction(
                'start_step_work'
            );
        }
    );

    endStepWorkBtn.on(
        'click',
        function(event) {
            event.preventDefault();

            runStepWorkAction(
                'end_step_work'
            );
        }
    );

    completeStepBtn.on(
        'click',
        function(event) {
            event.preventDefault();

            completeCurrentStep();
        }
    );

    refreshRegistryBtn.on(
        'click',
        function(event) {
            event.preventDefault();

            refreshComponentRegistry();
        }
    );

    enrichRegistryBtn.on(
        'click',
        function(event) {
            event.preventDefault();

            enrichComponentRegistry();
        }
    );

    completionApproveBtn.on(
        'click',
        function(event) {
            event.preventDefault();

            submitCompletionDecision(
                true
            );
        }
    );

    completionRejectBtn.on(
        'click',
        function(event) {
            event.preventDefault();

            submitCompletionDecision(
                false
            );
        }
    );

    $(document).on(
        'aurora:view_changed',
        function(event, viewMode) {
            if (viewMode === 'wu_chat') {
                loadSessionWorkflowStatus();
            }
        }
    );

    $(document).on(
        'aurora:session_started aurora:session_stopped',
        function() {
            clearCompletionReview();

            if (deltaNotesSession) {
                deltaNotesSession.reset();
            }

            loadSessionWorkflowStatus();
        }
    );

    if (
        window.WuDeltaNotesSession
        && typeof window.WuDeltaNotesSession.init === 'function'
    ) {
        deltaNotesSession = window.WuDeltaNotesSession.init({
            endpoint: engineeringSessionEndpoint,
            onWorkflowChanged: loadSessionWorkflowStatus,
        });
    }

    loadSessionWorkflowStatus();
    }

    window.initWuEngineeringSession =
        initWuEngineeringSession;
})(window, jQuery);
// ======================================================================
// END: ENGINEERING_SESSION_WORKFLOW
// ======================================================================
