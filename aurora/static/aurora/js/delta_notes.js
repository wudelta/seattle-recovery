// ======================================================================
// FILE: aurora/static/aurora/js/delta_notes.js (PATCH 1 OF 5)
// START: GLOBAL_SESSION_TIMER_STATE_CONSTRAINTS
// ======================================================================
// Global environment tracking variables for the single-dashboard cockpit
let activeTimerInterval = null;
let activeSecondsCount = 0;
let isSessionTracking = false;
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

        // Render clean, high-density checklist rows with zero row-level button clutter
        entries.forEach(function(note) {
            const cardHtml = `
                <div class="list-group-item note-row text-white d-flex align-items-center">
                    <span class="text-warning me-2">></span>
                    <div class="text-wrap small">${note.text}</div>
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

    // Capture text intention additions
    $('#create-note-form').on('submit', function(e) {
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
