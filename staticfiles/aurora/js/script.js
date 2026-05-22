document.addEventListener("DOMContentLoaded", function() {

    // CSRF Utility Extraction Function
    function getCsrfCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const btnExec = document.getElementById("brief-btn-execute");
    if (btnExec) {
        btnExec.addEventListener("click", function() {
            btnExec.disabled = true;
            btnExec.textContent = "CRUNCHING OBJECTIVES VIA LOCAL 8B ARRAY...";
            
            const txtArea = document.getElementById("brief-editor-textarea");
            const payload = new FormData();
            payload.append('brief_content', txtArea ? txtArea.value : "");

            fetch('/aurora/api/session/start/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfCookie('csrftoken') },
                body: payload
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    clearInterval(intervalTimer);
                    
                    // Unlock original status sidebar values securely
                    const statusField = document.getElementById('system-status');
                    if (statusField) {
                        statusField.textContent = "ONLINE // READY";
                        statusField.className = "status-active";
                    }

                    if (fallbackPane) {
                        fallbackPane.textContent = 
                            `[8B TRANSLATOR ABSTRACT MATRIX STAMPED IN POSTGRES]:\n${data.dense_abstract}\n\n` +
                            `[ORCHESTRATOR ENGINE]: Llama 3.3 70B (Wu) awakened successfully.\n` +
                            `Ready to address your morning briefing goals. Transmit directives when prepared.`;
                    }

                    // Remove overlay modal out of screen view space entirely
                    overlay.remove();
                } else {
                    alert(`Initialization Aborted: ${data.error}`);
                    btnExec.disabled = false;
                    btnExec.textContent = "START ONLINE SESSION (AWAKEN WU)";
                }
            })
            .catch(err => {
                alert(`Gateway Connection Failure: ${err}`);
                btnExec.disabled = false;
                btnExec.textContent = "START ONLINE SESSION (AWAKEN WU)";
            });
        });
    }

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
            if (!response.ok) throw new Error('SERVER_ERROR');
            const data = await response.json();
            
            if (data.reply) appendMessage('Wu', data.reply);

            if (data.tokens_left !== undefined && tokenCount && tokenGauge) {
                const remaining = parseInt(data.tokens_left);
                const maxFuel = parseInt(data.token_ceiling) || 18000;
                const percent = Math.max(0, Math.min(100, (remaining / maxFuel) * 100));
                tokenCount.innerText = `${remaining.toLocaleString()} / ${maxFuel.toLocaleString()}`;
                tokenGauge.style.width = percent + '%';
                
                if (modelDisplay && data.active_model) modelDisplay.innerText = data.active_model;

                if (percent < 20) {
                    tokenGauge.style.background = '#ef4444';
                    if (modelDisplay) modelDisplay.style.color = '#ef4444';
                } else if (percent < 50) {
                    tokenGauge.style.background = '#f59e0b';
                    if (modelDisplay) modelDisplay.style.color = '#f59e0b';
                } else {
                    tokenGauge.style.background = '#10b981';
                    if (modelDisplay) modelDisplay.style.color = '#10b981';
                }
            }
        } catch (e) {
            console.error("Caught JS Execution Anomaly Profile:", e);
            appendMessage('Wu', `<span style="color: #ef4444; font-family: monospace; font-weight: bold;">🔴 CIRCUIT BREAKER: Connection to Django Brain severed.</span>`);
        }
    }

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
            endBtn.disabled = true;
            endBtn.innerText = "🧹 Sweeping...";
            endBtn.style.background = "#475569";

            try {
                const response = await fetch('/aurora/end_session/', {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                if (!response.ok) throw new Error(`Server status anomaly: ${response.status}`);
                const data = await response.json();
                if (data.status === 'success') {
                    const mins = typeof data.duration === 'number' ? Math.round(data.duration / 60) : 0;
                    const statsDisplay = document.getElementById('session-stats');
                    if (statsDisplay) statsDisplay.innerText = `● Session Cleared: ${mins} mins`;
                    endBtn.innerText = "✅ Swept";

                    appendMessage('Wu', `
                        <div style="border-left: 3px solid #10b981; padding-left: 10px; color: #10b981; font-weight: bold; font-family: monospace; margin-bottom: 8px;">🧼 JANITOR CLEAN SWEEP COMPLETE</div>
                        <p><em>Session data saved to disk. Duration: <strong>${mins} minutes</strong>.</em></p>
                        <div style="background: #1e293b; padding: 12px; border-radius: 4px; border: 1px solid #334155; margin-top: 10px;">
                            <strong style="color: #38bdf8; font-family: monospace;">[PROJECT_STATE.md SNAPSHOT]</strong>
                            <p style="margin: 5px 0 0 0; line-height: 1.5; font-size: 13px; color: #cbd5e1;">${data.summary}</p>
                        </div>
                    `);
                } else {
                    alert(`Teardown message: ${data.message || 'Unknown processing halt'}`);
                    endBtn.disabled = false;
                    endBtn.innerText = "🛑 Close Session";
                    endBtn.style.background = "#dc2626";
                }
            } catch (error) {
                console.error("Session teardown error:", error);
                window.location.href = '/aurora/end_session/';
            }
        });
    }

    // ============================================================================
    // 7. MANUAL LOGGING CONTROLS
    // ============================================================================
    if (manualHoursField && manualNoteField) {
        const logManualTimeBtn = document.querySelector('button[onclick="logManualTime()"]');
        if (logManualTimeBtn) {
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
                    if (data.status === 'success') { alert(data.message); location.reload(); }
                } catch (error) { console.error("Manual log anomaly:", error); }
            });
        }
    }
});
