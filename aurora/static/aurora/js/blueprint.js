// ======================================================================
// FILE: aurora/static/aurora/js/blueprint.js (PATCH 1 OF 2)
// START: BLUEPRINT_INITIALIZATION_AND_REGISTRY_POLLING
// ======================================================================
function initBlueprintConsole() {
    const $telemetryConsole = $('#telemetry-console');
    const $unlockedList = $('#unlocked-components-list');
    let sessionActive = false;

    // Enforce initial uninitialized muted gray style directly on load
    if ($telemetryConsole.length) {
        $telemetryConsole.text("[SYSTEM] Inline telemetry engine online. Awaiting commands...")
            .removeClass('text-light')
            .addClass('text-muted');
    }

    /**
     * UNLOCKED COMPONENTS REGISTRY DETERMINISTIC POLLING ENGINE
     */
    function loadUnlockedComponentsManual() {
        if (!$unlockedList.length) return;
        $unlockedList.html('<div class="text-muted p-1">[Registry] Reading database state...</div>');
        $.ajax({
            url: '/aurora/api/components/unlocked/',
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.status === 'success' && response.components) {
                    if (response.components.length === 0) {
                        $unlockedList.html('<div class="text-muted p-1">[REGISTRY] Zero unlocked assets detected.</div>');
                        return;
                    }
                    $unlockedList.empty();
                    response.components.forEach(function(item) {
                        const rowHtml = `
                        <div class="d-flex justify-content-between align-items-center p-1 border-bottom border-secondary gap-1 font-monospace" style="font-size:0.7rem; border-color: #444444 !important;">
                            <div class="text-truncate text-muted" title="${item.path}"><strong>${item.name}</strong> <span class="small opacity-75">${item.path}</span></div>
                            <button class="btn btn-outline-success btn-xs py-0 px-1 lock-component-btn flex-shrink-0" data-id="${item.id}" style="font-size:0.65rem;">Lock</button>
                        </div>`;
                        $unlockedList.append(rowHtml);
                    });
                }
            },
            error: function() {
                $unlockedList.html('<div class="text-danger p-1">[Error] Failed to poll registry records.</div>');
            }
        });
    }

    // Capture global lifecycle triggers from console.js
    $(document).on('aurora:session_started', function() {
        sessionActive = true;
        loadUnlockedComponentsManual();
    });

    $(document).on('aurora:session_stopped', function() {
        sessionActive = false;
    });
