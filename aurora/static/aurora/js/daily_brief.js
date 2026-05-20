// Store the exact initial payload text state loaded from your server disk layout
const originalTextContent = document.getElementById('brief-text').value;

function checkTextState() {
    const currentTextContent = document.getElementById('brief-text').value;
    const saveButton = document.getElementById('save-btn');
    const exitButton = document.getElementById('exit-btn');

    if (currentTextContent !== originalTextContent) {
        saveButton.disabled = false; 
        exitButton.classList.add('disabled'); 
    } else {
        saveButton.disabled = true; 
        exitButton.classList.remove('disabled'); 
    }
}

function copyPromptToClipboard() {
    const textContent = document.getElementById('brief-text').value;
    if (textContent) {
        navigator.clipboard.writeText(textContent);
        alert("Prompt payload copied! Ready to feed to Wu.");
    }
}

// --- ACTIVE-ONLY SESSION TIME ACCUMULATOR TRACKING ENGINE ---
let totalSeconds = 0;

function updateSessionClock() {
    // Only accumulate seconds if the browser tab is actively in focus
    if (document.visibilityState === 'visible') {
        totalSeconds++;
        
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        const pad = (num) => String(num).padStart(2, '0');
        
        const timeString = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
        document.getElementById('session-timer').textContent = `TIME: ${timeString}`;
    }
}

// Tick every second offline
setInterval(updateSessionClock, 1000);
