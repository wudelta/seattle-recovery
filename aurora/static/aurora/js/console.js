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
            // Broadcast session activation out to independent workspace panel listeners
            $(document).trigger('aurora:session_started');
        } else {
            // Pause session and drop layout back to locked overlay mask state
            $viewSelector.prop('disabled', true);
            $gateOverlay.removeClass('d-none');
            $timerToggleBtn.removeClass('btn-outline-danger').addClass('btn-outline-success').text('Start Session');
            clearInterval(timerInterval);
            if ($unlockedList.length) {
                $unlockedList.html('<div class="text-muted p-1">[Registry] Standing by for session initialization...</div>');
            }
            // Broadcast session termination out to independent workspace panel listeners
            $(document).trigger('aurora:session_stopped', [elapsedSeconds]);
        }
    });
});
// ======================================================================
// END: HOOK_2_SESSION_LIFE_CYCLE_GATEKEEPER (PATCH 2 OF 2)
// ======================================================================
