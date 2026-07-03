document.addEventListener("DOMContentLoaded", () => {
    // Mermaid configuration for dark theme and high quality
    mermaid.initialize({ 
        startOnLoad: false, 
        theme: 'dark',
        securityLevel: 'loose',
        flowchart: { htmlLabels: true, curve: 'basis' }
    });

    let panZoomInstance = null;

    // UI Elements
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const uploadStatus = document.getElementById("upload-status");
    
    const canvasEmpty = document.getElementById("canvas-empty");
    const canvasContent = document.getElementById("canvas-content");
    const summaryText = document.getElementById("summary-text");
    const flowchartContainer = document.getElementById("flowchart-container");
    const flowchartWrapper = document.getElementById("flowchart-wrapper");
    
    const chatWindow = document.getElementById("chat-window");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");

    // Diagram Controls
    document.getElementById("zoom-in").addEventListener("click", () => panZoomInstance && panZoomInstance.zoomIn());
    document.getElementById("zoom-out").addEventListener("click", () => panZoomInstance && panZoomInstance.zoomOut());
    document.getElementById("zoom-reset").addEventListener("click", () => panZoomInstance && panZoomInstance.resetZoom());

    // File Upload Logic
    dropZone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length) handleFileUpload(e.target.files[0]);
    });

    dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
    dropZone.addEventListener("dragleave", () => { dropZone.classList.remove("dragover"); });
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
    });

    async function handleFileUpload(file) {
        if (file.type !== "application/pdf") {
            appendMessage("Please upload a valid PDF file.", "bot");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        uploadStatus.classList.remove("hidden");
        appendMessage(`Analyzing ${file.name}... This may take a minute for detailed analysis.`, "bot");

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });
            const data = await response.json();
            
            if (response.ok && data.status === "success") {
                appendMessage("Analysis complete! Check the main canvas.", "bot");
                renderSummary(data.summary);
            } else {
                appendMessage("Error processing document: " + (data.detail || "Unknown error"), "bot");
            }
        } catch (err) {
            console.error(err);
            appendMessage("Failed to upload document. Is the server running?", "bot");
        } finally {
            uploadStatus.classList.add("hidden");
            fileInput.value = "";
        }
    }

    async function renderSummary(fullText) {
        // Extract Mermaid block
        const mermaidMatch = fullText.match(/```mermaid\s*([\s\S]*?)```/i);
        let mermaidCode = "";
        let markdownOnly = fullText;

        if (mermaidMatch) {
            mermaidCode = mermaidMatch[1].trim();
            markdownOnly = fullText.replace(mermaidMatch[0], "");
        }

        // Show canvas
        canvasEmpty.classList.add("hidden");
        canvasContent.classList.remove("hidden");

        // Render Markdown using marked.js
        summaryText.innerHTML = marked.parse(markdownOnly);

        // Render Flowchart
        if (mermaidCode) {
            try {
                // Destroy old panZoom if exists
                if (panZoomInstance) {
                    panZoomInstance.destroy();
                    panZoomInstance = null;
                }
                
                // Reset container
                flowchartContainer.removeAttribute('data-processed');
                flowchartContainer.innerHTML = mermaidCode;
                
                // Render with mermaid
                await mermaid.run({
                    nodes: [flowchartContainer]
                });

                // Wait a tick for SVG to be injected
                setTimeout(() => {
                    const svgElement = flowchartContainer.querySelector("svg");
                    if (svgElement) {
                        svgElement.style.width = "100%";
                        svgElement.style.height = "100%";
                        svgElement.style.maxWidth = "none";
                        
                        // Initialize pan-zoom
                        panZoomInstance = svgPanZoom(svgElement, {
                            zoomEnabled: true,
                            controlIconsEnabled: false,
                            fit: true,
                            center: true,
                            minZoom: 0.5,
                            maxZoom: 10
                        });
                    }
                }, 100);

            } catch (err) {
                console.error("Mermaid syntax error:", err);
                flowchartContainer.innerHTML = `<p style='color: var(--text-secondary); text-align: center;'><em>Flowchart rendering failed. The model produced invalid syntax.</em></p><pre style='color: var(--text-secondary); padding: 1rem; overflow: auto; text-align: left;'>${mermaidCode}</pre>`;
            }
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
        const loadingId = appendLoading();

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            
            removeLoading(loadingId);
            
            if (response.ok && data.reply) {
                appendMessage(data.reply, "bot");
            } else {
                appendMessage("Error: " + (data.detail || "Server error occurred. Check API Key."), "bot");
            }
        } catch (err) {
            removeLoading(loadingId);
            appendMessage("Sorry, I encountered a connection error.", "bot");
        }
    }

    function appendMessage(text, sender) {
        const div = document.createElement("div");
        div.className = `message ${sender}-message`;
        
        // Parse markdown if bot message, else plain text
        const contentHtml = sender === "bot" ? marked.parse(text) : `<p>${text}</p>`;
        
        div.innerHTML = `<div class="msg-content">${contentHtml}</div>`;
        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function appendLoading() {
        const id = 'loading-' + Date.now();
        const div = document.createElement("div");
        div.className = "message bot-message";
        div.id = id;
        div.innerHTML = `<div class="msg-content">...</div>`;
        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return id;
    }

    function removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
