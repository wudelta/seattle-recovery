// ======================================================================
// FILE: aurora/static/aurora/js/anamod.js (PATCH 1 OF 1)
// START: ANAMOD_STANDALONE_CONSOLE_CONTROLLER
// ======================================================================
/**
 * Aurora System Automation Loop - Anamod Interface Module
 * Handles local python compilation and docker verification triggers.
 */
(function(window, $) {
    'use strict';

    // Execution endpoint configuration parameters
    const SANDBOX_API_ENDPOINT = '/api/console/sandbox/';

    /**
     * Initializes structural tracking bindings for the Anamod sandbox environment.
     */
    function initAnamodConsole(csrfToken) {
        console.log("[Anamod Channel] Establishing local event listener loop bindings...");

        const $textarea = $('#code-input-area');
        const $highlightPane = $('#highlight-code-target');
        const $scrollSyncSource = $('#code-input-area');
        const $scrollSyncTarget = $('#highlight-render-pane');

        function triggerFreshHighlight() {
            if ($textarea.length && $highlightPane.length && typeof Prism !== 'undefined') {
                let rawText = $textarea.val();
                
                // Keep trailing newline if present to prevent caret position flickering on blank lines
                if (rawText[rawText.length - 1] === "\n") {
                    rawText += " ";
                }
                
                // Escape raw text blocks securely before feeding Prism engine
                const escapedText = rawText
                    .replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;");

                $highlightPane.html(escapedText);
                Prism.highlightElement($highlightPane[0]);
            }
        }

        // Run initial highlighting pass on load
        triggerFreshHighlight();

        // Catch multiple input channels to refresh layout on pastes and edits instantly
        $(document).on('input keyup paste', '#code-input-area', function() {
            triggerFreshHighlight();
        });

        // Sync dual-layer scroll positions exactly across both axes
        $(document).on('scroll', '#code-input-area', function() {
            $scrollSyncTarget.scrollTop($scrollSyncSource.scrollTop());
            $scrollSyncTarget.scrollLeft($scrollSyncSource.scrollLeft());
        });

        // Handle the UI Wipe Button through instance clear
        $(document).on('click', '#btn-clear-canvas', function(e) {
            e.preventDefault();
            $textarea.val('');
            triggerFreshHighlight();
        });

        // Wire event handlers to your custom execution triggers
        $(document).on('click', '#btn-validate-syntax', function(e) {
            e.preventDefault();
            transmitCodePayload('check_syntax', csrfToken);
        });

        $(document).on('click', '#btn-run-tests', function(e) {
            e.preventDefault();
            transmitCodePayload('run_sandbox', csrfToken);
        });
    }

    /**
     * Transmits raw string editor values downstream to the seattle_django network interface.
     */
    function transmitCodePayload(targetAction, csrfToken) {
        const payloadBlock = $('#code-input-area').val();
        const $statusBadge = $('#engine-status');
        const $statusText = $('#status-text');
        const $terminalLog = $('#terminal-log-stream');
        const $timerDisplay = $('#execution-timer');

        if ($statusBadge.length) $statusBadge.attr('class', 'status-badge status-running');
        if ($statusText.length) $statusText.text('Executing');
        
        $terminalLog.text('>> Initiating remote compilation sequence inside cluster...\n').css('color', '#eab308');

        let startTimestamp = performance.now();

        $.ajax({
            url: SANDBOX_API_ENDPOINT,
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: JSON.stringify({
                code: payloadBlock,
                action: targetAction
            }),
            success: function(response) {
                let executionTime = ((performance.now() - startTimestamp) / 1000).toFixed(2);
                $timerDisplay.text(executionTime + 's');
                if ($statusBadge.length) $statusBadge.attr('class', 'status-badge status-active');
                if ($statusText.length) $statusText.text('Sandbox Ready');

                if (response.success) {
                    $terminalLog
                        .text('>> PIPELINE SUCCESS\n\n' + (response.stdout || 'Process completed with zero returned stack logs.'))
                        .css('color', '#4ade80');
                } else {
                    $terminalLog
                        .text('>> EXECUTION REJECTED (EXIT CODE: ' + response.exit_code + ')\n\n' + (response.stderr || response.stdout))
                        .css('color', '#f43f5e');
                }
            },
            error: function(xhr) {
                let executionTime = ((performance.now() - startTimestamp) / 1000).toFixed(2);
                $timerDisplay.text(executionTime + 's');
                if ($statusBadge.length) $statusBadge.attr('class', 'status-badge status-active');
                if ($statusText.length) $statusText.text('Error State');

                let errorLog = xhr.responseJSON ? xhr.responseJSON.error : 'Network pipeline execution fault occurred.';
                $terminalLog.text('>> SYSTEM PIPELINE ERROR:\n' + errorLog).css('color', '#f43f5e');
            }
        });
    }

    // Expose registration layer parameters safely to the root context engine
    window.initAnamodConsole = initAnamodConsole;

})(window, window.jQuery);
// ======================================================================
// END: ANAMOD_STANDALONE_CONSOLE_CONTROLLER (PATCH 1 OF 1)
// ======================================================================
