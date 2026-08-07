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
     * Cockpit session life-cycle gatekeeper.
     *
     * Controls console availability, session timing, and the shared
     * telemetry WebSocket connection.
     */
    $timerToggleBtn.on('click', function(e) {
        e.preventDefault();

        sessionActive = !sessionActive;

        if (sessionActive) {
            $viewSelector.prop('disabled', false);
            $gateOverlay.addClass('d-none');

            $timerToggleBtn
                .removeClass('btn-outline-success')
                .addClass('btn-outline-danger')
                .text('Pause Session');

            timerInterval = setInterval(function() {
                elapsedSeconds++;

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
            }, 1000);

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

            $(document).trigger(
                'aurora:session_started'
            );

            return;
        }

        $viewSelector.prop('disabled', true);
        $gateOverlay.removeClass('d-none');

        $timerToggleBtn
            .removeClass('btn-outline-danger')
            .addClass('btn-outline-success')
            .text('Start Session');

        clearInterval(timerInterval);

        if (telemetrySocket) {
            telemetrySocket.close();
            telemetrySocket = null;
        }

        $(document).trigger(
            'aurora:session_stopped',
            [elapsedSeconds]
        );
    });

    // Clear terminal output lines across console workspaces
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