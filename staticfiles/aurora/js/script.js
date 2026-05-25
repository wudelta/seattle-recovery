document.addEventListener("DOMContentLoaded", function () {
    console.log("📡 [FRONTEND] Initializing High-Density Aurora UI event matrix bindings...");

    // --- 1. ELEMENT SELECTION SYSTEM ---
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const responseOutput = document.getElementById("response-output");
    const copyButton = document.getElementById("copy-button");
    const consoleOutputCard = document.getElementById("console-output-card");
    const tokenGauge = document.getElementById("token-gauge");
    const tokenDisplay = document.getElementById("token-count-display");
    const activeBrain = document.getElementById("active-brain");
    const systemStatusText = document.getElementById("system-status");

    // Unified Action Button Control Anchors
    const endSessionBtn = document.getElementById("end-session-btn");
    const sweepMemoryBtn = document.getElementById("sweep-memory-btn");

    // --- 2. THE EMPTY-STATE LAYOUT PROTOCOL ---
    function evaluateEmptyState() {
        if (responseOutput && consoleOutputCard) {
            const rawContent = responseOutput.textContent.trim();
            if (rawContent.length === 0) {
                consoleOutputCard.style.setProperty("display", "none", "important");
            } else {
                consoleOutputCard.style.removeProperty("display");
            }
        }
    }
    evaluateEmptyState();

    // --- 3. DYNAMIC INTERACTIVE PROMPT TRANSMISSION ---
    function sendMessage() {
        if (!userInput || !sendBtn) return;
        const textValue = userInput.value.trim();
        if (!textValue) return;

        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrftoken = csrfInput ? csrfInput.value : "";
        const endpointInput = document.getElementById("aurora-chat-endpoint");
        const fetchUrl = endpointInput ? endpointInput.value : "/aurora/api/";

        sendBtn.disabled = true;
        sendBtn.textContent = "...";
        
        if (systemStatusText) {
            systemStatusText.textContent = "Processing Stream...";
            systemStatusText.className = "text-warning font-weight-bold mb-0";
        }

        const formData = new FormData();
        formData.append("text", textValue);

        fetch(fetchUrl, {
            method: "POST",
            credentials: "include", // FIXED: Forces profile cookies to pass to views
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrftoken
            }
        })
        .then(response => {
            if (!response.ok) throw new Error("API Gateway Network Failure Status");
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert("Cognitive Protection Alert: " + data.error);
                return;
            }
            if (consoleOutputCard) {
                consoleOutputCard.style.removeProperty("display");
            }
            if (responseOutput) {
                responseOutput.innerHTML = data.reply || data.system_prompt_envelope || "";
                evaluateEmptyState();
            }
            
            updateSystemGauges(data.tokens_left, data.token_ceiling, data.active_model);
            
            if (systemStatusText) {
                systemStatusText.textContent = "Operational";
                systemStatusText.className = "text-success font-weight-bold mb-0";
            }
            userInput.value = "";
            userInput.style.height = "auto";
        })
        .catch(err => {
            console.error("Critical Stream Anomaly Captured:", err);
            if (systemStatusText) {
                systemStatusText.textContent = "STREAM ERROR";
                systemStatusText.className = "text-danger font-weight-bold mb-0";
            }
            alert("Connection interrupted. Systems attempting automated link refresh.");
        })
        .finally(() => {
            sendBtn.disabled = false;
            sendBtn.innerHTML = "SEND";
        });
    }

    // --- 4. AUTOMATED CONTINUOUS MEMORY CLEANUP PIPELINE ---
    async function triggerWorkspaceMemorySweep() {
        console.log("🧹 [FRONTEND CONTROL] Dispatching manual micro-cleanup context signal...");
        if (!systemStatusText || !responseOutput) return;

        systemStatusText.textContent = "Sweeping RAM...";
        systemStatusText.className = "text-warning font-weight-bold mb-0";
        responseOutput.textContent = "⏳ Micro-sweeper scraping active graph memory strings. Resetting token allocations...";

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const response = await fetch('/aurora/micro-cleanup/', {
                method: 'POST',
                credentials: 'include', // FIXED: Includes login profile matrices
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });

            if (!response.ok) throw new Error(`Memory sweep network channel rejected transaction with status: ${response.status}`);
            
            const data = await response.json();
            console.log("✅ [FRONTEND] Micro-cleanup confirmation package received from backend.");

            if (data.success) {
                responseOutput.textContent = `🧹 [SYSTEM WORKSPACE GRAPH SWEPT & FLUSHED]\n\nRaw chat records have been compiled into a high-density milestone log chunk and committed down to persistent PostgreSQL tables.\n\nLatest Index Core Summary:\n${data.summary_snapshot}`;
                evaluateEmptyState();
                
                // Flush gauge meters down to baseline reset states
                updateSystemGauges(hardTokenCeiling - 1500, hardTokenCeiling, "Architect (70B)");
                
                systemStatusText.textContent = "Operational";
                systemStatusText.className = "text-success font-weight-bold mb-0";
            } else {
                throw new Error(data.error || "Unknown backend operational variance.");
            }
        } catch (error) {
            console.error("❌ [FRONTEND CRASH] Context sweeper execution failed: ", error);
            responseOutput.textContent = `💥 [INTERFACE FAULT] Micro-cleanup transaction collapsed:\n${error.message}`;
            systemStatusText.textContent = "SWEEP ERROR";
            systemStatusText.className = "text-danger font-weight-bold mb-0";
        }
    }

    // --- 5. AUTOMATIC MORNING PROTOCOL INITIALIZATION ROUTINE ---
    async function executeMorningHandshakeSequence() {
        const startEndpointInput = document.getElementById('aurora-start-session-endpoint');
        if (!startEndpointInput || !systemStatusText || !responseOutput) return;

        console.log("🚀 [FRONTEND] Page load complete. Dispatching automatic morning handshake sequence...");
        
        systemStatusText.textContent = "Spinning Up...";
        systemStatusText.className = "text-warning font-weight-bold mb-0";
        responseOutput.textContent = "⏳ Initializing Project Aurora Session... Processing daily brief and fetching 5-day context histories...";
        if (consoleOutputCard) consoleOutputCard.style.removeProperty("display");

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await fetch(startEndpointInput.value, {
                method: 'POST',
                credentials: 'include', // FIXED: Pass cookies to bypass Stage 0
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ 'brief_content': 'Initialize standard development session boundaries.' })
            });

            if (!response.ok) throw new Error(`Handshake transaction denied with status: ${response.status}`);
            
            const data = await response.json();
            console.log("✅ [FRONTEND] Morning handshake complete. System Prompt Envelope prepared.");

            responseOutput.textContent = data.system_prompt_envelope;
            evaluateEmptyState();
            
            systemStatusText.textContent = "Operational";
            systemStatusText.className = "text-success font-weight-bold mb-0";
            
            updateSystemGauges(hardTokenCeiling - 2500, hardTokenCeiling, "Architect (70B)");

        } catch (error) {
            console.error("❌ [FRONTEND CRASH] Morning handshake pipeline failed: ", error);
            responseOutput.textContent = `💥 [STARTUP FAULT] Failed to initialize morning context boundaries:\n${error.message}`;
            systemStatusText.textContent = "STARTUP FAULT";
            systemStatusText.className = "text-danger font-weight-bold mb-0";
            evaluateEmptyState();
        }
    }

    // --- 6. REAL-TIME SYSTEM GAUGES SYNC ---
    const hardTokenCeiling = 14400;
    function updateSystemGauges(tokensLeft, tokenCeiling, activeModel) {
        const ceiling = tokenCeiling || hardTokenCeiling;
        
        if (activeBrain && activeModel) {
            activeBrain.textContent = activeModel;
        }
        if (tokensLeft !== undefined) {
            if (tokenDisplay) {
                tokenDisplay.textContent = `${Number(tokensLeft).toLocaleString()} / ${Number(ceiling).toLocaleString()}`;
            }
            if (tokenGauge) {
                const percentage = Math.max(0, Math.min(100, (tokensLeft / ceiling) * 100));
                tokenGauge.style.width = `${percentage}%`;
                if (percentage < 25) {
                    tokenGauge.className = "progress-bar bg-danger";
                } else if (percentage < 60) {
