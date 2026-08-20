// ======================================================================
// FILE: aurora/static/aurora/js/delta_notes/delta_notes.js
// START: INITIALIZATION_CLOSURE_AND_STATE_ENCLOSURE
// ======================================================================
function initDeltaNotesConsole(endpoints, csrfToken) {
    
    // Bind endpoints globally so console.js can synchronize session timers
    window.auroraDeltaEndpoints = endpoints;

    function loadActiveQueue() {
        $.get(endpoints.endpoint_url, function(data) {
            if (data.status === "success") {
                renderQueues(data.unprocessed, data.processed);
            }
        });
    }

    function renderQueues(unprocessed, processed) {
        const unparsedContainer = $('#notes-container');
        const parsedContainer = $('#processed-notes-container');
        unparsedContainer.empty();
        parsedContainer.empty();
        $('#queue-count').text(unprocessed.length);
        $('#processed-count').text(processed.length);

        // Render UNPROCESSED_LOG Block Elements
        if (unprocessed.length === 0) {
            unparsedContainer.append('<div class="text-center text-muted p-3 small">[ Queue clean. No active intentions. ]</div>');
        } else {
            unprocessed.forEach(function(note) {
                const itemHtml = `
                <div class="list-group-item note-row text-white d-flex justify-content-between align-items-center p-2 border-secondary bg-transparent" data-id="${note.id}">
                    <div class="d-flex align-items-center flex-grow-1 me-2">
                        <span class="text-warning me-2">></span>
                        <div class="text-wrap small note-display-text" id="note-text-display-${note.id}">${note.text}</div>
                    </div>
                    <div class="btn-group shadow-sm flex-shrink-0">
                        <button class="btn btn-outline-success btn-xs px-1 py-0 complete-note-btn" data-id="${note.id}" title="Mark Processed" style="font-size: 0.7rem;">✓</button>
                        <button class="btn btn-outline-warning btn-xs px-1 py-0 edit-note-btn" data-id="${note.id}" style="font-size: 0.7rem;">Edit</button>
                        <button class="btn btn-outline-danger btn-xs px-1 py-0 delete-note-btn" data-id="${note.id}" style="font-size: 0.7rem;">Del</button>
                    </div>
                </div>`;
                unparsedContainer.append(itemHtml);
            });
        }

        // Render PROCESSED_LOG Block Elements
        if (processed.length === 0) {
            parsedContainer.append('<div class="text-center text-muted p-3 small">[ No directives processed this session. ]</div>');
        } else {
            processed.forEach(function(note) {
                const itemHtml = `
                <div class="list-group-item note-row text-muted d-flex justify-content-between align-items-center p-2 border-secondary bg-transparent" style="opacity: 0.75;">
                    <div class="d-flex align-items-center">
                        <span class="text-secondary me-2">✓</span>
                        <div class="text-wrap small text-decoration-line-through">${note.text}</div>
                    </div>
                </div>`;
                parsedContainer.append(itemHtml);
            });
        }
    }
// ======================================================================
// END: INITIALIZATION_CLOSURE_AND_STATE_ENCLOSURE (PATCH 1 OF 2)
// ======================================================================

// ====================================================================== 
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 2 OF 2)
// START: STRIPPED_EVENT_BINDINGS_AND_FLOW_CONTROL
// ====================================================================== 
    // Capture text intention additions
    $(document).off('submit', '#create-note-form').on('submit', '#create-note-form', function(e) {
        e.preventDefault();
        const textInput = $('#note-text');
        $.post(endpoints.endpoint_url, { 
            action: 'create_note', 
            text: textInput.val(), 
            csrfmiddlewaretoken: csrfToken 
        }, function(data) {
            if (data.status === "success") {
                textInput.val('');
                loadActiveQueue();
            }
        });
    });

    // Dynamic Row Action: Inline Mark Processed Handler
    $('#notes-container').off('click', '.complete-note-btn').on('click', '.complete-note-btn', function(e) {
        e.preventDefault();
        const noteId = $(this).attr('data-id') || $(this).data('id');
        $.post(endpoints.endpoint_url, { 
            action: 'process_note', 
            note_id: noteId, 
            csrfmiddlewaretoken: csrfToken 
        }, function(data) {
            if (data.status === "success") {
                loadActiveQueue();
            }
        });
    });

    // Dynamic Row Action Click Delegators: Inline Edit Handlers
    $('#notes-container').off('click', '.edit-note-btn').on('click', '.edit-note-btn', function(e) {
        e.preventDefault();
        const noteId = $(this).attr('data-id') || $(this).data('id');
        const displayDiv = $(`#note-text-display-${noteId}`);
        const currentVal = displayDiv.text().trim();
        const updatedVal = prompt("Modify target intention parameter configurations:", currentVal);
        if (updatedVal !== null && updatedVal.trim() !== "" && updatedVal.trim() !== currentVal) {
            $.post(endpoints.endpoint_url, { 
                action: 'edit_note', 
                note_id: noteId, 
                text: updatedVal.trim(), 
                csrfmiddlewaretoken: csrfToken 
            }, function(data) {
                loadActiveQueue();
            });
        }
    });

    // Dynamic Row Action Click Delegators: Inline Delete Handlers
    $('#notes-container').off('click', '.delete-note-btn').on('click', '.delete-note-btn', function(e) {
        e.preventDefault();
        const noteId = $(this).attr('data-id') || $(this).data('id');
        if (confirm("Surgically isolate and erase this active log entry?")) {
            $.post(endpoints.endpoint_url, { 
                action: 'delete_note', 
                note_id: noteId, 
                csrfmiddlewaretoken: csrfToken 
            }, function(data) {
                loadActiveQueue();
            });
        }
    });

    // Cross-subsystem synchronization:
    // another workflow changed Delta Notes persistence.
    $(document)
        .off('aurora:delta_notes_changed.delta_notes')
        .on(
            'aurora:delta_notes_changed.delta_notes',
            function() {
                loadActiveQueue();
            }
        );
        
    // Initial console populate execution pass
    loadActiveQueue();
}
// ====================================================================== 
// END: STRIPPED_EVENT_BINDINGS_AND_FLOW_CONTROL
// ======================================================================
