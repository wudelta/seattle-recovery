// ======================================================================
// FILE: aurora/static/aurora/js/delta_directives/directives.js
// START: DIRECTIVES_READ_ONLY_INSPECTION
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
        const rawLine = `[${timestamp}] ${indicator} ${text}\n`;
        const $stream = $('#dc-terminal-stream');

        $stream.prepend(
            $('<span>')
                .addClass(colorClass)
                .text(rawLine)
        );

        if ($stream.length) {
            $stream.scrollTop(0);
        }
    }

    function fetchInventory() {
        const currentScope =
            $('input[name="dc-status-filter"]:checked').val();

        $.ajax({
            url: apiURL,
            type: 'GET',
            data: {
                status: currentScope
            },

            success: function(response) {
                if (response.status !== 'SUCCESS') return;

                const $list = $('#dc-inventory-list').empty();

                if (!response.inventory.length) {
                    $list.append(
                        '<div class="text-muted text-center p-3 small italic">' +
                        'No directives found.' +
                        '</div>'
                    );
                    return;
                }

                response.inventory.forEach(function(item) {
                    const labelState =
                        item.is_active ? 'success' : 'secondary';
                    const badgeText =
                        item.is_active ? 'ACTIVE' : 'INACTIVE';

                    const $row = $(`
                        <div
                            class="d-flex align-items-center justify-content-between p-1 rounded border border-dark bg-black text-light"
                            style="cursor:pointer;"
                            data-id="${item.id}"
                        >
                            <div class="text-truncate flex-grow-1 me-1">
                                <span
                                    class="badge bg-opacity-25 bg-${labelState} text-${labelState} font-monospace me-1"
                                    style="font-size:0.65rem;"
                                >
                                    ${badgeText}
                                </span>
                                <span class="font-monospace small">
                                    ${item.directive_name}
                                </span>
                            </div>
                            <span
                                class="text-muted"
                                style="font-size:0.7rem; font-style:italic;"
                            >
                                ${item.date_modified}
                            </span>
                        </div>
                    `);

                    if (activeAssetId === item.id) {
                        $row
                            .addClass('border-warning')
                            .css('background-color', '#1b1b1b');
                    }

                    $list.append($row);
                });
            },

            error: function(xhr) {
                logToStream(
                    `Inventory registry retrieval fault: ${xhr.status}`,
                    true
                );
            }
        });
    }

    $(document).on(
        'click',
        '#dc-inventory-list [data-id]',
        function() {
            const targetId = $(this).data('id');

            $.ajax({
                url: apiURL,
                type: 'GET',
                data: {
                    id: targetId
                },

                success: function(response) {
                    if (response.status !== 'SUCCESS') return;

                    const asset = response.asset;

                    activeAssetId = asset.id;

                    $('#dc-field-name').val(asset.directive_name);
                    $('#dc-field-active').val(
                        asset.is_active ? 'ACTIVE' : 'INACTIVE'
                    );
                    $('#dc-field-constraints').val(
                        JSON.stringify(asset.constraints, null, 2)
                    );

                    // Instructions are canonical text. Never interpret the
                    // persisted value as HTML during inspection.
                    $('#dc-rich-editor').val(asset.instructions);

                    $('#dc-active-asset-indicator')
                        .text(`📑 DIRECTIVE LOADED: ${asset.directive_name}`);

                    logToStream(
                        `Loaded directive "${asset.directive_name}" ` +
                        `[Author: ${asset.author}].`
                    );

                    fetchInventory();
                },

                error: function() {
                    logToStream(
                        'Directive inspection request rejected.',
                        true
                    );
                }
            });
        }
    );

    $('input[name="dc-status-filter"]').on(
        'change',
        fetchInventory
    );

    fetchInventory();
}
// ======================================================================
// FILE: aurora/static/aurora/js/delta_directives/directives.js
// END: DIRECTIVES_READ_ONLY_INSPECTION
// ======================================================================