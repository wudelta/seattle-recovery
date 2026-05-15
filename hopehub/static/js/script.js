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
