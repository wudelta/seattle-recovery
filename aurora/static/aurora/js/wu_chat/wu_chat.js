// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat/wu_chat.js
// START: DOM_INITIALIZATIONS_AND_STREAM_ROUTING
// ======================================================================
function initWuChatConsole(endpoints, csrfToken) {
    const inputField = $('#wu-human-delta-notes-input');
    const transmitBtn = $('#transmit-to-wu-btn');
    const telemetryLog = $('#wu-telemetry-screen-output');
    const chatHistory = $('#wu-chat-history-log');
    const approveBtn = $('#wu-review-approve-btn');
    const rejectBtn = $('#wu-review-reject-btn');

    let pendingPatch = null;

    if (!transmitBtn.length) return;

    function handleIncomingStreamData(rawData) {
        let rawStringContent = '';

        if (typeof rawData === 'object' && rawData !== null) {
            rawStringContent = JSON.stringify(rawData);
        } else if (typeof rawData === 'string') {
            rawStringContent = rawData.trim();
        }

        if (!rawStringContent) return;

        const lineNode = $(
            '<div style="margin-bottom: 2px; color: #a3a3a3;"></div>'
        ).text(rawStringContent);

        telemetryLog.append(lineNode);
        telemetryLog.scrollTop(telemetryLog[0].scrollHeight);
    }

    $(document).on(
        'aurora:telemetry_stream_received',
        function(event, data) {
            handleIncomingStreamData(data);
        }
    );

    if (window.telemetrySocket) {
        window.telemetrySocket.onmessage = function(event) {
            handleIncomingStreamData(event.data);
        };
    }
// ======================================================================
// END: DOM_INITIALIZATIONS_AND_STREAM_ROUTING
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat/wu_chat.js
// START: ENGINEERING_SESSION_INITIALIZATION
// ======================================================================
    if (
        typeof window.initWuEngineeringSession ===
        'function'
    ) {
        window.initWuEngineeringSession();
    }
// ======================================================================
// END: ENGINEERING_SESSION_INITIALIZATION
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat/wu_chat.js
// START: TRANSMIT_CLICK_EVENT_AND_AJAX_ENGINE
// ======================================================================
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
            appendSystemAlert(
                '[WARNING] Cannot transmit blank design intentions.'
            );
            return;
        }

        pendingPatch = null;

        if (window.WuDiffViewer) {
            window.WuDiffViewer.hide();
        }

        const userBubble = $(
            '<div class="p-2 rounded font-monospace small text-light" ' +
            'style="background-color: #18181b; border: 1px solid #27272a; ' +
            'align-self: flex-end; max-width: 85%; white-space: pre-wrap;"></div>'
        ).text(deltaNotesText);

        chatHistory.append(userBubble);
        chatHistory.scrollTop(chatHistory[0].scrollHeight);

        inputField.val('').prop('disabled', true);

        transmitBtn
            .prop('disabled', true)
            .text('PROCESSING REASONING LOOP...');

        appendSystemAlert(
            '🚀 [SYSTEM] Transmitting context frames to Master Orchestration Core Engine...'
        );

        const activeToken =
            csrfToken || $('[name=csrfmiddlewaretoken]').val();

        if (!window.activeChatSessionToken) {
            window.activeChatSessionToken =
                'session_' +
                Math.random().toString(36).substring(2, 11);
        }

        $.ajax({
            url: endpoints.wu_chat_endpoint,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                delta_notes: deltaNotesText,
                session_id: window.activeChatSessionToken
            }),
            headers: {
                'X-CSRFToken': activeToken
            },
            success: function(response) {
                const acceptedStatus =
                    response.status === 'success' ||
                    response.status === 'wu_is_processing';

                if (!acceptedStatus) {
                    appendSystemAlert(
                        `💥 [SYSTEM ERROR] Query failure: ${
                            response.message || 'Verification anomaly.'
                        }`
                    );
                    resetInputControls();
                    return;
                }

                const finalOutputText =
                    response.direct_text_output ||
                    response.reply ||
                    response.message ||
                    '';

                if (finalOutputText) {
                    appendWuMessage(finalOutputText);
                }

                if (response.patch_error) {
                    appendSystemAlert(
                        `💥 [PATCH ERROR] ${
                            formatPatchError(response.patch_error)
                        }`
                    );
                    resetInputControls();
                    return;
                }

                if (response.patch) {
                    pendingPatch = response.patch;

                    if (
                        window.WuDiffViewer &&
                        typeof window.WuDiffViewer.show === 'function'
                    ) {
                        window.WuDiffViewer.show(response.patch);

                        appendSystemAlert(
                            `🧩 [PATCH READY] Structured patch opened${
                                formatPatchTarget(response.patch)
                            }.`
                        );
                    } else {
                        appendSystemAlert(
                            '💥 [REVIEW ERROR] WuDiffViewer is unavailable.'
                        );
                    }
                }

                resetInputControls();
            },
            error: function(xhr) {
                let errorText = 'Unknown API Fault.';

                try {
                    const parsed = JSON.parse(xhr.responseText);
                    errorText =
                        parsed.message ||
                        parsed.error ||
                        errorText;
                } catch (e) {
                    // Preserve the generic message for non-JSON responses.
                }

                appendSystemAlert(
                    `💥 [SYSTEM ERROR] Fault response: ${errorText}`
                );
                resetInputControls();
            }
        });
    });
