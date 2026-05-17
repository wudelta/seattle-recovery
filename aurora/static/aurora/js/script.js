// FILE: aurora/script.js
/*
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:45.400759+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/static/aurora/js/script.js
 TECHNICAL MATRIX: Javascript Client Architecture Asset.

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[script.js] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
*/
// ============================================================================
// 1. DOM ELEMENT BINDINGS & HANDSHAKES
// ============================================================================
const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const tokenGauge = document.getElementById('token-gauge');
const tokenCount = document.getElementById('token-count-display');
const modelDisplay = document.getElementById('active-brain'); 
const endBtn = document.getElementById('end-session-btn');
const manualHoursField = document.getElementById('manual-hours');
const manualNoteField = document.getElementById('manual-note');
const copyButton = document.getElementById('copy-button');

// ============================================================================
// 2. AUTO-GROW TEXTAREA LOGIC
// ============================================================================
if (userInput) {
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
}

// ============================================================================
// 3. CHAT CANVAS RENDERING MATRIX
// ============================================================================
function appendMessage(role, htmlContent) {
    if (!chatWindow) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = 'message';
    const color = (role === 'Delta') ? '#0284c7' : '#334155';
    const char = (role === 'Delta') ? 'D' : 'W';

    msgDiv.innerHTML = `
        <div class="avatar" style="background: ${color}">${char}</div>
        <div class="bubble">
            <p style="font-size: 10px; color: #64748b; margin: 0 0 5px 0; text-transform: uppercase; font-family: monospace;">${role}</p>
            <div class="rich-text">${htmlContent}</div>
        </div>
    `;

    chatWindow.appendChild(msgDiv);

    // Core Code Clipboard Injection Handler Logic
    msgDiv.querySelectorAll('pre').forEach((block) => {
        const btn = document.createElement('button');
        btn.innerText = 'Copy';
        btn.className = 'copy-btn';
        btn.onclick = () => {
            const codeText = block.innerText.replace('Copy', '').trim();
            navigator.clipboard.writeText(codeText).then(() => {
                btn.innerText = 'Copied!';
                setTimeout(() => btn.innerText = 'Copy', 2000);
            });
        };
        block.appendChild(btn);
    });

    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ============================================================================
// 4. ASYNCHRONOUS GRAPH BRAIN COMMUNICATIONS LAYER
// ============================================================================
async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage('Delta', text);
    userInput.value = '';
    userInput.style.height = 'auto';

    const formData = new FormData();
    formData.append('text', text);

    try {
        const response = await fetch('/aurora/api/', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            console.error("Server returned an invalid operational response header status:", response.status);
            throw new Error('SERVER_ERROR');
        }

        const data = await response.json();

        // Render Response Object Canvas Target View
        if (data.reply) {
            appendMessage('Wu', data.reply);
        }

        // Real-Time Quota Metrics HUD Re-calibration loop
        if (data.tokens_left !== undefined && tokenCount && tokenGauge) {
            const remaining = parseInt(data.tokens_left);
            const maxFuel = parseInt(data.token_ceiling) || 18000; 
            const percent = Math.max(0, Math.min(100, (remaining / maxFuel) * 100));

            tokenCount.innerText = `${remaining.toLocaleString()} / ${maxFuel.toLocaleString()}`;
            tokenGauge.style.width = percent + '%';

            if (modelDisplay && data.active_model) {
                modelDisplay.innerText = data.active_model;
            }

            // Color Shift Status Transitions Threshold Controls
            if (percent < 20) {
                tokenGauge.style.background = '#ef4444'; // Alarm State Red
                if (modelDisplay) modelDisplay.style.color = '#ef4444';
            } else if (percent < 50) {
                tokenGauge.style.background = '#f59e0b'; // Warn State Orange
                if (modelDisplay) modelDisplay.style.color = '#f59e0b';
            } else {
                tokenGauge.style.background = '#10b981'; // Operating Stable Emerald Green
                if (modelDisplay) modelDisplay.style.color = '#10b981';
            }
        }
    } catch (e) {
        console.error("Caught JS Execution Anomaly Profile:", e);
        appendMessage('Wu', `<span style="color: #ef4444; font-family: monospace; font-weight: bold;">🔴 CIRCUIT BREAKER: Connection to Django Brain severed. Fire up lifeboat terminal environment immediately.</span>`);
    }
}

