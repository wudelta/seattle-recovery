// ======================================================================
// FILE: aurora/static/aurora/js/console.js (PATCH 1 OF 2)
// START: SYSTEM_ASSET_REFERENCE_INTEGRITY_ALIGNMENT
// ======================================================================
$(document).ready(function() {
    console.log("[Aurora] Console automation loop loaded successfully.");

    // Core cockpit layout element definitions declared within the wrapper scope
    const $viewSelector = $('#console-view-selector');
    const $timerToggleBtn = $('#global-timer-toggle-btn');
    const $timerDisplay = $('#session-timer-display');
    const $gateOverlay = $('#aurora-cockpit-gate-overlay');

    let sessionActive = false;
    let timerInterval = null;
    let elapsedSeconds = 0;
    let telemetrySocket = null;

    function getCleanCSRFToken() {
        return $('input[name="csrfmiddlewaretoken"]').val();
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (
                !/^http:.*/.test(settings.url)
                && !/^https:.*/.test(settings.url)
            ) {
                const token = getCleanCSRFToken();

                if (token) {
                    xhr.setRequestHeader("X-CSRFToken", token);
                }
            }
        }
    });

    // Event handler for dynamic workspace switching
    $viewSelector.on('change', function() {
        const viewMode = $(this).val();

        $('.workspace-viewport .workspace-section')
            .addClass('d-none')
            .removeClass('active-pane');

        if (viewMode === 'delta_notes') {
            $('#delta-notes-workspace-container')
                .removeClass('d-none')
                .addClass('active-pane');

            $(document).trigger(
                'aurora:view_changed',
                ['delta_notes']
            );
        } else if (viewMode === 'wu_chat') {
            $('#wu_chat-workspace-container')
                .removeClass('d-none')
                .addClass('active-pane');

            $(document).trigger(
                'aurora:view_changed',
                ['wu_chat']
            );
        } else if (viewMode === 'planning') {
            $('#planning-workspace-container')
                .removeClass('d-none')
                .addClass('active-pane');

            $(document).trigger(
                'aurora:view_changed',
                ['planning']
            );
        } else if (viewMode === 'anamod') {
            $('#anamod-workspace-container')
                .removeClass('d-none')
                .addClass('active-pane');

            $(document).trigger(
                'aurora:view_changed',
                ['anamod']
            );
        } else if (viewMode === 'content_panel') {
            $('#content_panel-workspace-container')
                .removeClass('d-none')
                .addClass('active-pane');

            $(document).trigger(
                'aurora:view_changed',
                ['content_panel']
            );
        } else if (viewMode === 'directives_panel') {
            $('#directives_panel-workspace-container')
                .removeClass('d-none')
                .addClass('active-pane');

            $(document).trigger(
                'aurora:view_changed',
                ['directives_panel']
            );
        }
    });
// ======================================================================
// END: SYSTEM_ASSET_REFERENCE_INTEGRITY_ALIGNMENT (PATCH 1 OF 2)
// ======================================================================


