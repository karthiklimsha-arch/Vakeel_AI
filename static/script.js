let historyData = JSON.parse(localStorage.getItem("chatHistory")) || [];

// 🚀 SEND MESSAGE
function sendMessage() {
    const input = document.getElementById("userInput");
    const messages = document.getElementById("messages");
    const welcome = document.getElementById("welcomeScreen");

    const query = input.value.trim();
    if (!query) return;

    const lang = document.getElementById("language")?.value || "auto"; // ✅ FIX

    if (welcome) welcome.style.display = "none";

    messages.innerHTML += `<div class="user">${query}</div>`;

    const loadingId = "loading-" + Date.now();
    messages.innerHTML += `<div id="${loadingId}" class="bot">Typing...</div>`;

    messages.scrollTop = messages.scrollHeight;

    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            query: query,   // ✅ FIX
            lang: lang      // ✅ FIX
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById(loadingId)?.remove();

        if (!data || !data.response) {
            messages.innerHTML += `<div class="bot">No response</div>`;
            return;
        }

        messages.innerHTML += `
        <div class="bot">
            <b>${data.source || "AI"}</b><br>
            ${data.response}
        </div>`;

        saveToHistory(query, data.response);

        messages.scrollTop = messages.scrollHeight;
    })
    .catch(err => {
        console.error(err);
        document.getElementById(loadingId)?.remove();
        messages.innerHTML += `<div class="bot">Error occurred</div>`;
    });

    input.value = "";
}


// ENTER KEY
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("userInput");

    if (input) {
        input.addEventListener("keypress", function (e) {
            if (e.key === "Enter") sendMessage();
        });
    }

    renderHistory();
});


// NEW CHAT
function newChat() {
    document.getElementById("messages").innerHTML = "";
    document.getElementById("welcomeScreen").style.display = "block";
}


// VOICE INPUT
function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-IN";

    recognition.onresult = function (event) {
        document.getElementById("userInput").value = event.results[0][0].transcript;
    };

    recognition.start();
}


// SAVE HISTORY
function saveToHistory(query, response) {
    const chat = {
        id: Date.now(),
        query,
        response
    };

    historyData.unshift(chat);
    localStorage.setItem("chatHistory", JSON.stringify(historyData));
    renderHistory();
}


// RENDER HISTORY
function renderHistory() {
    const history = document.getElementById("history");
    if (!history) return;

    history.innerHTML = "";

    historyData.forEach(item => {
        history.innerHTML += `
        <div class="history-item">
            <span onclick="loadChat(${item.id})">
                ${item.query.substring(0, 25)}...
            </span>

            <div class="history-actions">
                <span onclick="renameChat(${item.id})">✏️</span>
                <span onclick="deleteChat(${item.id})">🗑️</span>
            </div>
        </div>`;
    });
}


// LOAD CHAT
function loadChat(id) {
    const chat = historyData.find(c => c.id === id);
    if (!chat) return;

    document.getElementById("welcomeScreen").style.display = "none";

    document.getElementById("messages").innerHTML = `
        <div class="user">${chat.query}</div>
        <div class="bot">${chat.response}</div>
    `;
}


// RENAME
function renameChat(id) {
    const newName = prompt("Rename chat:");
    if (!newName) return;

    const chat = historyData.find(c => c.id === id);
    if (chat) {
        chat.query = newName;
        localStorage.setItem("chatHistory", JSON.stringify(historyData));
        renderHistory();
    }
}


// DELETE
function deleteChat(id) {
    historyData = historyData.filter(c => c.id !== id);
    localStorage.setItem("chatHistory", JSON.stringify(historyData));
    renderHistory();
}


// CLEAR
function clearHistory() {
    localStorage.removeItem("chatHistory");
    historyData = [];
    renderHistory();
}