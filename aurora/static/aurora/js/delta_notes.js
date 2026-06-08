// ======================================================================
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 1 OF 5)
// START: GLOBAL_SESSION_TIMER_STATE_CONSTRAINTS
// ======================================================================
// Global environment tracking variables for the single-dashboard cockpit
let activeTimerInterval = null;
let activeSecondsCount = 0;
let isSessionTracking = false;

// Typing Debounce variables to manage automated text-area saving loops
let autoSaveDebounceTimeout = null;
const DEBOUNCE_DELAY_MS = 1000; // Fires auto-save 1 second after typing ceases
// ======================================================================
// END: GLOBAL_SESSION_TIMER_STATE_CONSTRAINTS
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 2 OF 5)
// START: ASYNC_QUEUE_LOAD_AND_HIGH_DENSITY_RENDER
// ======================================================================
function initDeltaNotesConsole(endpoints, csrfToken) {
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
        
        // Render clean, high-density checklist rows with modular inline action buttons
        entries.forEach(function(note) {
            const cardHtml = `
                <div class="list-group-item note-row text-white d-flex justify-content-between align-items-center p-2 border-secondary bg-transparent">
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
// END: ASYNC_QUEUE_LOAD_AND_HIGH_DENSITY_RENDER
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 3 OF 5)
// START: GLOBAL_TIMER_CORE_MANAGEMENT
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
        
        // Commit global focus time directly up to the latest open tracking item
        $.post(endpoints.endpoint_url, {
            action: 'sync_timer',
            current_duration: activeSecondsCount,
            csrfmiddlewaretoken: csrfToken
        }, function(data) {
            if (callback) callback();
        }).fail(function(xhr) {
            console.error("Session sync failed: ", xhr.responseText);
            if (callback) callback();
        });
    }
// ======================================================================
// END: GLOBAL_TIMER_CORE_MANAGEMENT
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 4 OF 5)
// START: FRONTEND_UI_EVENT_BINDINGS
// ======================================================================
    // Toggle dashboard session focus states
    $('#global-timer-toggle-btn').on('click', function() {
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

    // Keystroke Debounce handler to save typing changes on the fly
    $('#note-text').on('input', function() {
        clearTimeout(autoSaveDebounceTimeout);
        const currentText = $(this).val().trim();
        if (!currentText) return;

        autoSaveDebounceTimeout = setTimeout(function() {
            console.log("[Aurora Auto-Save] Typing stabilized. Syncing raw draft state...");
            // Non-blocking auto-save call to ensure progress isn't lost if you change your mind
            $.post(endpoints.endpoint_url, {
                action: 'autosave_draft',
                text: currentText,
                csrfmiddlewaretoken: csrfToken
            });
        }, DEBOUNCE_DELAY_MS);
    });

    // Capture text intention additions
    $('#create-note-form').on('submit', function(e) {
        e.preventDefault();
        clearTimeout(autoSaveDebounceTimeout);
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
    $('#notes-container').on('click', '.edit-note-btn', function() {
        const noteId = $(this).data('id');
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
                if (data.status === "success") {
                    loadActiveQueue();
                }
            });
        }
    });

    // Dynamic Row Action Click Delegators: Inline Delete Handlers
    $('#notes-container').on('click', '.delete-note-btn', function() {
        const noteId = $(this).data('id');
        if (confirm("Surgically isolate and erase this active log entry?")) {
            $.post(endpoints.endpoint_url, {
                action: 'delete_note',
                note_id: noteId,
                csrfmiddlewaretoken: csrfToken
            }, function(data) {
                if (data.status === "success") {
                    loadActiveQueue();
                }
            });
        }
    });
// ======================================================================
// END: FRONTEND_UI_EVENT_BINDINGS
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 5 OF 5)
// START: COMPILATION_AUTOMATION_AND_CLOSURES
// ======================================================================
    // Compile entire backlog down onto project.md
    $('#compile-blueprint-btn').on('click', function() {
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

    // Auto-Pause Protection on Workspace tab switching
    document.addEventListener("visibilitychange", function() {
        if (document.hidden && isSessionTracking) {
            clearInterval(activeTimerInterval);
            activeTimerInterval = null;
            // Background update to safe-store seconds before page suspension
            $.post(endpoints.endpoint_url, {
                action: 'sync_timer',
                current_duration: activeSecondsCount,
                csrfmiddlewaretoken: csrfToken
            });
        } else if (!document.hidden && isSessionTracking) {
            startGlobalTimer();
        }
    });

    // Initial console populate execution pass
    loadActiveQueue();
}
// ======================================================================
// END: COMPILATION_AUTOMATION_AND_CLOSURES
// ======================================================================
