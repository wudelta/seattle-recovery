// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat.js (PATCH 1 OF 1)
// START: WU_CHAT_CONSOLE_PANEL_STREAMING_CONTROLLER
// ======================================================================
function initWuChatConsole(endpoints, csrfToken) {
    const $inputField = $('#wu-human-delta-notes-input');
    const $transmitBtn = $('#transmit-to-wu-btn');
    const $telemetryLog = $('#wu-telemetry-screen-output');

    if (!$transmitBtn.length) return;

    $transmitBtn.on('click', function(e) {
        e.preventDefault();
        const deltaNotesText = $inputField.val().trim();
        
        if (!deltaNotesText) {
            appendSystemAlert('[WARNING] Cannot transmit blank design intentions.');
            return;
        }

        // Apply interactive locked interface states to prevent multi-click racing operations
        $transmitBtn.prop('disabled', true).text('PROCESSING STRATEGY LOOP...');
        $inputField.prop('disabled', true);
        appendSystemAlert('🚀 [SYSTEM] Transmitting design intentions to Commander Wu...');

        $.ajax({
            url: endpoints.wu_chat_endpoint,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ delta_notes: deltaNotesText }),
            headers: { 'X-CSRFToken': csrfToken },
            success: function(response) {
                if (response.status === 'wu_is_processing') {
                    $inputField.val(''); // Wipe text input layout upon clear transmission handoff
                } else {
                    appendSystemAlert(`💥 [SYSTEM ERROR] Unexpected response status: ${response.status}`);
                    resetInputControls();
                }
            },
            error: function(xhr) {
                let errorText = 'Unknown API Fault.';
                try {
                    const parsed = JSON.parse(xhr.responseText);
                    errorText = parsed.error || errorText;
                } catch(e) {}
                appendSystemAlert(`💥 [SYSTEM ERROR] Fault response: ${errorText}`);
                resetInputControls();
            }
        });
    });

    function resetInputControls() {
        $transmitBtn.prop('disabled', false).text('Transmit to Commander Wu');
        $inputField.prop('disabled', false).focus();
    }

    function appendSystemAlert(message) {
        const $lineNode = $('<div style="margin-bottom: 4px; color: #38bdf8;"></div>').text(message);
        $telemetryLog.append($lineNode);
        $telemetryLog.scrollTop($telemetryLog[0].scrollHeight);
    }

    // Intercept global custom events fired when the Daphne socket ends execution loops
    $(document).on('aurora:telemetry_stream_ended', function() {
        resetInputControls();
    });
}
// ======================================================================
// END: WU_CHAT_CONSOLE_PANEL_STREAMING_CONTROLLER (PATCH 1 OF 1)
// ======================================================================