// ======================================================================
// FILE: aurora/static/aurora/js/console.js (PATCH 2 OF 2)
// START: SESSION_LIFE_CYCLE_GATEKEEPER
// ======================================================================
    /**
     * Cockpit Engineering Session client.
     *
     * Engineering Session persistence is authoritative on the backend.
     * This module owns only Console presentation, elapsed-time display,
     * workspace gating, and telemetry connection state.
     */

    const engineeringSessionEndpoint =
        '/aurora/api/engineering_session/';

    function calculateElapsedSeconds(startedAt) {
        const startedTimestamp = Date.parse(startedAt);

        if (Number.isNaN(startedTimestamp)) {
            return 0;
        }

        return Math.max(
            0,
            Math.floor(
                (Date.now() - startedTimestamp) / 1000
            )
        );
    }

    function renderElapsedTime() {
        const hrs = String(
            Math.floor(elapsedSeconds / 3600)
        ).padStart(2, '0');

        const mins = String(
            Math.floor(
                (elapsedSeconds % 3600) / 60
            )
        ).padStart(2, '0');

        const secs = String(
            elapsedSeconds % 60
        ).padStart(2, '0');

        $timerDisplay.text(
            `${hrs}:${mins}:${secs}`
        );
    }

    function startElapsedDisplay(startedAt) {
        if (timerInterval) {
            clearInterval(timerInterval);
        }

        elapsedSeconds = calculateElapsedSeconds(
            startedAt
        );
        renderElapsedTime();

        timerInterval = setInterval(function() {
            elapsedSeconds = calculateElapsedSeconds(
                startedAt
            );
            renderElapsedTime();
        }, 1000);
    }

    function stopElapsedDisplay() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    function openTelemetrySocket() {
        if (
            telemetrySocket
            && (
                telemetrySocket.readyState === WebSocket.OPEN
                || telemetrySocket.readyState === WebSocket.CONNECTING
            )
        ) {
            return;
        }

        const wsScheme = (
            window.location.protocol === "https:"
                ? "wss"
                : "ws"
        );

        telemetrySocket = new WebSocket(
            `${wsScheme}://${window.location.host}/ws/console/`
        );

        telemetrySocket.onmessage = function(event) {
            const payload = JSON.parse(event.data);
            const msg = payload.message;

            const $screens = $(
                '#telemetry-screen-output, '
                + '#wu-telemetry-screen-output'
            );

            $screens.each(function() {
                const $screen = $(this);

                const $lineNode = $(
                    '<div '
                    + 'style="margin-bottom: 4px; '
                    + 'white-space: pre-wrap;">'
                    + '</div>'
                ).text(msg);

                if (
                    msg.includes(
                        '[WU ORCHESTRATION PLAN]'
                    )
                ) {
                    $lineNode.css({
                        'color': '#a78bfa',
                        'font-weight': 'bold'
                    });
                } else if (
                    msg.includes('[SYSTEM]')
                    || msg.includes('[INFO]')
                ) {
                    $lineNode.css(
                        'color',
                        '#38bdf8'
                    );
                }

                $screen.append($lineNode);
                $screen.scrollTop(
                    $screen[0].scrollHeight
                );
            });
        };

        telemetrySocket.onclose = function() {
            telemetrySocket = null;
        };
    }

    function closeTelemetrySocket() {
        if (!telemetrySocket) {
            return;
        }

        telemetrySocket.close();
        telemetrySocket = null;
    }

    function activateConsoleSession(session) {
        sessionActive = true;

        $viewSelector.prop('disabled', false);
        $gateOverlay.addClass('d-none');

        $timerToggleBtn
            .removeClass('btn-outline-success')
            .addClass('btn-outline-danger')
            .text('End Session');

        startElapsedDisplay(
            session.started_at
        );

        openTelemetrySocket();

        $(document).trigger(
            'aurora:session_started',
            [session]
        );
    }

    function deactivateConsoleSession(
        session = null,
        emitEvent = true
    ) {
        sessionActive = false;

        $viewSelector.prop('disabled', true);
        $gateOverlay.removeClass('d-none');

        $timerToggleBtn
            .removeClass('btn-outline-danger')
            .addClass('btn-outline-success')
            .text('Start Session');

        if (
            session
            && session.started_at
            && session.ended_at
        ) {
            const startedTimestamp = Date.parse(
                session.started_at
            );
            const endedTimestamp = Date.parse(
                session.ended_at
            );

            if (
                !Number.isNaN(startedTimestamp)
                && !Number.isNaN(endedTimestamp)
            ) {
                elapsedSeconds = Math.max(
                    0,
                    Math.floor(
                        (
                            endedTimestamp
                            - startedTimestamp
                        ) / 1000
                    )
                );

                renderElapsedTime();
            }
        } else {
            elapsedSeconds = 0;
            renderElapsedTime();
        }

        stopElapsedDisplay();
        closeTelemetrySocket();

        if (emitEvent) {
            $(document).trigger(
                'aurora:session_stopped',
                [
                    elapsedSeconds,
                    session,
                ]
            );
        }
    }

    function recoverEngineeringSession() {
        $.get(
            engineeringSessionEndpoint,
            function(data) {
                if (
                    data.status === 'success'
                    && data.active
                    && data.session
                ) {
                    activateConsoleSession(
                        data.session
                    );
                    return;
                }

                deactivateConsoleSession(
                    null,
                    false
                );
            }
        ).fail(function(xhr) {
            console.error(
                '[Engineering Session] '
                + 'Unable to recover session state.',
                xhr.responseText
            );

            deactivateConsoleSession(
                null,
                false
            );
        });
    }

    $timerToggleBtn.on('click', function(e) {
        e.preventDefault();

        const action = (
            sessionActive
                ? 'end'
                : 'start'
        );

        $timerToggleBtn.prop(
            'disabled',
            true
        );

        $.post(
            engineeringSessionEndpoint,
            {
                action: action
            },
            function(data) {
                if (
                    data.status !== 'success'
                    || !data.session
                ) {
                    console.error(
                        '[Engineering Session] '
                        + 'Invalid lifecycle response.',
                        data
                    );
                    return;
                }

                if (action === 'start') {
                    activateConsoleSession(
                        data.session
                    );
                } else {
                    deactivateConsoleSession(
                        data.session
                    );
                }
            }
        ).fail(function(xhr) {
            console.error(
                '[Engineering Session] '
                + `${action} failed.`,
                xhr.responseText
            );
        }).always(function() {
            $timerToggleBtn.prop(
                'disabled',
                false
            );
        });
    });

    // Restore an existing persisted Engineering Session after page refresh.
    recoverEngineeringSession();

    // Clear terminal output lines across console workspaces.
    $(document).on(
        'click',
        '#clear-telemetry-btn, #clear-wu-telemetry-btn',
        function() {
            $(
                '#telemetry-screen-output, '
                + '#wu-telemetry-screen-output'
            ).html('');
        }
    );
});
// ======================================================================
// END: SESSION_LIFE_CYCLE_GATEKEEPER (PATCH 2 OF 2)
// ======================================================================