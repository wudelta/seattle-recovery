// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat.js (PATCH 1 OF 3)
// START: DOM_INITIALIZATIONS_AND_STREAM_ROUTING
// ======================================================================
function initWuChatConsole(endpoints, csrfToken) {
    const inputField = $('#wu-human-delta-notes-input');
    const transmitBtn = $('#transmit-to-wu-btn');
    const telemetryLog = $('#wu-telemetry-screen-output');
    const chatHistory = $('#wu-chat-history-log');
    const approvalDrawer = $('#wu-pending-transaction-drawer');
    const approveBtn = $('#wu-action-approve-btn');
    const destroyBtn = $('#wu-action-destroy-btn');
    let activeTransactionId = null;
    let $currentWuBubble = null;

    if (!transmitBtn.length) return;

    function handleIncomingStreamData(rawData) {
        let rawStringContent = "";
        if (typeof rawData === 'object' && rawData !== null) {
            rawStringContent = JSON.stringify(rawData);
        } else if (typeof rawData === 'string') {
            rawStringContent = rawData.trim();
        }

        // REMOVED legacy Groq WebSocket text match conditionals.
        // Pure text string operations fall cleanly directly to our telemetry view logs monitor.
        if (rawStringContent.trim()) {
            const lineNode = $('<div style="margin-bottom: 2px; color: #a3a3a3;"></div>').text(rawStringContent);
            telemetryLog.append(lineNode);
            telemetryLog.scrollTop(telemetryLog[0].scrollHeight);
        }
    }

    $(document).on('aurora:telemetry_stream_received', function(event, data) {
        handleIncomingStreamData(data);
    });

    if (window.telemetrySocket) {
        window.telemetrySocket.onmessage = function(e) {
            handleIncomingStreamData(e.data);
        };
    }
// ======================================================================
// END: DOM_INITIALIZATIONS_AND_STREAM_ROUTING (PATCH 1 OF 3)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat.js (PATCH 2 OF 3)
// START: TRANSMIT_CLICK_EVENT_AND_AJAX_ENGINE
// ======================================================================
// FIXED: Active keydown listener to trigger transmission loop on Enter, while allowing Shift+Enter for carriage returns
inputField.on('keydown', function(e) {
    if (e.which === 13 && !e.shiftKey) {
        e.preventDefault();
        transmitBtn.click();
    }
});

transmitBtn.on('click', function(e) {
    e.preventDefault();
    const deltaNotesText = inputField.val().trim();
    if (!deltaNotesText) {
        appendSystemAlert('[WARNING] Cannot transmit blank design intentions.');
        return;
    }
    approvalDrawer.addClass('d-none');
    activeTransactionId = null;

    const userBubble = $('<div class="p-2 rounded font-monospace small text-light" style="background-color: #18181b; border: 1px solid #27272a; align-self: flex-end; max-width: 85%; white-space: pre-wrap;"></div>').text(deltaNotesText);
    chatHistory.append(userBubble);
    chatHistory.scrollTop(chatHistory[0].scrollHeight);

    inputField.val('').prop('disabled', true);
    transmitBtn.prop('disabled', true).text('PROCESSING REASONING LOOP...');
    appendSystemAlert('🚀 [SYSTEM] Transmitting context frames to Master Orchestration Core Engine...');

    const activeToken = csrfToken || $('[name=csrfmiddlewaretoken]').val();
    
    // FIXED: Generate or retrieve a persistent browser thread identifier signature
    if (!window.activeChatSessionToken) {
        window.activeChatSessionToken = "session_" + Math.random().toString(36).substring(2, 11);
    }

    // FIXED: Re-routed from standalone gemini stream straight to our secure database ledger endpoint
    $.ajax({
        url: endpoints.wu_chat_endpoint,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 
            delta_notes: deltaNotesText,
            session_id: window.activeChatSessionToken
        }),
        headers: { 'X-CSRFToken': activeToken },
        success: function(response) {
            // FIXED: Support both view response formats ('success' and 'wu_is_processing') safely
            if (response.status === 'success' || response.status === 'wu_is_processing') {
                const finalOutputText = response.direct_text_output || response.reply || "No response received.";
                
                const $wuBubble = $('<div class="p-2 rounded font-monospace small text-light" style="background-color: #1e1b4b; border: 1px solid #312e81; align-self: flex-start; max-width: 85%; white-space: pre-wrap;"><strong>Wu: </strong></div>');
                $wuBubble.append(document.createTextNode(finalOutputText));
                chatHistory.append($wuBubble);
                chatHistory.scrollTop(chatHistory[0].scrollHeight);

                if (response.mutations && response.mutations.length > 0) {
                    response.mutations.forEach(function(m) {
                        appendSystemAlert(`🛠️ [MUTATION]: ${m}`);
                    });
                }

                if (response.transaction_id) {
                    activeTransactionId = response.transaction_id;
                    approvalDrawer.removeClass('d-none');
                    appendSystemAlert('⚠️ [SAFETY GATE] Actions queued. Awaiting permissions confirmation...');
                }
            } else {
                appendSystemAlert(`💥 [SYSTEM ERROR] Query failure: ${response.message || 'Verification anomaly.'}`);
            }
            resetInputControls();
        },
        error: function(xhr) {
            let errorText = 'Unknown API Fault.';
            try {
                const parsed = JSON.parse(xhr.responseText);
                errorText = parsed.message || parsed.error || errorText;
            } catch(e) {}
            appendSystemAlert(`💥 [SYSTEM ERROR] Fault response: ${errorText}`);
            resetInputControls();
        }
    });
});
// ======================================================================
// END: TRANSMIT_CLICK_EVENT_AND_AJAX_ENGINE (PATCH 2 OF 3)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat.js (PATCH 3 OF 3)
// START: VERIFICATION_ACTIONS_AND_UI_HELPERS
// ======================================================================
    approveBtn.on('click', function() {
        executeTransactionAction('APPROVE', '🛠️ [SYSTEM] Authorizing file creation scripts...');
    });

    destroyBtn.on('click', function() {
        executeTransactionAction('DESTROY', '🛑 [SYSTEM] Triggering surgical asset rollback execution sequence...');
    });

    function executeTransactionAction(actionName, systemLogMessage) {
        if (!activeTransactionId) return;
        appendSystemAlert(systemLogMessage);
        approvalDrawer.addClass('d-none');
        
        // Aligned perfectly with Nginx proxy route patterns passing directly down to core_logic
        const actionUrl = `/aurora/api/transaction/${activeTransactionId}/action/`;
        
        $.ajax({
            url: actionUrl,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ action: actionName }),
            headers: { 'X-CSRFToken': csrfToken },
            success: function(response) {
                if (response.status === 'SUCCESS') {
                    appendSystemAlert(`✅ [ACTION SUCCESS]: ${response.message}`);
                } else {
                    appendSystemAlert(`💥 [ACTION FAULT]: Request failed context response.`);
                }
                resetInputControls();
            },
            error: function(xhr) {
                appendSystemAlert('💥 [ACTION FAULT]: Error communicating with verification endpoint nodes.');
                resetInputControls();
            }
        });
    }

    // NEW UTILITY: Scrapes the live DOM message list state to populate Gemini's persistent chat arrays
    function gatherLocalChatHistory() {
        const historyArray = [];
        chatHistory.find('> div').each(function() {
            const $node = $(this);
            const textContent = $node.text().trim();
            if ($node.css('background-color') === 'rgb(24, 24, 27)') {
                historyArray.push({ role: 'user', text: textContent });
            } else if ($node.css('background-color') === 'rgb(30, 27, 75)') {
                // Stripping out the 'Wu: ' identifier prefix token string
                const cleanedText = textContent.replace(/^Wu:\s*/i, '');
                historyArray.push({ role: 'model', text: cleanedText });
            }
        });
        return historyArray;
    }

    function resetInputControls() {
        transmitBtn.prop('disabled', false).text('Transmit to Commander Wu');
        inputField.prop('disabled', false).val('').focus();
    }

    function appendSystemAlert(message) {
        const lineNode = $('<div style="margin-bottom: 4px; color: #38bdf8;"></div>').text(message);
        telemetryLog.append(lineNode);
        telemetryLog.scrollTop(telemetryLog[0].scrollHeight);
    }

    $(document).on('aurora:telemetry_stream_ended', function() {
        resetInputControls();
    });
}
// ======================================================================
// END: VERIFICATION_ACTIONS_AND_UI_HELPERS (PATCH 3 OF 3)
// ======================================================================
