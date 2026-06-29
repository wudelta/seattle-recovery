// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat.js (PATCH 1 OF 3)
// START: WU_CHAT_STREAM_PROCESSOR_AND_SELECTORS
// ======================================================================
function initWuChatConsole(endpoints, csrfToken) {
  const $inputField = $('#wu-human-delta-notes-input');
  const $transmitBtn = $('#transmit-to-wu-btn');
  const $telemetryLog = $('#wu-telemetry-screen-output');
  const $chatHistory = $('#wu-chat-history-log');
  
  const $approvalDrawer = $('#wu-pending-transaction-drawer');
  const $approveBtn = $('#wu-action-approve-btn');
  const $destroyBtn = $('#wu-action-destroy-btn');
  
  let activeTransactionId = null;
  let $currentWuBubble = null;

  if (!$transmitBtn.length) return;

  function handleIncomingStreamData(rawData) {
    let payload = null;
    let isJsonPacket = false;
    let rawStringContent = "";

    try {
      // FIX: Hardened validation layer to safely intercept pre-parsed object 
      // dictionaries as well as raw strings without falling through to the catch block.
      if (typeof rawData === 'object' && rawData !== null) {
        payload = rawData;
        isJsonPacket = (payload.event !== undefined);
        rawStringContent = JSON.stringify(rawData);
      } else if (typeof rawData === 'string') {
        rawStringContent = rawData.trim();
        if (rawStringContent.startsWith('{') || rawStringContent.startsWith('[')) {
          payload = JSON.parse(rawStringContent);
          isJsonPacket = (payload && payload.event !== undefined);
        }
      }

      // Route tokens straight to the chat view logs
      if (isJsonPacket && payload.event === 'wu_chat_token' && payload.text) {
        if (!$currentWuBubble) {
          $currentWuBubble = $('<div class="p-2 rounded font-monospace small text-light" style="background-color: #1e1b4b; border: 1px solid #312e81; align-self: flex-start; max-width: 85%; white-space: pre-wrap;"><strong>Wu: </strong></div>');
          $chatHistory.append($currentWuBubble);
        }
        $currentWuBubble.append(document.createTextNode(payload.text));
        $chatHistory.scrollTop($chatHistory[0].scrollHeight);
        return; // Handled, block fallback logs
      } 
      // FIX: Cleanly catch the pre-parsed object termination event, reset bubbles, 
      // and invoke the unfreeze controllers instantly.
      else if (isJsonPacket && payload.event === 'wu_chat_complete') {
        appendSystemAlert('📡 [SYSTEM]: Orchestrator response transaction complete.');
        $currentWuBubble = null;
        resetInputControls();
        return;
      }
    } catch (parseError) {
      isJsonPacket = false;
    }

    // Filter out any JSON structures from leaking into the terminal log view
    if (rawStringContent.trim() && !rawStringContent.includes('"event":')) {
      const $lineNode = $('<div style="margin-bottom: 2px; color: #a3a3a3;"></div>').text(rawStringContent);
      $telemetryLog.append($lineNode);
      $telemetryLog.scrollTop($telemetryLog[0].scrollHeight);
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
// END: WU_CHAT_STREAM_PROCESSOR_AND_SELECTORS (PATCH 1 OF 3)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat.js (PATCH 2 OF 3)
// START: WU_CHAT_TRANSMIT_ACTION_HANDLER
// ======================================================================
  $transmitBtn.on('click', function(e) {
    e.preventDefault();
    const deltaNotesText = $inputField.val().trim();
    if (!deltaNotesText) {
      appendSystemAlert('[WARNING] Cannot transmit blank design intentions.');
      return;
    }

    $approvalDrawer.addClass('d-none');
    activeTransactionId = null;

    // Append your prompt message clean and isolated to the left chat log view pane
    const $userBubble = $('<div class="p-2 rounded font-monospace small text-light" style="background-color: #18181b; border: 1px solid #27272a; align-self: flex-end; max-width: 85%; white-space: pre-wrap;"></div>').text(deltaNotesText);
    $chatHistory.append($userBubble);
    $chatHistory.scrollTop($chatHistory[0].scrollHeight);

    // Freeze input controls and update state indicators during transaction runs
    $inputField.val('').prop('disabled', true);
    $transmitBtn.prop('disabled', true).text('PROCESSING STRATEGY LOOP...');
    appendSystemAlert('🚀 [SYSTEM] Transmitting design intentions to Commander Wu...');

    $.ajax({
      url: endpoints.wu_chat_endpoint,
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ delta_notes: deltaNotesText }),
      headers: { 'X-CSRFToken': csrfToken },
      success: function(response) {
        if (response.status === 'wu_is_processing') {
          // FIX: Bypassed volatile websocket timing constraints. Render the full completed
          // orchestrator text response bubble directly into the chat history pane layout
          // upon successful HTTP callback return.
          const finalOutputText = response.direct_text_output || "No explicit response text returned.";
          const $wuBubble = $('<div class="p-2 rounded font-monospace small text-light" style="background-color: #1e1b4b; border: 1px solid #312e81; align-self: flex-start; max-width: 85%; white-space: pre-wrap;"><strong>Wu: </strong></div>');
          $wuBubble.append(document.createTextNode(finalOutputText));
          $chatHistory.append($wuBubble);
          $chatHistory.scrollTop($chatHistory[0].scrollHeight);
          
          if (response.transaction_id) {
            activeTransactionId = response.transaction_id;
            $approvalDrawer.removeClass('d-none');
            appendSystemAlert('⚠️ [SAFETY GATE] Orchestration completed. Awaiting file modification permissions...');
          }
        } else {
          appendSystemAlert(`💥 [SYSTEM ERROR] Unexpected response status: ${response.status}`);
        }
        resetInputControls(); // FIX: Instantly release lockout state to let the user type infinite replies
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
// ======================================================================
// END: WU_CHAT_TRANSMIT_ACTION_HANDLER (PATCH 2 OF 3)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat.js (PATCH 3 OF 3)
// START: WU_CHAT_APPROVAL_BUTTONS_AND_UTILITIES
// ======================================================================
  $approveBtn.on('click', function() {
    executeTransactionAction('APPROVE', '🛠️ [SYSTEM] Authorizing file creation scripts...');
  });

  $destroyBtn.on('click', function() {
    executeTransactionAction('DESTROY', '🛑 [SYSTEM] Triggering surgical asset rollback execution sequence...');
  });

  function executeTransactionAction(actionName, systemLogMessage) {
    if (!activeTransactionId) return;
    
    appendSystemAlert(systemLogMessage);
    $approvalDrawer.addClass('d-none');

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

  function resetInputControls() {
    $transmitBtn.prop('disabled', false).text('Transmit to Commander Wu');
    $inputField.prop('disabled', false).val('').focus();
  }

  function appendSystemAlert(message) {
    const $lineNode = $('<div style="margin-bottom: 4px; color: #38bdf8;"></div>').text(message);
    $telemetryLog.append($lineNode);
    $telemetryLog.scrollTop($telemetryLog[0].scrollHeight);
  }

  $(document).on('aurora:telemetry_stream_ended', function() {
    resetInputControls();
  });
}
// ======================================================================
// END: WU_CHAT_APPROVAL_BUTTONS_AND_UTILITIES (PATCH 3 OF 3)
// ======================================================================