// ============================================================================
// 5. ATTACH INTERFACE EVENT LISTENERS
// ============================================================================
if (sendBtn) sendBtn.addEventListener('click', handleSend);
if (userInput) {
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
}

// ============================================================================
// 6. DUAL-WRITE SESSION TEARDOWN CONTROLS
// ============================================================================
if (endBtn) {
    endBtn.addEventListener('click', async () => {
        if (!confirm("Close current session and execute Janitor Clean Sweep?")) return;
        
        // Prevent double submissions and give visual feedback
        endBtn.disabled = true;
        endBtn.innerText = "🧹 Sweeping...";
        endBtn.style.background = "#475569";

        try {
            // Note: Changed endpoint path to point directly to your views.py mapping
            const response = await fetch('/aurora/end_session/', { 
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Server status anomaly: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                const mins = typeof data.duration === 'number' ? Math.round(data.duration / 60) : 0;
                
                // Update your session HUD dashboard metric indicator if it exists
                const statsDisplay = document.getElementById('session-stats');
                if (statsDisplay) {
                    statsDisplay.innerText = `● Session Cleared: ${mins} mins`;
                }
                
                endBtn.innerText = "✅ Swept";
                
                // Print the Janitor's technical markdown summary straight into the chat view
                appendMessage('Wu', `
                    <div style="border-left: 3px solid #10b981; padding-left: 10px; color: #10b981; font-weight: bold; font-family: monospace; margin-bottom: 8px;">
                        🧼 JANITOR CLEAN SWEEP COMPLETE
                    </div>
                    <p><em>Session data saved to disk and cleared from active graph memory. Duration: <strong>${mins} minutes</strong>.</em></p>
                    <div style="background: #1e293b; padding: 12px; border-radius: 4px; border: 1px solid #334155; margin-top: 10px;">
                        <strong style="color: #38bdf8; font-family: monospace;">[PROJECT_STATE.md SNAPSHOT]</strong>
                        <p style="margin: 5px 0 0 0; line-height: 1.5; font-size: 13px; color: #cbd5e1;">${data.summary}</p>
                    </div>
                `);
            } else {
                alert(`Teardown execution message: ${data.message || 'Unknown processing halt'}`);
                endBtn.disabled = false;
                endBtn.innerText = "🛑 Close Session";
                endBtn.style.background = "#dc2626";
            }
        } catch (error) {
            console.error("Session teardown transmission error caught:", error);
            alert("Teardown link failed. Bypassing UI to attempt raw endpoint release...");
            
            // Emergency fallback: If AJAX fails, load the endpoint directly in your browser tab
            window.location.href = '/aurora/end_session/';
        }
    });
}

// ============================================================================
// 7. MANUAL LOGGING CONTROLS
// ============================================================================
if (manualHoursField && manualNoteField) {
    const logManualTimeBtn = document.querySelector('button[onclick="logManualTime()"]');
    logManualTimeBtn.addEventListener('click', async () => {
        const hours = manualHoursField.value;
        const note = manualNoteField.value;
        if (!hours) return alert("Enter hours first.");

        const formData = new FormData();
        formData.append('hours', hours);
        formData.append('note', note);

        try {
            const response = await fetch('/aurora/manual_log/', { method: 'POST', body: formData });
            const data = await response.json();

            if (data.status === 'success') {
                alert(data.message);
                location.reload();
            }
        } catch (error) {
            console.error("Manual ledger synchronization anomaly tracked:", error);
        }
    });
}

// ============================================================================
// 8. COPY BUTTON CONTROLS
// ============================================================================
if (copyButton) {
    copyButton.addEventListener('click', () => {
        const codeText = chatWindow.innerText;
        navigator.clipboard.writeText(codeText).then(() => {
            copyButton.innerText = 'Copied!';
            setTimeout(() => copyButton.innerText = 'Copy', 2000);
        });
    });
}