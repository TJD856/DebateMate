const chatForm = document.getElementById("chat-form");
const messages = document.getElementById("messages");

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const queryInput = document.getElementById("query");
    const query = queryInput.value;

    // Add user query to the chatbox
    const userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.textContent = query;
    messages.appendChild(userMessage);

    // Clear input field
    queryInput.value = "";

    // Fetch response from the server
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();
        const botMessage = document.createElement("div");
        botMessage.classList.add("message", "bot");
        botMessage.textContent = data.response || "Sorry, I couldn't understand that.";
        messages.appendChild(botMessage);

        // Auto-scroll to the latest message
        messages.scrollTop = messages.scrollHeight;
    } catch (error) {
        console.error("Error fetching response:", error);
    }
});
