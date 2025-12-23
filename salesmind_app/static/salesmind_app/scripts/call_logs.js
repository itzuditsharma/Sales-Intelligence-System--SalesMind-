// static/salesmind_app/scripts/call_logs.js

// 1. Read the embedded JSON data
const dataScript = document.getElementById("call-logs-data");
// 1. Check if the element was found
if (!dataScript) {
    console.error("DEBUG: Element with ID 'call-logs-data' not found in the DOM.");
    // Stop execution if element is missing
}

// Use a try-catch block for safe parsing, especially important if the JSON might be empty or malformed.
let callLogs = [];
try {
    // Check if the script tag exists and has content
    if (dataScript && dataScript.textContent.trim()) {
        callLogs = JSON.parse(dataScript.textContent);
        console.log("DEBUG: Parsed Log Count:", callLogs.length); // CHECK 4
    }
} catch (e) {
    console.error("Error parsing call log data from embedded JSON:", e);
    // Keep callLogs as an empty array if parsing fails
}


// 2. Reference the container element
const calllogsBody = document.getElementById("calllogsBody");

// 3. Render function
function renderCallLogs() {
    // Clear the container before rendering (useful if you ever re-render/filter)
    calllogsBody.innerHTML = '';

    if (callLogs.length === 0) {
        calllogsBody.innerHTML = '<div style="text-align: center; padding: 20px; color: #666;">No call logs found.</div>';
        return;
    }

    callLogs.forEach((log) => {
        const row = document.createElement("div");
        row.classList.add("calllog-row"); // Use a class for CSS styling

        // Important: Ensure the keys (log.id, log.customer, etc.) match 
        // the keys in the dictionaries passed from your Django view.
        row.innerHTML = `
            <div>${log.id}</div>
            <div>${log.customer}</div>
            <div>${log.team}</div>
            <div>${log.discussion}</div>
        `;

        calllogsBody.appendChild(row);
    });
}

// 4. Initialize on page load
document.addEventListener("DOMContentLoaded", renderCallLogs);