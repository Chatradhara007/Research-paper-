from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from core.processor import get_llm
from core.vector_db import load_index

# Global chat history so conversation persists across requests
chat_history = InMemoryChatMessageHistory()

def set_new_document_context(filename: str):
    """Injects a system prompt into the memory to focus on the new document."""
    system_msg = f"[SYSTEM NOTIFICATION]: I have just uploaded a new document named '{filename}'. From this point forward, please prioritize this new document in your answers. Do not discuss previous documents unless I explicitly ask you to compare them or reference them."
    chat_history.add_user_message(system_msg)
    chat_history.add_ai_message(f"Understood. I will now focus my analysis primarily on '{filename}' while retaining the ability to search older documents if explicitly requested.")

def chat_with_memory(user_query: str) -> str:
    """
    Handle user query. If index exists, use RAG.
    Otherwise, respond as a normal conversational AI using memory.
    """
    llm = get_llm()
    vectorstore = load_index()
    
    if vectorstore:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(user_query)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # We manually construct the prompt to avoid the "condense question" double-LLM-call of ConversationalRetrievalChain
        from langchain_core.prompts import PromptTemplate
        
        prompt = f"""You are a helpful AI assistant analyzing a document.
        
Context from document:
{context}

History:
{chat_history.messages}

User: {user_query}
AI Assistant:"""
        
        response = llm.invoke(prompt)
        chat_history.add_user_message(user_query)
        chat_history.add_ai_message(response.content)
        return response.content
    else:
        # Normal conversation without document context
        from langchain_classic.chains import ConversationChain
        
        # Memory configured specifically for standard ConversationChain
        memory = ConversationBufferMemory(
            chat_memory=chat_history,
            memory_key="history", 
            return_messages=True
        )
        
        conversation = ConversationChain(
            llm=llm,
            memory=memory
        )
        response = conversation.invoke(input=user_query)
        return response["response"]
