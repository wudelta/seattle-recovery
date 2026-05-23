document.addEventListener("DOMContentLoaded", function () {
    // --- 1. ELEMENT SELECTION SYSTEM ---
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const responseOutput = document.getElementById("response-output");
    const copyButton = document.getElementById("copy-button");
    const consoleOutputCard = document.getElementById("console-output-card");

    // --- 2. THE EMPTY-STATE LAYOUT PROTOCOL ---
    function evaluateEmptyState() {
        if (responseOutput && consoleOutputCard) {
            const rawContent = responseOutput.textContent.trim();
            
            if (rawContent.length === 0) {
                // Keep the HTML tag alive for script stability, but hide it visually
                consoleOutputCard.style.setProperty("display", "none", "important");
            } else {
                // Instantly unhide the box container when response text exists
                consoleOutputCard.style.removeProperty("display");
            }
        }
    }

    // Execute the empty state scan immediately on page load
    evaluateEmptyState();

    // --- 3. DYNAMIC INTERACTIVE PROMPT TRANSMISSION ---
    function sendMessage() {
        if (!userInput || !sendBtn) return;
        
        const textValue = userInput.value.trim();
        if (!textValue) return;

        // Pull the secure generated key and the verified URL endpoint out of the page DOM layout
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrftoken = csrfInput ? csrfInput.value : "";
        
        const endpointInput = document.getElementById("aurora-chat-endpoint");
        const fetchUrl = endpointInput ? endpointInput.value : "/chat_api/";

        // Visual Pending State Trigger
        sendBtn.disabled = true;
        sendBtn.textContent = "...";

        // Create form payload matching your Django POST view requirements
        const formData = new FormData();
        formData.append("text", textValue);

        // Uses the bulletproof dynamic path calculated by Django
        fetch(fetchUrl, { 
            method: "POST",
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

            // Reveal the master container card immediately before rendering text strings
            if (consoleOutputCard) {
                consoleOutputCard.style.removeProperty("display");
            }

            // Append response text to code output tags
            if (responseOutput) {
                responseOutput.innerHTML = data.reply;
            }

            // Sync structural dashboard gauge counters with live API rate header parameters
            updateSystemGauges(data.tokens_left, data.token_ceiling, data.active_model);

            // Clear layout input container prompt variables
            userInput.value = "";
            userInput.style.height = "auto";
        })
        .catch(err => {
            console.error("Critical Stream Anomaly Captured:", err);
            alert("Connection interrupted. Systems attempting automated link refresh.");
        })
        .finally(() => {
            // Restore visual layout control interaction status loops
            sendBtn.disabled = false;
            sendBtn.innerHTML = "SEND";
        });
    }

    // --- 4. REAL-TIME SYSTEM GAUGES SYNC ---
    function updateSystemGauges(tokensLeft, tokenCeiling, activeModel) {
        const tokenGauge = document.getElementById("token-gauge");
        const tokenDisplay = document.getElementById("token-count-display");
        const activeBrain = document.getElementById("active-brain");

        if (activeBrain && activeModel) {
            activeBrain.textContent = activeModel;
        }

        if (tokensLeft !== undefined && tokenCeiling !== undefined) {
            if (tokenDisplay) {
                tokenDisplay.textContent = `${Number(tokensLeft).toLocaleString()} / ${Number(tokenCeiling).toLocaleString()}`;
            }

            if (tokenGauge) {
                // Calculate dynamic gauge scale percentage
                const percentage = Math.max(0, Math.min(100, (tokensLeft / tokenCeiling) * 100));
                tokenGauge.style.width = `${percentage}%`;

                // Adapt gauge warning colors based on resource levels
                if (percentage < 25) {
                    tokenGauge.className = "progress-bar bg-danger";
                } else if (percentage < 60) {
                    tokenGauge.className = "progress-bar bg-warning";
                } else {
                    tokenGauge.className = "progress-bar bg-info";
                }
            }
        }
    }

    // --- 5. CLIPBOARD MANAGEMENT LAYER ---
    if (copyButton && responseOutput) {
        copyButton.addEventListener("click", function () {
            const cleanCodeString = responseOutput.textContent;
            navigator.clipboard.writeText(cleanCodeString)
                .then(() => {
                    const originalText = copyButton.textContent;
                    copyButton.textContent = "Copied!";
                    copyButton.classList.replace("btn-secondary", "btn-success");
                    
                    setTimeout(() => {
                        copyButton.textContent = originalText;
                        copyButton.classList.replace("btn-success", "btn-secondary");
                    }, 2000);
                })
                .catch(err => console.error("Clipboard permission query denied:", err));
        });
    }

    // --- 6. EVENT INTERFACE WRAPPERS ---
    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
    }

    if (userInput) {
        // Submit on Enter keypress unless holding the Shift key modifier down
        userInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Dynamic auto-expansion tracking height variables logic adjustments
        userInput.addEventListener("input", function () {
            this.style.height = "auto";
            this.style.height = (this.scrollHeight) + "px";
        });
    }
});

// --- 7. EXTERNAL GLOBAL LOG CALLS ---
window.logManualTime = function() {
    const hours = document.getElementById("manual-hours")?.value;
    const note = document.getElementById("manual-note")?.value;
    
    if (!hours || !note) {
        alert("Log entry inputs incomplete.");
        return;
    }
    
    console.log(`[MANUAL LOG REGISTERED] Tracked hours: ${hours} | Task: ${note}`);
    alert(`Documented ${hours} hours successfully.`);
    
    // Clear log form input fields after processing
    if (document.getElementById("manual-hours")) document.getElementById("manual-hours").value = "";
    if (document.getElementById("manual-note")) document.getElementById("manual-note").value = "";
};
