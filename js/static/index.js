const maxInputLength = 200;
const textArea = document.querySelector("textarea");
const charCount = document.getElementById("charCounter");
const chatBody = document.getElementById("chatBody");
const submitButton = document.getElementById("submitButton");
const clearChatButton = document.getElementById("clearChat");

// --- Utility Functions ---

function scrollToBottom() {
    chatBody.scrollTop = chatBody.scrollHeight;
}

function createMessageHTML(msg) {
    return `<div class="flex items-start space-x-2">
                <svg class="w-4 h-4 text-red-800" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 2a8 8 0 108 8 8.01 8.01 0 00-8-8zm1 12H9v-2h2zm0-4H9V6h2z"/>
                </svg>
                <div class="bg-gray-800/70 px-4 py-2 rounded-xl rounded-tl-none shadow max-w-[75%] border border-gray-700">
                    ${msg}
                </div>
            </div>`;
}

function generateId(msg) {
    return btoa(unescape(encodeURIComponent(msg))).slice(0, 30); // simple hash
}

function addMessage(msg) {
    const msgId = generateId(msg);
    const saved = JSON.parse(localStorage.getItem("chatMessages") || "[]");

    if (!saved.find(item => item.id === msgId)) {
        saved.push({id: msgId, msg});
        localStorage.setItem("chatMessages", JSON.stringify(saved));
        chatBody.innerHTML += createMessageHTML(msg);
        scrollToBottom();
    }
}

// --- WebSocket Setup ---

const socket = new WebSocket("ws://192.168.1.100:8080");

socket.addEventListener("message", (event) => {
    const msg = event.data;
    addMessage(msg);
    addMessage("You have been Connected.")
});

// --- DOMContentLoaded ---

window.addEventListener("DOMContentLoaded", () => {
    const saved = JSON.parse(localStorage.getItem("chatMessages") || "[]");
    saved.forEach(({msg}) => {
        chatBody.innerHTML += createMessageHTML(msg);
    });
    resetInactivityTimer();
    scrollToBottom();
});

// --- Input Handler ---

textArea.addEventListener("input", () => {
    const prohibitedWords = ["<script>", "</script>", "alert", "console.log"];

    if (textArea.value.length <= maxInputLength) {
        charCount.textContent = maxInputLength - textArea.value.length;
        submitButton.disabled = false;
    }

    if (textArea.value.length >= maxInputLength) {
        charCount.textContent = "Maximum reached";
        submitButton.disabled = true;
    }

    prohibitedWords.forEach((badWord) => {
        if (textArea.value.includes(badWord)) {
            textArea.value = textArea.value.replace(badWord, "");
            charCount.textContent = "Prohibited word removed";
            setTimeout(() => {
                charCount.textContent = maxInputLength - textArea.value.length;
            }, 2000);
        }
    });
});

// --- Submit Chat ---

document.querySelector("form").addEventListener("submit", (e) => e.preventDefault());

submitButton.addEventListener("click", () => {
    const message = textArea.value.trim();
    if (!message) {
        charCount.textContent = "You can't send an empty message";
        setTimeout(() => {
            charCount.textContent = maxInputLength;
        }, 2000);
        return;
    }

    addMessage(message);
    socket.send(message);
    textArea.value = "";
    charCount.textContent = maxInputLength;
});

// --- Clear Chat ---

function clearChat() {
    localStorage.removeItem("chatMessages");
    chatBody.innerHTML = "";
}

clearChatButton.addEventListener("click", clearChat);

// --- Eye Blink Animation ---

function blinkEyes() {
    const eyes = document.querySelectorAll('.eye');
    eyes.forEach((eye) => {
        eye.style.animation = 'blink-eye 0.5s ease-in-out';
    });
    setTimeout(() => {
        eyes.forEach((eye) => {
            eye.style.animation = '';
        });
    }, 3000);
}

setInterval(blinkEyes, 30000);

// --- Pupil Follower ---

document.addEventListener('mousemove', (event) => {
    const eyes = document.querySelectorAll('.eye');
    eyes.forEach((eye) => {
        const rect = eye.getBoundingClientRect();
        const eyeCenterX = rect.left + rect.width / 2;
        const eyeCenterY = rect.top + rect.height / 2;

        const dx = event.clientX - eyeCenterX;
        const dy = event.clientY - eyeCenterY;
        const angle = Math.atan2(dy, dx);

        // Calculate maximum distance based on the size of the eye
        const maxX = (rect.width / 2) - 25; // Adjusted for pupil size
        const maxY = (rect.height / 2) - 25;

        // Calculate movement within boundaries
        const x = Math.cos(angle) * Math.min(Math.abs(dx), maxX);
        const y = Math.sin(angle) * Math.min(Math.abs(dy), maxY);

        const pupil = eye.querySelector('.pupil');
        pupil.style.transform = `translate(${x}px, ${y}px)`;
    });

    // Reset inactivity timer
    resetInactivityTimer();
});

// --- Inactivity Timer ---

let inactivityTimer;

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
        document.querySelectorAll('.eye .pupil').forEach(pupil => {
            pupil.style.transform = 'translate(0, 0)';
        });
    }, 10000);
}

// --- Auto-Clear Every 12 Hours ---

setInterval(clearChat, 1000 * 60 * 60 * 12);
