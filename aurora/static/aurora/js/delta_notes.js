document.addEventListener("DOMContentLoaded", function () {
    console.log("📝 [NOTES WORKSPACE] Initializing offline entry transaction loops...");

    // Core Document Element Anchors
    const saveNoteBtn = document.getElementById("save-note-btn");
    const offlineNoteText = document.getElementById("offline-note-text");
    const saveStatusText = document.getElementById("save-status-text");
    const timelineContainer = document.getElementById("notes-timeline-container");

    /**
     * Submits the plain-English text down to the headless PostgreSQL entry API
     */
    async function commitDeltaJournalEntry() {
        const textValue = offlineNoteText.value.trim();
        if (!textValue) {
            alert("Journal entry content cannot be completely empty.");
            return;
        }

        // Establish immediate loading view parameters
        saveNoteBtn.disabled = true;
        saveNoteBtn.textContent = "Committing...";
        if (saveStatusText) saveStatusText.textContent = "⏳ Accessing PostgreSQL relational layers...";

        try {
            // Recover standard Django security token string from hidden input fields
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Post directly down to our newly registered notes database endpoint
            const response = await fetch('/aurora/api/notes/create/', {
                method: 'POST',
                credentials: 'include', // Mandate cookie routing to bypass Stage 0 blocks
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ 'raw_text': textValue })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || `Server transaction rejected with status: ${response.status}`);
            }

            console.log(`✅ [FRONTEND] Note logged successfully. ID: ${data.note_id}`);
            if (saveStatusText) saveStatusText.textContent = `膜 Success: Saved row entry ID ${data.note_id}.`;
            
            alert(`Journal entry saved securely as DeltaNote ID ${data.note_id}.`);
            offlineNoteText.value = ""; // Clear form fields natively
            
            // Refresh the placeholder queue container view on screen
            fetchUnprocessedNotesTimeline();

        } catch (error) {
            console.error("❌ [FRONTEND CRASH] Offline entry pass failed: ", error);
            if (saveStatusText) saveStatusText.textContent = "❌ Transaction execution failure.";
            alert(`💥 [INTEGRATION ERROR] Failed to lock note to database: ${error.message}`);
        } finally {
            saveNoteBtn.disabled = false;
            saveNoteBtn.textContent = "Save Note to Postgres";
        }
    }

    /**
     * Placeholder visualization frame to render data states on screen
     */
    function fetchUnprocessedNotesTimeline() {
        if (!timelineContainer) return;
        timelineContainer.innerHTML = `
            <div class="p-2 mb-2 rounded bg-white border border-secondary shadow-sm">
                <small class="text-primary font-weight-bold d-block mb-1">Queue Tracking Active</small>
                <p class="text-dark small mb-0 font-weight-medium">New notes will be captured as UNPROCESSED until your session_start processing minion loop activates.</p>
            </div>
        `;
    }

    // Bind event handlers securely
    if (saveNoteBtn) {
        saveNoteBtn.addEventListener("click", commitDeltaJournalEntry);
    }
    
    // Run an immediate initialization draw pass
    fetchUnprocessedNotesTimeline();
});
