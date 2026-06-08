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
                renderQueue(data.entries);
            }
        });
    }

    function renderQueue(entries) {
        const container = $('#notes-container');
        container.empty();
        $('#queue-count').text(entries.length);
        if (entries.length === 0) {
            container.append('<div class="text-center text-muted p-4 small">[ Queue pristine. No active intentions registered. ]</div>');
            return;
        }
        
        entries.forEach(function(note) {
            const cardHtml = `
                <div class="list-group-item note-row text-white d-flex justify-content-between align-items-center p-2 border-secondary bg-transparent" data-id="${note.id}">
                    <div class="d-flex align-items-center flex-grow-1 me-3">
                        <span class="text-warning me-2">></span>
                        <div class="text-wrap small note-display-text" id="note-text-display-${note.id}">${note.text}</div>
                    </div>
                    <div class="btn-group shadow-sm">
                        <button class="btn btn-outline-warning btn-xs px-2 py-0 edit-note-btn" data-id="${note.id}" style="font-size: 0.75rem;">Edit</button>
                        <button class="btn btn-outline-danger btn-xs px-2 py-0 delete-note-btn" data-id="${note.id}" style="font-size: 0.75rem;">Delete</button>
                    </div>
                </div>
            `;
            container.append(cardHtml);
        });
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

    // Capture text intention additions (Direct submission only - debounce removed)
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

    // Compile entire backlog down onto project.md
    $(document).off('click', '#compile-blueprint-btn').on('click', '#compile-blueprint-btn', function() {
        const btn = $(this);
        btn.prop('disabled', true).text('Syncing Blueprint...');
        
        function executeCompilation() {
            $.post(endpoints.endpoint_url, {
                action: 'compile_blueprint',
                csrfmiddlewaretoken: csrfToken
            }, function(data) {
                alert(data.message);
                btn.prop('disabled', false).text('🚀 Compile to project.md');
                activeSecondsCount = 0;
                $('#session-timer-display').text('00:00:00');
                loadActiveQueue();
            }).fail(function(xhr) {
                alert("Compilation failed: " + xhr.responseText);
                btn.prop('disabled', false).text('🚀 Compile to project.md');
            });
        }

        if (isSessionTracking) {
            isSessionTracking = false;
            $('#global-timer-toggle-btn').removeClass('btn-danger').addClass('btn-outline-success').text('Start Session');
            stopGlobalTimer(executeCompilation);
        } else {
            executeCompilation();
        }
    });

    // Initial console populate execution pass
    loadActiveQueue();
}
// ======================================================================
// END: STRIPPED_EVENT_BINDINGS_AND_FLOW_CONTROL
// ======================================================================
