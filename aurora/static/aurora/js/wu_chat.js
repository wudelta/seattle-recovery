// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat.js (PATCH 1 OF 1)
// START: WU_CHAT_CONSOLE_PANEL_STREAMING_CONTROLLER
// ======================================================================
function initWuChatConsole(endpoints, csrfToken) {
  const $inputField = $('#wu-human-delta-notes-input');
  const $transmitBtn = $('#transmit-to-wu-btn');
  const $telemetryLog = $('#wu-telemetry-screen-output');
  
  // Staging elements for safety drawer workflow
  const $approvalDrawer = $('#wu-pending-transaction-drawer');
  const $approveBtn = $('#wu-action-approve-btn');
  const $destroyBtn = $('#wu-action-destroy-btn');
  let activeTransactionId = null;

  if (!$transmitBtn.length) return;

  $transmitBtn.on('click', function(e) {
    e.preventDefault();
    const deltaNotesText = $inputField.val().trim();
    if (!deltaNotesText) {
      appendSystemAlert('[WARNING] Cannot transmit blank design intentions.');
      return;
    }

    // Hide drawer from previous attempts during a new round of orchestration
    $approvalDrawer.addClass('d-none');
    activeTransactionId = null;

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
          // Display the response content in the prompt box for readability
          $inputField.val(response.direct_text_output);
          
          // Capture and stage transaction monitoring token references
          if (response.transaction_id) {
            activeTransactionId = response.transaction_id;
            $approvalDrawer.removeClass('d-none');
            appendSystemAlert('⚠️ [SAFETY GATE] Orchestration completed. Awaiting file modification permissions...');
          } else {
            resetInputControls();
          }
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

  // --- Interactive Verification Actions Routing Mappings ---
  
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

    // Build the action endpoint path pattern dynamically
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
          if (actionName === 'DESTROY') {
            $inputField.val(''); // Wipe layout space if rolled back
          }
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
    $inputField.prop('disabled', false).focus();
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
// END: WU_CHAT_CONSOLE_PANEL_STREAMING_CONTROLLER (PATCH 1 OF 1)
// ======================================================================
