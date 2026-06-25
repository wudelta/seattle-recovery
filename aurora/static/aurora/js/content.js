// ======================================================================
// FILE: aurora/static/aurora/js/content.js (PATCH 1 OF 1)
// START: CONTENT_PANEL_ORCHESTRATOR_LOGIC
// ======================================================================
function initContentConsole(endpoints, csrfToken) {
    const $wrapper = $('#content-module-wrapper');
    if (!$wrapper.length) return;

    let activeAssetId = null;
    const apiURL = endpoints.content_endpoint;

    function logToStream(text, isError = false) {
        const timestamp = new Date().toLocaleTimeString();
        const indicator = isError ? '[ERROR]' : '[SUCCESS]';
        const colorClass = isError ? 'text-danger' : 'text-success';
        const rawLine = `\n[${timestamp}] ${indicator} ${text}`;
        
        const $stream = $('#cc-terminal-stream');
        $stream.append($('<span>').addClass(colorClass).text(rawLine));
        if ($stream.length) {
            $stream.scrollTop($stream[0].scrollHeight);
        }
    }

    function fetchInventory() {
        const currentScope = $('input[name="cc-app-filter"]:checked').val();
        
        $.ajax({
            url: apiURL,
            type: 'GET',
            data: { application: currentScope },
            success: function(response) {
                if (response.status === 'SUCCESS') {
                    const $list = $('#cc-inventory-list').empty();
                    if (!response.inventory.length) {
                        $list.append('<div class="text-muted text-center p-3 small italic">No records found.</div>');
                        return;
                    }
                    response.inventory.forEach(function(item) {
                        const labelApp = item.application === 'aurora' ? 'info' : 'warning';
                        const $row = $(`
                            <div class="d-flex align-items-center justify-content-between p-1 rounded border border-dark bg-black text-light" style="cursor:pointer;" data-id="${item.id}">
                                <div class="text-truncate flex-grow-1 me-1">
                                    <span class="badge bg-opacity-25 bg-${labelApp} text-${labelApp} font-monospace me-1" style="font-size:0.65rem;">${item.application.toUpperCase()}</span>
                                    <span class="font-monospace small">${item.title}</span>
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

    function clearWorkspaceForm() {
        activeAssetId = null;
        $('#cc-field-id').val('');
        $('#cc-field-title').val('');
        $('#cc-field-application').val('aurora');
        $('#cc-field-html').val('');
        $('#cc-active-asset-indicator').text('🆕 COMPOSING NEW STANDALONE STATIC ASSET').addClass('text-warning').removeClass('text-info');
        $('#cc-delete-btn').prop('disabled', true);
        fetchInventory();
    }

    $(document).on('click', '#cc-inventory-list [data-id]', function() {
        const targetId = $(this).data('id');
        $.ajax({
            url: apiURL,
            type: 'GET',
            data: { id: targetId },
            success: function(response) {
                if (response.status === 'SUCCESS') {
                    const asset = response.asset;
                    activeAssetId = asset.id;
                    $('#cc-field-id').val(asset.id);
                    $('#cc-field-title').val(asset.title);
                    $('#cc-field-application').val(asset.application);
                    $('#cc-field-html').val(asset.html_content);
                    $('#cc-active-asset-indicator').text(`📑 ASSET LOADED: ${asset.id}`).addClass('text-info').removeClass('text-warning');
                    $('#cc-delete-btn').prop('disabled', false);
                    logToStream(`Loaded document asset structure: "${asset.title}" [Author: ${asset.author}].`);
                    fetchInventory();
                }
            },
            error: function(xhr) {
                logToStream(`Fetch transaction rejected.`, true);
            }
        });
    });

    $('#cc-save-btn').on('click', function() {
        const payload = {
            id: $('#cc-field-id').val() || null,
            title: $('#cc-field-title').val().trim(),
            application: $('#cc-field-application').val(),
            html_content: $('#cc-field-html').val()
        };
        if (!payload.title || !payload.html_content) {
            logToStream("Validation blocked: Title and HTML fields are required.", true);
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

    $('#cc-delete-btn').on('click', function() {
        if (!activeAssetId || !confirm("Execute database mutation statement? This permanently prunes this static text asset configuration.")) return;
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

    $('#cc-clear-btn').on('click', clearWorkspaceForm);
    $('#cc-new-page-btn').on('click', clearWorkspaceForm);
    $('input[name="cc-app-filter"]').on('change', fetchInventory);

    fetchInventory();
}
// ======================================================================
// END: CONTENT_PANEL_ORCHESTRATOR_LOGIC
// ======================================================================
