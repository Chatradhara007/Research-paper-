from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("Please provide a valid GROQ_API_KEY in your .env file")
    
    return ChatGroq(
        api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.2
    )

def generate_summary_and_flowchart(chunks):
    """
    Generate a highly detailed summary and an intricate Mermaid.js flowchart 
    representing the paper's core methodology, architecture, and experiments.
    """
    llm = get_llm()
    
    # Take a much larger slice of the document (e.g., first 20 chunks) 
    # Llama 3 70B can handle 8k context, 20 chunks * 1000 chars is ~20k chars (~5k tokens)
    max_chunks = min(len(chunks), 20)
    text_content = "\n\n".join([chunk.page_content for chunk in chunks[:max_chunks]])
    
    prompt = f"""
    You are an expert AI Research Scientist. Analyze the following excerpts from a research paper.
    
    Output a highly detailed response in two parts:
    
    1. A "Core Breakdown" using RICH BULLET POINTS. Each bullet must be 2-3 detailed sentences. DO NOT just write one short sentence. Provide deep clarity and thorough explanations. Structure:
       - 🎯 Core Objective (What problem are they solving and why is it complex?)
       - 🔬 Methodology (Detailed step-by-step of how they did it)
       - 📊 Key Findings (Specific results, metrics, and outcomes)
       - 💡 Implications (Broader impact on the field)
       
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
