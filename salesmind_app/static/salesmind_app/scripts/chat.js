const chatContainer = document.getElementById("chatContainer");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// Get CSRF token from meta tag
const csrftoken = document.querySelector('[name=csrf-token]').content;

function appendMessage(text, sender) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = text;
  msgDiv.appendChild(bubble);
  chatContainer.appendChild(msgDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
  const text = userInput.value.trim();
  if (text === "") return;

  appendMessage(text, "user");
  userInput.value = "";

  const thinkingDiv = document.createElement("div");
  thinkingDiv.classList.add("message", "bot");
  const thinkingBubble = document.createElement("div");
  thinkingBubble.classList.add("bubble");
  thinkingBubble.textContent = "Thinking...";
  thinkingDiv.appendChild(thinkingBubble);
  chatContainer.appendChild(thinkingDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  try {
    const response = await fetch("/chat_query/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,  // ✅ Include CSRF token here
      },
      body: JSON.stringify({ message: text }),
    });

    const data = await response.json();

    if (data.response) {
      thinkingBubble.textContent = data.response;
    } else if (data.error) {
      thinkingBubble.textContent = "Error: " + data.error;
    } else {
      thinkingBubble.textContent = "Unexpected server response.";
    }
  } catch (error) {
    thinkingBubble.textContent = "Request failed: " + error.message;
  }

  chatContainer.scrollTop = chatContainer.scrollHeight;
}

const uploadSuccessModal = document.getElementById("uploadSuccessModal");
const successModalBody = document.getElementById("successModalBody");
const closeSuccessModal = document.getElementById("closeSuccessModal");
const okBtn = document.getElementById("okBtn");

function showSuccessModal(message) {
  successModalBody.textContent = message;
  uploadSuccessModal.style.display = "flex";
}

function hideSuccessModal() {
  uploadSuccessModal.style.display = "none";
}

closeSuccessModal.addEventListener("click", hideSuccessModal);
okBtn.addEventListener("click", hideSuccessModal);

// Update your file upload handler:
chatFileInput.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/upload-transcript/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
      },
      body: formData,
    });

    const data = await response.json();

    if (data.message) {
      showSuccessModal(`${data.message}`); // Show modal instead of chat
    } else if (data.error) {
      showSuccessModal(`Error: ${data.error}`);
    }
  } catch (error) {
    showSuccessModal(`Upload failed: ${error.message}`);
  }

  chatFileInput.value = "";
});

