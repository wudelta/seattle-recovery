// ====================================================================== 
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 1 OF 3) 
// START: INITIALIZATION_CLOSURE_AND_STATE_ENCLOSURE 
// ====================================================================== 
function initDeltaNotesConsole(endpoints, csrfToken) {
    // ENCLOSED STATE: Accessible to all nested timer and click loop blocks
    let activeTimerInterval = null;
    let activeSecondsCount = 0;
    let isSessionTracking = false;

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

    function formatTime(totalSeconds) {
        let hrs = Math.floor(totalSeconds / 3600);
        let mins = Math.floor((totalSeconds % 3600) / 60);
        let secs = totalSeconds % 60;
        return String(hrs).padStart(2, '0') + ':' + String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
    }
// ====================================================================== 
// END: INITIALIZATION_CLOSURE_AND_STATE_ENCLOSURE 
// ====================================================================== 

// ====================================================================== 
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 2 OF 3) 
// START: ENCLOSED_TIMER_CORE_OPERATIONS 
// ====================================================================== 
    function startGlobalTimer() {
        if (!activeTimerInterval) {
            activeTimerInterval = setInterval(function() {
                activeSecondsCount++;
                $('#session-timer-display').text(formatTime(activeSecondsCount));
            }, 1000);
        }
    }

    function stopGlobalTimer(callback) {
        if (!activeTimerInterval) {
            if (callback) callback();
            return;
        }
        clearInterval(activeTimerInterval);
        activeTimerInterval = null;

        // Commit tracking parameters right up to the latest open Postgres item 
        $.post(endpoints.endpoint_url, { 
            action: 'sync_timer', 
            current_duration: activeSecondsCount, 
            csrfmiddlewaretoken: csrfToken 
        }, function(data) {
            if (callback) callback();
        }).fail(function(xhr) {
            console.error("Session sync failure: ", xhr.responseText);
            if (callback) callback();
        });
    }
// ====================================================================== 
// END: ENCLOSED_TIMER_CORE_OPERATIONS 
// ====================================================================== 

// ====================================================================== 
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 3 OF 3) 
// START: STRIPPED_EVENT_BINDINGS_AND_FLOW_CONTROL 
// ====================================================================== 
    // Toggle dashboard session focus states via strict dynamic document delegation 
    $(document).off('click', '#global-timer-toggle-btn').on('click', '#global-timer-toggle-btn', function() {
        const btn = $(this);
        if (!isSessionTracking) {
            isSessionTracking = true;
            btn.removeClass('btn-outline-success').addClass('btn-danger').text('Pause Session');
            startGlobalTimer();
        } else {
            isSessionTracking = false;
            btn.removeClass('btn-danger').addClass('btn-outline-success').text('Start Session');
            stopGlobalTimer();
        }
    });

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

    // Compile markdown loop (Decoupled: Only refreshes project file context)
    $(document).off('click', '#compile-blueprint-btn').on('click', '#compile-blueprint-btn', function() {
        const btn = $(this);
        btn.prop('disabled', true).text('Writing File...');
        
        $.post(endpoints.endpoint_url, { 
            action: 'compile_blueprint', 
            csrfmiddlewaretoken: csrfToken 
        }, function(data) {
            alert(data.message);
            btn.prop('disabled', false).text('Compile to project.md');
            loadActiveQueue();
        }).fail(function(xhr) {
            alert("Compilation failed: " + xhr.responseText);
            btn.prop('disabled', false).text('Compile to project.md');
        });
    });

    // Initial console populate execution pass 
    loadActiveQueue();
}
// ====================================================================== 
// END: STRIPPED_EVENT_BINDINGS_AND_FLOW_CONTROL 
// ====================================================================== 
