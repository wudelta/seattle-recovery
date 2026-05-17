// FILE: hopehub/script.js
/*
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:46.557353+00:00
 PROJECT ECOSYSTEM: HOPEHUB
 FILE PATH: hopehub/static/js/script.js
 TECHNICAL MATRIX: Javascript Client Architecture Asset.

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[script.js] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[HOPEHUB]
 ```
*/
// script.js

// Get the input field, send button, and chat log elements
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const chatLog = document.getElementById('chat-log');

// Add an event listener to the send button
sendButton.addEventListener('click', () => {
    // Get the user's input
    const userMessage = userInput.value.trim();

    // Check if the user entered a message
    if (userMessage !== '') {
        // Add the user's message to the chat log
        const userMessageElement = document.createElement('p');
        userMessageElement.textContent = `You: ${userMessage}`;
        chatLog.appendChild(userMessageElement);

        // Clear the input field
        userInput.value = '';

        // Add a response from the "server" (for demo purposes only)
        const serverResponseElement = document.createElement('p');
        serverResponseElement.textContent = `Server: ${userMessage} received!`;
        chatLog.appendChild(serverResponseElement);
    }
});