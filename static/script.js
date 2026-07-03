document.addEventListener("DOMContentLoaded", () => {
    // Mermaid initialization
    mermaid.initialize({ startOnLoad: false, theme: 'dark' });

    // UI Elements
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const browseBtn = document.getElementById("browse-btn");
    const uploadStatus = document.getElementById("upload-status");
    const summaryContainer = document.getElementById("summary-container");
    const summaryContent = document.getElementById("summary-content");
    const flowchartContainer = document.getElementById("flowchart-container");
    
    const chatWindow = document.getElementById("chat-window");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");

    // File Upload Logic
    browseBtn.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length) {
            handleFileUpload(e.target.files[0]);
        }
    });

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    async function handleFileUpload(file) {
        if (file.type !== "application/pdf") {
            alert("Please upload a PDF file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        uploadStatus.classList.remove("hidden");
        summaryContainer.classList.add("hidden");

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });
            const data = await response.json();
            
            if (data.status === "success") {
                renderSummary(data.summary);
            } else {
                alert("Error processing document");
            }
        } catch (err) {
            console.error(err);
            alert("Failed to upload document");
        } finally {
            uploadStatus.classList.add("hidden");
        }
    }

    function renderSummary(summaryText) {
        // Simple extraction of markdown and mermaid
        // We look for ```mermaid ... ```
        const mermaidMatch = summaryText.match(/```mermaid([\s\S]*?)```/);
        let mermaidCode = "";
        let textOnly = summaryText;

        if (mermaidMatch) {
            mermaidCode = mermaidMatch[1].trim();
            textOnly = summaryText.replace(mermaidMatch[0], "");
        }

        // Render Text
        // Convert basic markdown to HTML (just handling paragraphs for simplicity, 
        // a real app might use marked.js)
        const paragraphs = textOnly.split('\n\n').filter(p => p.trim());
        summaryContent.innerHTML = paragraphs.map(p => {
            if(p.startsWith('###')) return `<h3>${p.replace('###', '').trim()}</h3>`;
            if(p.startsWith('##')) return `<h2>${p.replace('##', '').trim()}</h2>`;
            if(p.startsWith('#')) return `<h1>${p.replace('#', '').trim()}</h1>`;
            return `<p>${p}</p>`;
        }).join('');

        summaryContainer.classList.remove("hidden");

        // Render Flowchart
        if (mermaidCode) {
            flowchartContainer.innerHTML = mermaidCode;
            flowchartContainer.removeAttribute('data-processed');
            mermaid.init(undefined, flowchartContainer);
        }
    }

    // Chat Logic
    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        appendMessage(text, "user");
        chatInput.value = "";
        
        // Show loading indicator
        const loadingDiv = document.createElement("div");
        loadingDiv.className = "message bot-message";
        loadingDiv.textContent = "...";
        chatWindow.appendChild(loadingDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            
            loadingDiv.remove();
            if (response.ok && data.reply) {
                appendMessage(data.reply, "bot");
            } else {
                appendMessage("Error: " + (data.detail || "Unknown server error. Please check your API key."), "bot");
            }
        } catch (err) {
            loadingDiv.remove();
            appendMessage("Sorry, I encountered an error connecting to the server.", "bot");
        }
    }

    function appendMessage(text, sender) {
        const div = document.createElement("div");
        div.className = `message ${sender}-message`;
        div.innerHTML = `<p>${text}</p>`; // Simple rendering, could use marked.js here too
        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});
