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
    
    max_chunks = min(len(chunks), 20)
    text_content = "\n\n".join([chunk.page_content for chunk in chunks[:max_chunks]])
    
    # --- DUAL CALL ARCHITECTURE ---
    # Call 1: Core Breakdown + 4 Diagrams
    prompt1 = f"""
    You are an expert AI Research Scientist. Analyze the excerpts from the research paper.
    
    Output a highly detailed response in two parts:
    
    1. A "Core Breakdown" using BITE-SIZED BULLET POINTS. 
       - NEVER write paragraphs. Use 1-2 punchy sentences per point. 
       Structure strictly into:
       - 🎯 Core Objective
       - 🔬 Methodology 
       - 📊 Key Findings
       - 💡 Implications
       
    2. Generate EXACTLY 4 HIGHLY DETAILED Mermaid.js flowcharts (`graph TD` or `graph LR`). Choose from: System Architecture, Data Preprocessing, Model Architecture, or Training Pipeline.
       
    MERMAID INSTRUCTIONS:
    - KEEP NODE LABELS CLEAN: DO NOT use quotes or special characters inside node text.
    - ADD COLORS: Use `classDef` to color code nodes.
    
    TAGGING INSTRUCTIONS:
    You MUST wrap each flowchart inside `<diagram title="Your Title Here"> ... </diagram>` tags.
    
    CRITICAL INSTRUCTION: Do NOT repeat the instructions back to me. Do NOT loop. Stop after the 4 diagrams.
    
    Paper Excerpts:
    {text_content}
    """
    
    resp1 = llm.invoke(prompt1).content
    
    # Call 2: 4 More Diagrams
    prompt2 = f"""
    You are an expert AI Research Scientist. Analyze the same excerpts.
    
    Your ONLY task is to generate EXACTLY 4 MORE HIGHLY DETAILED Mermaid.js flowcharts. 
    Choose different topics from before, such as: Evaluation Metrics, Citation Graph, Research Methodology, or Inference Pipeline.
    
    MERMAID INSTRUCTIONS:
    - KEEP NODE LABELS CLEAN: DO NOT use quotes or special characters inside node text.
    - ADD COLORS: Use `classDef` to color code nodes.
    
    TAGGING INSTRUCTIONS:
    You MUST wrap each flowchart inside `<diagram title="Your Title Here"> ... </diagram>` tags.
    
    CRITICAL INSTRUCTION: Do NOT repeat the instructions back to me. Do NOT loop. Provide the output and stop immediately.
    
    Paper Excerpts:
    {text_content}
    """
    
    resp2 = llm.invoke(prompt2).content
    
    # Seamlessly stitch them together!
    return resp1 + "\n\n" + resp2
