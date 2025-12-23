// Modal Elements
const modal = document.getElementById("transcriptModal");
const openBtn = document.getElementById("openTranscriptModal");
const closeBtn = document.getElementById("closeModal");
const cancelBtn = document.getElementById("cancelBtn");
const uploadBtn = document.getElementById("uploadBtn");
const uploadBox = document.getElementById("uploadBox");
const fileInput = document.getElementById("fileInput");

// --- New Elements for UI Feedback ---
let fileNameDisplay = document.createElement("p");
fileNameDisplay.classList.add("file-name-display");
uploadBox.appendChild(fileNameDisplay);

let progressContainer = document.createElement("div");
progressContainer.classList.add("progress-container");
progressContainer.innerHTML = `<div class="progress-bar" id="uploadProgress"></div>`;
uploadBox.appendChild(progressContainer);
const progressBar = document.getElementById("uploadProgress");

// --- Modal Handling ---
openBtn.addEventListener("click", (e) => {
  e.preventDefault();
  modal.style.display = "flex";
});

closeBtn.addEventListener("click", () => closeModal());
cancelBtn.addEventListener("click", () => closeModal());
modal.addEventListener("click", (e) => {
  if (e.target === modal) closeModal();
});

function closeModal() {
  modal.style.display = "none";
  fileInput.value = "";
  fileNameDisplay.textContent = "";
  progressBar.style.width = "0%";
}

// --- Drag & Drop ---
uploadBox.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadBox.style.background = "#eef1fb";
});

uploadBox.addEventListener("dragleave", () => {
  uploadBox.style.background = "#fff";
});

uploadBox.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadBox.style.background = "#fff";
  fileInput.files = e.dataTransfer.files;
  showFileName(fileInput.files[0]);
});

fileInput.addEventListener("change", (e) => {
  if (e.target.files.length) {
    showFileName(e.target.files[0]);
  }
});

// --- Display Selected File Name ---
function showFileName(file) {
  fileNameDisplay.textContent = `Selected file: ${file.name}`;
}

// --- Handle Upload ---
uploadBtn.addEventListener("click", () => {
  if (!fileInput.files.length) {
    alert("Please select a file first!");
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/upload-transcript/");

  xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));

  // --- Progress Event ---
  xhr.upload.addEventListener("progress", (event) => {
    if (event.lengthComputable) {
      const percentComplete = (event.loaded / event.total) * 100;
      progressBar.style.width = percentComplete + "%";
    }
  });


  xhr.onload = function () {
    if (xhr.status === 200) {
      const data = JSON.parse(xhr.responseText);
      alert(data.message || "Upload successful!");
    } else {
      alert("Upload failed: " + xhr.statusText);
    }
    closeModal();
  };

  xhr.onerror = function () {
    alert("An error occurred while uploading the file.");
    closeModal();
  };

  xhr.send(formData);
});

// --- Helper to get CSRF token from cookies ---
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
