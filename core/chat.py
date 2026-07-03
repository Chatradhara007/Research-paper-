from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from core.processor import get_llm
from core.vector_db import load_index

# Global memory instance so conversation persists across requests
memory = ConversationBufferMemory(
    memory_key="chat_history", 
    return_messages=True,
    output_key="answer"
)

def chat_with_memory(user_query: str) -> str:
    """
    Handle user query. If index exists, use RAG.
    Otherwise, respond as a normal conversational AI using memory.
    """
    llm = get_llm()
    vectorstore = load_index()
    
    if vectorstore:
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
        from langchain.chains import ConversationChain
        
        # We create a simple ConversationChain if no document is uploaded yet
        conversation = ConversationChain(
            llm=llm,
            memory=memory
        )
        response = conversation.invoke(input=user_query)
        return response["response"]
