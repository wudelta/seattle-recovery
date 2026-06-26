// ======================================================================
// FILE: aurora/static/aurora/js/console.js (PATCH 1 OF 2)
// START: SYSTEM ASSET REFERENCE INTEGRITY ALIGNMENT
// ======================================================================
$(document).ready(function() {
    console.log("[Aurora] Console automation loop loaded successfully.");

    // Core cockpit layout element definitions declared within the wrapper scope
    const $viewSelector = $('#console-view-selector');
    const $timerToggleBtn = $('#global-timer-toggle-btn');
    const $timerDisplay = $('#session-timer-display');
    const $gateOverlay = $('#aurora-cockpit-gate-overlay');
    const $unlockedList = $('#unlocked-components-list');

    let sessionActive = false;
    let timerInterval = null;
    let elapsedSeconds = 0;
    let telemetrySocket = null;

    function getCleanCSRFToken() {
        return $('input[name="csrfmiddlewaretoken"]').val();
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^http:.*/.test(settings.url) && !/^https:.*/.test(settings.url)) {
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
        $('.workspace-viewport .workspace-section').addClass('d-none').removeClass('active-pane');
        
        if (viewMode === 'delta_notes') {
            $('#delta-notes-workspace-container').removeClass('d-none').addClass('active-pane');
            $(document).trigger('aurora:view_changed', ['delta_notes']);
        } else if (viewMode === 'wu_chat') {
            // FIXED: Added view frame integration tracking for Wu's Orchestrator Window
            $('#wu_chat-workspace-container').removeClass('d-none').addClass('active-pane');
            $(document).trigger('aurora:view_changed', ['wu_chat']);
        } else if (viewMode === 'blueprint') {
            $('#ai-blueprint-workspace-container').removeClass('d-none').addClass('active-pane');
            $(document).trigger('aurora:view_changed', ['blueprint']);
        } else if (viewMode === 'anamod') {
            $('#anamod-workspace-container').removeClass('d-none').addClass('active-pane');
            $(document).trigger('aurora:view_changed', ['anamod']);
        } else if (viewMode === 'content_panel') {
            $('#content_panel-workspace-container').removeClass('d-none').addClass('active-pane');
            $(document).trigger('aurora:view_changed', ['content_panel']);
        } else if (viewMode === 'directives_panel') {
            $('#directives_panel-workspace-container').removeClass('d-none').addClass('active-pane');
            $(document).trigger('aurora:view_changed', ['directives_panel']);
        }
    });
// ======================================================================
// END: SYSTEM ASSET REFERENCE INTEGRITY ALIGNMENT (PATCH 1 OF 2)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/console.js (PATCH 2 OF 2)
// START: HOOK_2_SESSION_LIFE_CYCLE_GATEKEEPER
// ======================================================================
    /**
     * HOOK 2: COCKPIT SESSION LIFE-CYCLE GATEKEEPER SWITCH
     * Handles UI states and safely handles PostgreSQL session timer synchronization metrics
     */
    $timerToggleBtn.on('click', function(e) {
        e.preventDefault();
        sessionActive = !sessionActive;

        if (sessionActive) {
            // Activate session layout states
            $viewSelector.prop('disabled', false);
            $gateOverlay.addClass('d-none');
            $timerToggleBtn.removeClass('btn-outline-success').addClass('btn-outline-danger').text('Pause Session');

            timerInterval = setInterval(function() {
                elapsedSeconds++;
                const hrs = String(Math.floor(elapsedSeconds / 3600)).padStart(2, '0');
                const mins = String(Math.floor((elapsedSeconds % 3600) / 60)).padStart(2, '0');
                const secs = String(elapsedSeconds % 60).padStart(2, '0');
                $timerDisplay.text(`${hrs}:${mins}:${secs}`);
            }, 1000);

            // FIXED: Mount live asynchronous telemetry stream channels over Daphne ASGI
            let wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
            telemetrySocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/console/`);
            
            telemetrySocket.onmessage = function(event) {
                let payload = JSON.parse(event.data);
                let msg = payload.message;
                
                // Broadly updates any active terminal container mounted across snippet blocks
                let $screens = $('#telemetry-screen-output, #wu-telemetry-screen-output');
                $screens.each(function() {
                    let $screen = $(this);
                    let $lineNode = $('<div style="margin-bottom: 4px; white-space: pre-wrap;"></div>').text(msg);
                    
                    if (msg.includes('[WU ORCHESTRATION PLAN]')) {
                        $lineNode.css({ 'color': '#a78bfa', 'font-weight': 'bold' });
                    } else if (msg.includes('[SYSTEM]') || msg.includes('[INFO]')) {
                        $lineNode.css('color', '#38bdf8');
                    }
                    
                    $screen.append($lineNode);
                    $screen.scrollTop($screen[0].scrollHeight);
                });
            };

            // Broadcast session activation out to independent workspace panel listeners
            $(document).trigger('aurora:session_started');
        } else {
            // Pause session and drop layout back to locked overlay mask state
            $viewSelector.prop('disabled', true);
            $gateOverlay.removeClass('d-none');
            $timerToggleBtn.removeClass('btn-outline-danger').addClass('btn-outline-success').text('Start Session');
            
            clearInterval(timerInterval);
            
            if (telemetrySocket) {
                telemetrySocket.close();
                telemetrySocket = null;
            }

            if ($unlockedList.length) {
                $unlockedList.html('<div class="text-muted p-1">[Registry] Standing by for session initialization...</div>');
            }

            // Broadcast session termination out to independent workspace panel listeners
            $(document).trigger('aurora:session_stopped', [elapsedSeconds]);
        }
    });

    // FIXED: Clear terminal output lines across console snippets
    $(document).on('click', '#clear-telemetry-btn, #clear-wu-telemetry-btn', function() {
        $('#telemetry-screen-output, #wu-telemetry-screen-output').html('');
    });

    // FIXED: AJAX Transmission Pipeline to Fleet Commander Wu
    $(document).on('click', '#transmit-to-wu-btn', function() {
        let $textInput = $('#wu-human-delta-notes-input');
        let notes = $textInput.val().trim();
        if (!notes) return alert("Please input your design intentions first.");

        let $sendBtn = $(this);
        $sendBtn.attr('disabled', 'disabled').text('PROCESSING STRATEGY LOOP...');

        fetch('/api/chat-to-wu/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCleanCSRFToken()
            },
            body: JSON.stringify({ delta_notes: notes })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'wu_is_processing') {
                $textInput.val(''); // Clear input box on successful handoff
            } else {
                alert(`Error from fleet controller: ${data.error}`);
            }
        })
        .catch(err => console.error("Pipeline transmission error:", err))
        .finally(() => {
            $sendBtn.removeAttr('disabled').text('TRANSMIT TO COMMANDER WU');
        });
    });
});
// ======================================================================
// END: HOOK_2_SESSION_LIFE_CYCLE_GATEKEEPER (PATCH 2 OF 2)
// ======================================================================