// ======================================================================
// END: BLUEPRINT_INITIALIZATION_AND_REGISTRY_POLLING (PATCH 1 OF 2)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/blueprint.js (PATCH 2 OF 2)
// START: COMPILATION_ENGINE_AND_COMPONENT_MUTATION_LISTENERS
// ======================================================================
    /**
     * Blueprint Submission Button (Command Wu)
     */
    $(document).off('click', '#submit-blueprint').on('click', '#submit-blueprint', function(e) {
        e.preventDefault();
        const blueprintText = $('#blueprint-input').val().trim();
        if (!blueprintText) {
            alert("Architectural desk error: Blueprint text field is empty.");
            return;
        }
        const $feed = $('#minion-feed');
        const $inspector = $('#inspector-output');
        const $crucible = $('#code-viewer');
        
        $feed.html('<div class="text-warning">[System] Blueprint sent to Wu. Initializing assembly line...</div>');
        $inspector.html('<div class="text-muted font-monospace small">Analyzing downstream code generation output...</div>');
        $crucible.text('# Forge processing in progress...');
        
        if ($telemetryConsole.length) {
            $telemetryConsole.html('<span class="text-info fw-bold">[SYSTEM] Resetting stream deck... Pipeline execution loop initialized...</span>');
        }

        $.ajax({
            url: '/aurora/api/command/',
            method: 'POST',
            data: { 'blueprint': blueprintText },
            dataType: 'json',
            success: function(response) {
                if (response.status === 'success') {
                    $feed.html(`<div class="text-light">[System] Code block successfully compiled by Wu.</div>`);
                    if (response.minion_log) {
                        $feed.append(`<div class="text-muted small mt-1">${response.minion_log}</div>`);
                    }
                    $crucible.text(response.generated_code);
                    $inspector.empty();
                    
                    if (response.telemetry_stream && $telemetryConsole.length) {
                        let compiledContent = "";
                        let lines = response.telemetry_stream.split('\n');
                        lines.forEach(function(rawLine) {
                            if (!rawLine.trim()) return;
                            let formattedLine = rawLine;
                            if (rawLine.includes("[ERROR]") || rawLine.includes("[CRITICAL]")) {
                                compiledContent += (compiledContent ? "\n" : "") + `<span class="text-danger fw-bold">${rawLine}</span>`;
                            } else if (rawLine.includes("SUCCESS:")) {
                                compiledContent += (compiledContent ? "\n" : "") + `<span class="text-success fw-bold">${rawLine}</span>`;
                            } else if (rawLine.includes("[FORGE_ENGINE]")) {
                                compiledContent += (compiledContent ? "\n" : "") + `<span class="text-muted">${rawLine}</span>`;
                            } else {
                                compiledContent += (compiledContent ? "\n" : "") + formattedLine;
                            }
                        });
                        $telemetryConsole.html(compiledContent).removeClass('text-muted').addClass('text-light');
                        $telemetryConsole.scrollTop($telemetryConsole.prop('scrollHeight'));
                    }

                    const val = response.validation;
                    if (val && val.valid) {
                        $inspector.append('<div class="text-success fw-bold">✔ Syntax Check: Passed Cleanly</div>');
                    } else {
                        $inspector.append('<div class="text-danger fw-bold">❌ Syntax Check: Failed</div>');
                    }
                    if (val && val.errors && val.errors.length > 0) {
                        val.errors.forEach(err => {
                            $inspector.append(`<div class="text-danger small ms-2 mt-1">• ${err}</div>`);
                        });
                    }
                    // Refresh registry on successful build pass
                    if (sessionActive) {
                        loadUnlockedComponentsManual();
                    }
                }
            },
            error: function(xhr) {
                $feed.html(`<div class="text-danger">[Error] Critical pipeline communication error occurred.</div>`);
                $inspector.html('<div class="text-danger">❌ Validation pipeline halted execution.</div>');
                $crucible.text('# Deployment stream disconnected.');
            }
        });
    });

    // Bind state event capture for lock mutation button switches
    $(document).off('click', '.lock-component-btn').on('click', '.lock-component-btn', function(e) {
        e.preventDefault();
        const componentId = $(this).data('id');
        const $row = $(this).closest('div');
        $.ajax({
            url: '/aurora/api/components/unlocked/',
            method: 'POST',
            data: { 'component_id': componentId },
            dataType: 'json',
            success: function(response) {
                if (response.status === 'success') {
                    $row.fadeOut(200, function() {
                        $(this).remove();
                        if ($unlockedList.children().length === 0) {
                            $unlockedList.html('<div class="text-muted p-1">[Registry] Zero unlocked assets detected.</div>');
                        }
                    });
                    if (response.telemetry_stream && $telemetryConsole.length) {
                        $telemetryConsole.append("\n" + response.telemetry_stream);
                        $telemetryConsole.scrollTop($telemetryConsole.prop('scrollHeight'));
                    }
                }
            }
        });
    });

    // Local code committing execution handler
    $(document).off('click', '#forge-deploy').on('click', '#forge-deploy', function(e) {
        e.preventDefault();
        const codeBlock = $('#code-viewer').text();
        if (!codeBlock || codeBlock.startsWith('#') || codeBlock.startsWith('//')) return;
        const $feed = $('#minion-feed');
        if ($feed.length) {
            $feed.append('<div class="text-info mt-2 font-monospace small">[FORGE] Committing generated modules to active local staging tree...</div>');
            $feed.scrollTop($feed.prop('scrollHeight'));
        }
    });
}

// Auto-initialize if module is loaded independently
$(document).ready(function() {
    initBlueprintConsole();
});
// ======================================================================
// END: COMPILATION_ENGINE_AND_COMPONENT_MUTATION_LISTENERS (PATCH 2 OF 2)
// ======================================================================
