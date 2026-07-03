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
    You are an expert AI Research Scientist. I will provide you with extensive excerpts from a research paper.
    
    Your task is to analyze the text and output a highly detailed response in two parts:
    
    1. A detailed Summary (3-5 paragraphs) discussing the objectives, methodologies, architectures, and outcomes.
    2. A HIGHLY DETAILED Mermaid.js flowchart (`graph TD` or `graph LR`) illustrating the entire methodology, 
       model architecture, or experimental pipeline. 
       
    MERMAID INSTRUCTIONS:
    - Make the diagram complex and comprehensive (use subgraphs if appropriate).
    - Ensure logical flow from data ingestion/setup to final evaluation.
    - KEEP NODE LABELS CLEAN: DO NOT use quotes, parentheses, brackets, or any special characters inside node text.
    - Example of valid complex syntax:
      subgraph Data Prep
        A[Raw Data] --> B[Cleaned Data]
      end
      B --> C[Model Training]
    
    Paper Excerpts:
    {text_content}
    
    Output Format STRICTLY:
    ### Summary
    [Your comprehensive summary here]
    
    ### Flowchart
    ```mermaid
    [Your detailed mermaid code here]
    ```
    """
    
    response = llm.invoke(prompt)
    return response.content
