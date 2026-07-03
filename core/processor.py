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
    You are an expert AI Research Scientist focused on CLARITY. I will provide you with excerpts from a research paper.
    
    Your task is to analyze the text and output a response in two parts:
    
    1. A "Core Breakdown". DO NOT output walls of text. Use short, punchy bullet points and bold text to make it extremely easy to read at a glance. Break it strictly into these sections:
       - 🎯 Core Objective (What problem are they solving?)
       - 🔬 Methodology (How did they do it?)
       - 📊 Key Findings (What were the results?)
       - 💡 Implications (Why does this matter?)
       
    2. A HIGHLY DETAILED and COLORFUL Mermaid.js flowchart (`graph TD` or `graph LR`) illustrating the methodology, architecture, or experimental pipeline. 
       
    MERMAID INSTRUCTIONS:
    - Make the diagram comprehensive, showing logical flow from start to finish.
    - KEEP NODE LABELS CLEAN: DO NOT use quotes, parentheses, brackets, or any special characters inside node text.
    - ADD COLORS: You MUST use `classDef` to color code different types of nodes (e.g., inputs, processes, models, outputs). Make it visually stunning.
    - Example of valid colorful syntax:
      ```mermaid
      graph TD
      classDef input fill:#10b981,color:#fff,stroke:#047857,stroke-width:2px;
      classDef model fill:#8b5cf6,color:#fff,stroke:#6d28d9,stroke-width:2px;
      classDef output fill:#f59e0b,color:#fff,stroke:#b45309,stroke-width:2px;
      
      A[Raw Dataset]:::input --> B[Neural Network]:::model
      B --> C[Predictions]:::output
      ```
    
    Paper Excerpts:
    {text_content}
    
    Output Format STRICTLY:
    ### Core Breakdown
    [Your bulleted breakdown here]
    
    ### Flowchart
    ```mermaid
    [Your detailed colorful mermaid code here]
    ```
    """
    
    response = llm.invoke(prompt)
    return response.content