// ======================================================================
// END: TRANSMIT_CLICK_EVENT_AND_AJAX_ENGINE
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/wu_chat/wu_chat.js
// START: VERIFICATION_ACTIONS_AND_UI_HELPERS
// ======================================================================
    approveBtn.on('click', function() {
        if (!pendingPatch || !pendingPatch.pending_change_id) {
            appendSystemAlert(
                '💥 [PATCH ERROR] No persisted code change is available for approval.'
            );
            return;
        }

        approveBtn.prop('disabled', true);
        rejectBtn.prop('disabled', true);

        $.ajax({
            url: endpoints.wu_chat_approve_endpoint,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                pending_change_id: pendingPatch.pending_change_id
            }),
            headers: {
                'X-CSRFToken':
                    csrfToken || $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                appendSystemAlert(
                    `✅ [PATCH APPLIED] Repository file updated: ${
                        response.file_path || formatPatchTarget(pendingPatch)
                    }`
                );

                pendingPatch = null;

                if (window.WuDiffViewer) {
                    window.WuDiffViewer.hide();
                }
            },
            error: function(xhr) {
                let errorText = 'The code change could not be applied.';

                try {
                    const parsed = JSON.parse(xhr.responseText);
                    errorText = parsed.error || parsed.message || errorText;
                } catch (e) {
                    // Preserve the generic message for non-JSON responses.
                }

                appendSystemAlert(
                    `💥 [PATCH APPROVAL ERROR] ${errorText}`
                );
            },
            complete: function() {
                approveBtn.prop('disabled', false);
                rejectBtn.prop('disabled', false);
            }
        });
    });

    rejectBtn.on('click', function() {
        if (!pendingPatch || !pendingPatch.pending_change_id) {
            appendSystemAlert(
                '💥 [PATCH ERROR] No persisted code change is available for rejection.'
            );
            return;
        }

        approveBtn.prop('disabled', true);
        rejectBtn.prop('disabled', true);

        $.ajax({
            url: endpoints.wu_chat_reject_endpoint,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                pending_change_id: pendingPatch.pending_change_id
            }),
            headers: {
                'X-CSRFToken':
                    csrfToken || $('[name=csrfmiddlewaretoken]').val()
            },
            success: function() {
                pendingPatch = null;

                if (window.WuDiffViewer) {
                    window.WuDiffViewer.hide();
                }

                appendSystemAlert(
                    '🗑️ [PATCH REJECTED] The pending change was discarded without modifying the repository.'
                );
            },
            error: function(xhr) {
                let errorText = 'The code change could not be rejected.';

                try {
                    const parsed = JSON.parse(xhr.responseText);
                    errorText = parsed.error || parsed.message || errorText;
                } catch (e) {
                    // Preserve the generic message for non-JSON responses.
                }

                appendSystemAlert(
                    `💥 [PATCH REJECTION ERROR] ${errorText}`
                );
            },
            complete: function() {
                approveBtn.prop('disabled', false);
                rejectBtn.prop('disabled', false);
            }
        });
    });

    function appendWuMessage(message) {
        const wuBubble = $(
            '<div class="p-2 rounded font-monospace small text-light" ' +
            'style="background-color: #1e1b4b; border: 1px solid #312e81; ' +
            'align-self: flex-start; max-width: 85%; white-space: pre-wrap;">' +
            '<strong>Wu: </strong></div>'
        );

        wuBubble.append(document.createTextNode(message));
        chatHistory.append(wuBubble);
        chatHistory.scrollTop(chatHistory[0].scrollHeight);
    }

    function formatPatchError(patchError) {
        if (typeof patchError === 'string') {
            return patchError;
        }

        if (patchError && typeof patchError === 'object') {
            return (
                patchError.message ||
                patchError.error ||
                JSON.stringify(patchError)
            );
        }

        return 'The AI response did not contain a valid structured patch.';
    }

    function formatPatchTarget(patch) {
        if (!patch || typeof patch !== 'object') {
            return '';
        }

        const targetPath =
            patch.file_path ||
            patch.path ||
            patch.target_file;

        return targetPath ? ` for ${targetPath}` : '';
    }

    function gatherLocalChatHistory() {
        const historyArray = [];

        chatHistory.find('> div').each(function() {
            const node = $(this);
            const textContent = node.text().trim();
            const backgroundColor = node.css('background-color');

            if (backgroundColor === 'rgb(24, 24, 27)') {
                historyArray.push({
                    role: 'user',
                    text: textContent
                });
            } else if (backgroundColor === 'rgb(30, 27, 75)') {
                historyArray.push({
                    role: 'model',
                    text: textContent.replace(/^Wu:\s*/i, '')
                });
            }
        });

        return historyArray;
    }

    function resetInputControls() {
        transmitBtn
            .prop('disabled', false)
            .text('Transmit to Commander Wu');

        inputField
            .prop('disabled', false)
            .val('')
            .focus();
    }

    function appendSystemAlert(message) {
        const lineNode = $(
            '<div style="margin-bottom: 4px; color: #38bdf8;"></div>'
        ).text(message);

        telemetryLog.append(lineNode);
        telemetryLog.scrollTop(telemetryLog[0].scrollHeight);
    }

    $(document).on('aurora:telemetry_stream_ended', function() {
        resetInputControls();
    });
}
// ======================================================================
// END: VERIFICATION_ACTIONS_AND_UI_HELPERS
// ======================================================================