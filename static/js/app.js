const shareButton = document.getElementById("shareButton");
const startButton = document.getElementById("startButton");
const stopButton = document.getElementById("stopButton");
const targetLanguageSelect = document.getElementById("targetLanguage");
const statusText = document.getElementById("statusText");
const feed = document.getElementById("feed");

let websocket;
let captureStream;
let captureInterval;
let videoElement;
let canvasElement;
let targetLanguage = targetLanguageSelect.value;

function updateStatus(message) {
    statusText.textContent = message;
}

function createMessageCard(message) {
    const card = document.createElement("article");
    card.classList.add("message-card");

    card.innerHTML = `
        <div class="label">Detected Language: ${message.detected_language}</div>
        <h3>Original Text</h3>
        <div class="text-block">${escapeHtml(message.original_text)}</div>
        <p><strong>Original Romanised</strong></p>
        <div class="text-block">${escapeHtml(message.original_romanized)}</div>
        <p><strong>Target Language Romanised (${escapeHtml(message.target_language)})</strong></p>
        <div class="text-block">${escapeHtml(message.target_translation_romanized)}</div>
        <p><strong>English Translation</strong></p>
        <div class="text-block">${escapeHtml(message.english_translation)}</div>
    `;

    feed.prepend(card);
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function initializeWebSocket() {
    websocket = new WebSocket(`ws://${window.location.host}/ws`);

    websocket.addEventListener("open", () => {
        updateStatus("Connected to translation server.");
    });

    websocket.addEventListener("message", (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "translation") {
            createMessageCard(data.payload);
            updateStatus("Received new translation.");
        } else if (data.type === "status") {
            updateStatus(data.detail);
        } else if (data.type === "error") {
            updateStatus(`Error: ${data.detail}`);
        }
    });

    websocket.addEventListener("close", () => {
        updateStatus("Disconnected from server.");
    });
}

async function shareScreen() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        updateStatus("Screen capture is not supported in this browser.");
        return;
    }

    try {
        captureStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        videoElement = document.createElement("video");
        videoElement.srcObject = captureStream;
        videoElement.muted = true;
        videoElement.playsInline = true;
        await videoElement.play();

        canvasElement = document.createElement("canvas");
        startButton.disabled = false;
        shareButton.disabled = true;
        updateStatus("Chat window shared. Click Start Translation.");

        captureStream.getTracks().forEach((track) => {
            track.onended = () => {
                stopCapture();
                shareButton.disabled = false;
                updateStatus("Screen share ended.");
            };
        });
    } catch (error) {
        updateStatus(`Permission denied: ${error.message}`);
    }
}

function startCapture() {
    if (!captureStream) {
        updateStatus("Please click 'Share Chat Window' before starting translation.");
        return;
    }

    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        initializeWebSocket();
    }

    if (!captureInterval) {
        captureInterval = setInterval(captureFrame, 2000);
        updateStatus("Capturing chat screen every 2 seconds.");
    }

    startButton.disabled = true;
    stopButton.disabled = false;
}

function stopCapture() {
    if (captureInterval) {
        clearInterval(captureInterval);
        captureInterval = null;
    }
    if (captureStream) {
        captureStream.getTracks().forEach((track) => track.stop());
        captureStream = null;
    }
    startButton.disabled = false;
    stopButton.disabled = true;
    shareButton.disabled = false;
    updateStatus("Capture stopped.");
}

function captureFrame() {
    if (!videoElement || !canvasElement || !websocket || websocket.readyState !== WebSocket.OPEN) {
        return;
    }

    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    const context = canvasElement.getContext("2d");
    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

    const imageData = canvasElement.toDataURL("image/png");
    websocket.send(JSON.stringify({
        type: "screenshot",
        target_language: targetLanguage,
        image_data: imageData,
    }));
    updateStatus("Screenshot sent for translation.");
}

shareButton.addEventListener("click", () => {
    shareScreen();
});

startButton.addEventListener("click", () => {
    startCapture();
});

stopButton.addEventListener("click", () => {
    stopCapture();
});

targetLanguageSelect.addEventListener("change", (event) => {
    targetLanguage = event.target.value;
    updateStatus(`Target language set to ${targetLanguage}.`);
});

window.addEventListener("beforeunload", () => {
    if (captureInterval) {
        clearInterval(captureInterval);
    }
    if (captureStream) {
        captureStream.getTracks().forEach((track) => track.stop());
    }
    if (websocket) {
        websocket.close();
    }
});
