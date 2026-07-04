from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def get_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("Please provide a valid GEMINI_API_KEY in your .env file")
    
    # Using gemini-1.5-flash as it is globally available and has a massive context window for complex instructions
    return ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model="gemini-1.5-flash",
        temperature=0.2
    )

def generate_summary_and_flowchart(chunks):
    """
    Generate a highly detailed summary and an intricate Mermaid.js flowchart 
    representing the paper's core methodology, architecture, and experiments.
    """
    llm = get_llm()
    
    # Take a much larger slice of the document
    max_chunks = min(len(chunks), 20)
    text_content = "\n\n".join([chunk.page_content for chunk in chunks[:max_chunks]])
    
    prompt = f"""
    You are an expert AI Research Scientist. Analyze the following excerpts from a research paper.
    
    Output a highly detailed response in two parts:
    
    1. A "Core Breakdown" using BITE-SIZED BULLET POINTS. 
       - NEVER write paragraphs or massive blocks of text.
       - Use 1-2 punchy sentences per point. 
       - Use sub-bullets to break up complex information into scannable lists.
       - Make it feel like a premium, highly readable executive summary.
       Structure strictly into:
       - 🎯 Core Objective (What problem are they solving?)
       - 🔬 Methodology (2-3 short sub-bullets explaining the steps)
       - 📊 Key Findings (2-3 short sub-bullets highlighting results)
       - 💡 Implications (Why does it matter?)
       
    2. A GALLERY OF FLOWCHARTS. Generate at least 5 to 8 HIGHLY DETAILED and COLORFUL Mermaid.js flowcharts (`graph TD` or `graph LR`) covering different aspects of the paper. Choose from:
       - Research Methodology
       - System Architecture
       - Data Preprocessing Pipeline
       - Model Architecture
       - Training / Inference Pipeline
       - Evaluation Metrics Workflow
       - Citation / Knowledge Graph
       
    MERMAID INSTRUCTIONS:
    - KEEP NODE LABELS CLEAN: DO NOT use quotes, parentheses, brackets, or any special characters inside node text.
    - ADD COLORS: Use `classDef` to color code nodes to make it visually stunning.
    
    TAGGING INSTRUCTIONS:
    You MUST wrap each flowchart inside `<diagram title="Your Title Here"> ... </diagram>` tags so the frontend can parse them into tabs.
    Example:
    <diagram title="Data Preprocessing Pipeline">
    ```mermaid
    graph TD
    classDef step fill:#3b82f6,color:#fff;
    A[Raw Data]:::step --> B[Cleaning]:::step
    ```
    </diagram>
    
    CRITICAL INSTRUCTION: Do NOT repeat the instructions back to me. Do NOT generate infinite loops of text. Provide the output and stop immediately.
    
    Paper Excerpts:
    {text_content}
    
    Output Format STRICTLY:
    ### Core Breakdown
    [Your rich bullet points here]
    
    ### Flowcharts
    [Your 5-8 tagged diagrams here]
    """
    
    response = llm.invoke(prompt)
    return response.content
