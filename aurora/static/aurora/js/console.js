// aurora/static/aurora/js/console.js

$(document).ready(function() {
    
    // Helper function to extract Django's CSRF token cookie for secure offline POST requests
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Setup jQuery AJAX defaults to inject the CSRF token into request headers automatically
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^http:.*/.test(settings.url) && !/^https:.*/.test(settings.url)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    /**
     * TRIGGER POINT 1: Blueprint Submission (Commanding Wu)
     */
    $('#submit-blueprint').on('click', function() {
        const blueprintText = $('#blueprint-input').val().trim();
        
        // Block empty actions to save processing cycles
        if (!blueprintText) return;

        const $feed = $('#minion-feed');
        const $inspector = $('#inspector-output');
        const $crucible = $('#code-viewer');

        // 1. Update UI to reflect blueprint dispatching status
        $feed.html('<div class="text-warning">[System] Blueprint sent to Wu. Initializing assembly line...</div>');
        $inspector.html('<div class="text-muted">Analyzing downstream code generation output...</div>');
        $crucible.text('# Forge processing in progress...');

        // 2. Dispatch instruction packet to local API View routing node
        $.ajax({
            url: '/aurora/api/command/',
            method: 'POST',
            data: { 'blueprint': blueprintText },
            dataType: 'json',
            success: function(response) {
                if (response.status === 'success') {
                    // Update Minion Tracking Feed Panel
                    $feed.append(`<div class="text-light mt-1">${response.minion_log}</div>`);
                    $feed.append('<div class="text-success">[System] Code block successfully compiled by Wu.</div>');

                    // Update Code Crucible Visual Panel
                    $crucible.text(response.generated_code);

                    // Parse & Render Validation Inspector Panel (Spyder Engine Replacement)
                    const val = response.validation;
                    $inspector.empty();

                    if (val.valid) {
                        $inspector.append('<div class="text-success">✔ Syntax Check: Passed cleanly</div>');
                    } else {
                        $inspector.append('<div class="text-danger">❌ Syntax Check: Failed</div>');
                    }

                    // Loop and stream errors out to view screen
                    if (val.errors && val.errors.length > 0) {
                        val.errors.forEach(err => {
                            $inspector.append(`<div class="text-danger small ms-2">• ${err}</div>`);
                        });
                    }

                    // Loop and stream warnings out to view screen (Unused imports, variables)
                    if (val.warnings && val.warnings.length > 0) {
                        $inspector.append('<div class="text-warning mt-2">⚠ Code Metrics Warnings:</div>');
                        val.warnings.forEach(warn => {
                            $inspector.append(`<div class="text-warning small ms-2">• ${warn}</div>`);
                        });
                    }
                }
            },
            error: function(xhr) {
                let errorMsg = 'Critical pipeline communication error occurred.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                $feed.html(`<div class="text-danger">[Error] ${errorMsg}</div>`);
                $inspector.html('<div class="text-danger">❌ Validation pipeline halted execution.</div>');
                $crucible.text('# Deployment stream disconnected.');
            }
        });
    });

    /**
     * TRIGGER POINT 2: Forge & Deploy Execution (Staging approved modules)
     */
    $('#forge-deploy').on('click', function() {
        const codeBlock = $('#code-viewer').text();
        if (!codeBlock || codeBlock.startsWith('#')) return;

        $('#minion-feed').append('<div class="text-info mt-2">[Forge] Committing generated modules to active local staging tree...</div>');
        // This will hook straight into your GitHub git automation module next
    });

});
