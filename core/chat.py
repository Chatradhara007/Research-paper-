from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from core.processor import get_llm
from core.vector_db import load_index

# Global chat history so conversation persists across requests
chat_history = InMemoryChatMessageHistory()

def chat_with_memory(user_query: str) -> str:
    """
    Handle user query. If index exists, use RAG.
    Otherwise, respond as a normal conversational AI using memory.
    """
    llm = get_llm()
    vectorstore = load_index()
    
    if vectorstore:
        # Memory configured specifically for ConversationalRetrievalChain
        memory = ConversationBufferMemory(
            chat_memory=chat_history,
            memory_key="chat_history", 
            return_messages=True,
            output_key="answer"
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=False
        )
        response = chain.invoke({"question": user_query})
        return response["answer"]
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
