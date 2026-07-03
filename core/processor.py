from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    # Use an available Groq model or fallback to a default if user hasn't set it up
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
    Given the document chunks, generate a summary and a Mermaid.js flowchart 
    representing the paper's methodology or structure.
    """
    llm = get_llm()
    
    # We only take the first few chunks to generate a high-level summary to save tokens.
    text_content = "\n\n".join([chunk.page_content for chunk in chunks[:5]])
    
    prompt = f"""
    You are an expert AI Research Assistant. Analyze the following excerpts from a research paper and provide:
    1. A detailed summary (3-4 paragraphs) highlighting the objectives, methodology, and key findings.
    2. A Mermaid.js flowchart (graph TD) that illustrates the flow of the research methodology or system architecture.
    
    Paper Excerpts:
    {text_content}
    
    Output Format STRICTLY:
    ### Summary
    [Your summary here]
    
    ### Flowchart
    ```mermaid
    [Your mermaid code here]
    ```
    """
    
    response = llm.invoke(prompt)
    return response.content
