document.addEventListener("DOMContentLoaded", function () {
    console.log("📡 [FRONTEND] Initializing High-Density Aurora UI event matrix bindings...");

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

        // Pull security keys and verified URL anchors safely from the DOM layout
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrftoken = csrfInput ? csrfInput.value : "";
        const endpointInput = document.getElementById("aurora-chat-endpoint");
        
        // FIXED FALLBACK PATHWAY MATRIX: Maps directly to your true app namespace root
        const fetchUrl = endpointInput ? endpointInput.value : "/aurora/api/";

        // Visual Pending State Trigger
        sendBtn.disabled = true;
        sendBtn.textContent = "...";

        const formData = new FormData();
        formData.append("text", textValue);

        // Dispatches payload straight to your running views logic core
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
            if (consoleOutputCard) {
                consoleOutputCard.style.removeProperty("display");
            }
            if (responseOutput) {
                responseOutput.innerHTML = data.reply || "";
                evaluateEmptyState();
            }
            updateSystemGauges(data.tokens_left, data.token_ceiling, data.active_model);
            userInput.value = "";
            userInput.style.height = "auto";
        })
        .catch(err => {
            console.error("Critical Stream Anomaly Captured:", err);
            alert("Connection interrupted. Systems attempting automated link refresh.");
        })
        .finally(() => {
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
                const percentage = Math.max(0, Math.min(100, (tokensLeft / tokenCeiling) * 100));
                tokenGauge.style.width = `${percentage}%`;
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
        userInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        userInput.addEventListener("input", function () {
            this.style.height = "auto";
            this.style.height = (this.scrollHeight) + "px";
        });
    }
}); // FIXED: Cleanly terminates the DOMContentLoaded master file wrapper scope

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
    if (document.getElementById("manual-hours")) document.getElementById("manual-hours").value = "";
    if (document.getElementById("manual-note")) document.getElementById("manual-note").value = "";
};
