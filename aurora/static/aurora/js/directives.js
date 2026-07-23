// ======================================================================
// FILE: aurora/static/aurora/js/directives.js (PATCH 1 OF 2)
// START: DIRECTIVES_PANEL_INITIALIZATION_AND_INVENTORY_PIPES
// ======================================================================
function initDirectivesConsole(endpoints, csrfToken) {
    const $wrapper = $('#directives-module-wrapper');
    if (!$wrapper.length) return;

    let activeAssetId = null;
    const apiURL = endpoints.directives_endpoint;

    function logToStream(text, isError = false) {
        const timestamp = new Date().toLocaleTimeString();
        const indicator = isError ? '[ERROR]' : '[SUCCESS]';
        const colorClass = isError ? 'text-danger' : 'text-success';
        const rawLine = `\n[${timestamp}] ${indicator} ${text}`;
        const $stream = $('#dc-terminal-stream');
        $stream.append($('<span>').addClass(colorClass).text(rawLine));
        if ($stream.length) {
            $stream.scrollTop($stream.scrollHeight);
        }
    }

    function fetchInventory() {
        const currentScope = $('input[name="dc-status-filter"]:checked').val();
        $.ajax({
            url: apiURL,
            type: 'GET',
            data: { status: currentScope },
            success: function(response) {
                if (response.status === 'SUCCESS') {
                    const $list = $('#dc-inventory-list').empty();
                    if (!response.inventory.length) {
                        $list.append('<div class="text-muted text-center p-3 small italic">No prompts found.</div>');
                        return;
                    }
                    response.inventory.forEach(function(item) {
                        const labelState = item.is_active ? 'success' : 'secondary';
                        const badgeText = item.is_active ? 'ACTIVE' : 'INACTIVE';
                        const $row = $(`
                            <div class="d-flex align-items-center justify-content-between p-1 rounded border border-dark bg-black text-light" style="cursor:pointer;" data-id="${item.id}">
                                <div class="text-truncate flex-grow-1 me-1">
                                    <span class="badge bg-opacity-25 bg-${labelState} text-${labelState} font-monospace me-1" style="font-size:0.65rem;">${badgeText}</span>
                                    <span class="font-monospace small">${item.directive_name}</span>
                                </div>
                                <span class="text-muted" style="font-size:0.7rem; font-style:italic;">${item.date_modified}</span>
                            </div>
                        `);
                        if(activeAssetId === item.id) {
                            $row.addClass('border-warning').css('background-color', '#1b1b1b');
                        }
                        $list.append($row);
                    });
                }
            },
            error: function(xhr) {
                logToStream(`Inventory registry retrieval fault: ${xhr.status}`, true);
            }
        });
    }

    // FIX: Intercept real-time tokens out of the global Daphne consumer pipe to unlock form input controls
    $(document).on('aurora:telemetry_stream', function(event, messageChunk) {
        if (!messageChunk) return;
        if (messageChunk.includes('[SYSTEM] Prompt optimization finalized.')) {
            $('#dc-distill-btn').prop('disabled', false).text('✨ Distill Prompt');
            $('#dc-rich-editor').attr('contenteditable', 'true').css('opacity', '1').focus();
        }
    });
// ======================================================================
// END: DIRECTIVES_PANEL_INITIALIZATION_AND_INVENTORY_PIPES (PATCH 1 OF 2)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/directives.js (PATCH 2 OF 2)
// START: DIRECTIVES_PANEL_MUTATION_OPERATIONS_AND_EVENT_BINDINGS
// ======================================================================
function clearWorkspaceForm() {
    activeAssetId = null;
    $('#dc-field-id').val('');
    $('#dc-field-name').val('');
    $('#dc-field-constraints').val('{\n  "model_profile": "medium",\n  "temperature": 0.3\n}');
    $('#dc-field-active').prop('checked', true);
    $('#dc-rich-editor').html('');
    $('#dc-active-asset-indicator').text('🆕 COMPOSING NEW MASTER MINION PROMPT DIRECTIVE').addClass('text-warning').removeClass('text-info');
    $('#dc-delete-btn').prop('disabled', true);
    fetchInventory();
}

// Inject the custom Distill button layout cleanly into the header indicator bar context
$('#dc-active-asset-indicator').after(
    $('<button>')
        .attr('id', 'dc-distill-btn')
        .addClass('btn btn-outline-warning btn-xs py-0 px-2 font-monospace text-uppercase ms-2')
        .css({ 'font-size': '0.7rem', 'line-height': '1.5' })
        .attr('title', 'Send conversational rambling text to minion_AI_writer')
        .text('✨ Distill Prompt')
);

// --- NEW INTERACTIVE ACTION LINK: DISPATCH TO MINION_AI_WRITER ---
$(document).on('click', '#dc-distill-btn', function() {
    const rawRambling = $('#dc-rich-editor').text().trim();
    const minionName = $('#dc-field-name').val().trim() || 'unnamed_minion';

    if (!rawRambling) {
        logToStream("Validation blocked: Rich text instructions field is empty.", true);
        return;
    }

    // Apply interactive lock layers to prevent multi-transmission collisions
    const $btn = $(this);
    $btn.prop('disabled', true).text('DISTILLING PROMPT...');
    $('#dc-rich-editor').attr('contenteditable', 'false').css('opacity', '0.5');
    logToStream(`Dispatched prompt lines for '${minionName}' to optimization pipeline engine...`);

    $.ajax({
        url: apiURL,
        type: 'POST',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        data: JSON.stringify({
            action: 'optimize_prompt',
            directive_name: minionName,
            instructions: rawRambling
        }),
        error: function(xhr) {
            logToStream("Prompt optimization request execution pipeline fault.", true);
            $btn.prop('disabled', false).text('✨ Distill Prompt');
            $('#dc-rich-editor').attr('contenteditable', 'true').css('opacity', '1');
        }
    });
});

$(document).on('click', '#dc-inventory-list [data-id]', function() {
    const targetId = $(this).data('id');
    $.ajax({
        url: apiURL,
        type: 'GET',
        data: { id: targetId },
        success: function(response) {
            if (response.status === 'SUCCESS') {
                const asset = response.asset;
                activeAssetId = asset.id;
                $('#dc-field-id').val(asset.id);
                $('#dc-field-name').val(asset.directive_name);
                $('#dc-field-constraints').val(JSON.stringify(asset.constraints, null, 2));
                $('#dc-field-active').prop('checked', asset.is_active);
                $('#dc-rich-editor').html(asset.instructions);
                $('#dc-active-asset-indicator').text(`📑 DIRECTIVE LOADED: ${asset.id}`).addClass('text-info').removeClass('text-warning');
                $('#dc-delete-btn').prop('disabled', false);
                logToStream(`Loaded minion asset structure: "${asset.directive_name}" [Author: ${asset.author}].`);
                fetchInventory();
            }
        },
        error: function(xhr) {
            logToStream(`Fetch transaction rejected.`, true);
        }
    });
});

$('#dc-save-btn').on('click', function() {
    let parsedConstraints = {};
    try {
        parsedConstraints = JSON.parse($('#dc-field-constraints').val() || '{}');
    } catch(e) {
        logToStream("Validation blocked: Constraints must be a well-formed JSON object block.", true);
        return;
    }
    const payload = {
        id: $('#dc-field-id').val() || null,
        directive_name: $('#dc-field-name').val().trim(),
        constraints: parsedConstraints,
        is_active: $('#dc-field-active').is(':checked'),
        instructions: $('#dc-rich-editor').html()
    };
    if (!payload.directive_name || !payload.instructions) {
        logToStream("Validation blocked: System lookup name and payload instructions are required fields.", true);
        return;
    }
    $.ajax({
        url: apiURL,
        type: 'POST',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        data: JSON.stringify(payload),
        success: function(response) {
            if (response.status === 'SUCCESS') {
                logToStream(`Transaction applied. Block status: [${response.action}] UUID: ${response.id}`);
                activeAssetId = response.id;
                fetchInventory();
            }
        },
        error: function(xhr) {
            logToStream(`Save processing pipeline exception.`, true);
        }
    });
});

$('#dc-delete-btn').on('click', function() {
    if (!activeAssetId || !confirm("Execute database mutation statement? This permanently prunes this prompt configuration.")) return;
    $.ajax({
        url: apiURL,
        type: 'DELETE',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        data: JSON.stringify({ id: activeAssetId }),
        success: function(response) {
            if (response.status === 'SUCCESS') {
                logToStream(`System purge confirmed. Object payload UUID erased.`);
                clearWorkspaceForm();
            }
        },
        error: function(xhr) {
            logToStream(`Destruction protocol rejected.`, true);
        }
    });
});

$('#dc-clear-btn').on('click', clearWorkspaceForm);
$('#dc-new-prompt-btn').on('click', clearWorkspaceForm);
$('input[name="dc-status-filter"]').on('change', fetchInventory);
fetchInventory();
}
// ======================================================================
// END: DIRECTIVES_PANEL_MUTATION_OPERATIONS_AND_EVENT_BINDINGS (PATCH 2 OF 2)
// ======================================================================
