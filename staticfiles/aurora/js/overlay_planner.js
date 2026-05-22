/**
 * Project Aurora - Step 1: Pre-Session Planning Module (Live-Scraper Edition)
 */
document.addEventListener("DOMContentLoaded", function() {
    console.log("[Aurora Debug] Initializing safe event hook loop...");

    setTimeout(() => {
        const buttons = document.querySelectorAll('.brief-btn-go');
        if (buttons.length > 0) {
            const saveBtn = buttons[0]; // Isolate the first button (Reload Disk)

            // Force unlock styling and constraints
            saveBtn.disabled = false;
            saveBtn.removeAttribute('disabled');
            saveBtn.style.background = "#10b981"; 
            saveBtn.style.color = "#ffffff";
            saveBtn.style.cursor = "pointer";
            saveBtn.textContent = "SAVE & RELOAD DISK";
            saveBtn.onclick = null; 
            saveBtn.addEventListener("click", function(e) {
                e.preventDefault();
                e.stopPropagation();

                // DYNAMIC SCRAPE: Find ALL textareas on screen at the exact second of the click
                const allTextAreas = document.querySelectorAll('textarea');
                let textToSend = "";

                console.log("[Aurora Debug] Click triggered. Found textareas on screen:", allTextAreas.length);

                // Loop through all text boxes to find the one containing the user's edits
                allTextAreas.forEach((box, index) => {
                    console.log(`[Aurora Debug] Textbox [${index}] length: ${box.value.length}, value snippet: "${box.value.substring(0, 15)}"`);
                    if (box.value && box.value.length > textToSend.length) {
                        textToSend = box.value; // Prioritize the text area that has active data
                    }
                });

                // If everything is completely empty, use whatever text is in the main layout box
                if (!textToSend && allTextAreas.length > 0) {
                    textToSend = allTextAreas[0].value;
                }

                saveBtn.disabled = true;
                saveBtn.textContent = "SAVING TO DISK...";

                fetch('/aurora/save_brief/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ brief_text: textToSend })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.location.href = window.location.pathname + '?v=' + new Date().getTime();
                    } else {
                        alert("Disk Save Failed: " + data.message);
                        saveBtn.disabled = false;
                        saveBtn.textContent = "SAVE & RELOAD DISK";
                    }
                })
                .catch(err => {
                    alert("Backend network communication error.");
                    saveBtn.disabled = false;
                    saveBtn.textContent = "SAVE & RELOAD DISK";
                });
            });
        }
    }, 500);
});
